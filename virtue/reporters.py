from time import time
from traceback import format_exc
import sys

from twisted.python.reflect import fullyQualifiedName as fully_qualified_name


class ComponentizedReporter(object):

    shouldStop = False

    def __init__(
        self, outputter=None, recorder=None, stream=sys.stdout, time=time,
    ):
        if outputter is None:
            outputter = Outputter()
        if recorder is None:
            recorder = Recorder()

        self.outputter = outputter
        self.recorder = recorder
        self.stream = stream
        self._time = time

    def startTestRun(self):
        self._start_time = self._time()
        self.recorder.startTestRun()
        self.stream.writelines(self.outputter.run_started() or "")

    def stopTestRun(self):
        self.recorder.stopTestRun()
        runtime = self._time() - self._start_time
        self.stream.writelines(
            self.outputter.run_stopped(self.recorder, runtime) or ""
        )

    def startTest(self, test):
        self.stream.writelines(self.outputter.test_started(test) or "")

    def stopTest(self, test):
        self.stream.writelines(self.outputter.test_stopped(test) or "")

    def addError(self, test, exc_info):
        self.recorder.addError(test, exc_info)
        self.stream.writelines(
            self.outputter.test_errored(test, exc_info) or ""
        )

    def addFailure(self, test, exc_info):
        self.recorder.addFailure(test, exc_info)
        self.stream.writelines(
            self.outputter.test_failed(test, exc_info) or ""
        )

    def addSkip(self, test, reason):
        self.recorder.addSkip(test, reason)
        self.stream.writelines(self.outputter.test_skipped(test, reason) or "")

    def addSuccess(self, test):
        self.recorder.addSuccess(test)
        self.stream.writelines(self.outputter.test_succeeded(test) or "")

    def wasSuccessful(self):
        return self.recorder.wasSuccessful()


class Outputter(object):

    _last_test_class = None
    _last_test_module = None

    FAILED, PASSED = "FAILED", "PASSED"
    ERROR, FAIL, OK, SKIPPED = "[ERROR]", "[FAIL]", "[OK]", "[SKIPPED]"

    def __init__(self, colored=True, indent=" " * 2, line_width=120):
        self.indent = indent
        self.line_width = line_width

        if colored:
            from colorama import Fore, Style
            message = "{Style.BRIGHT}{color}{text}{Style.RESET_ALL}"
            for attr, color, text in [
                ("_error", Fore.RED, self.ERROR),
                ("_fail", Fore.RED, self.FAIL),
                ("_failed", Fore.RED, self.FAILED),
                ("_ok", Fore.GREEN, self.OK),
                ("_passed", Fore.GREEN, self.PASSED),
                ("_skipped", Fore.BLUE, self.SKIPPED),
            ]:
                setattr(
                    self, attr, message.format(
                        Style=Style, color=color, text=text,
                    )
                )
        else:
            self._error = self.ERROR
            self._failed = self.FAILED
            self._passed = self.PASSED
            self._skipped = self.SKIPPED

        self._after = []

    def run_started(self):
        pass

    def run_stopped(self, recorder, runtime):
        for line in self._after:
            yield line
        yield "\n"
        yield "-" * self.line_width
        yield "\n"
        count = recorder.count
        yield "Ran {count} test{s} in {runtime:.3f}s\n".format(
            count=count, runtime=runtime, s="s" if count != 1 else "",
        )
        yield "\n"
        if recorder.wasSuccessful():
            yield self._passed
        else:
            yield self._failed

        if recorder.count:
            yield " ("
            summary = []

            successes = len(recorder.successes)
            if successes:
                summary.append("successes=" + str(successes))
            skips = len(recorder.skips)
            if skips:
                summary.append("skips=" + str(skips))
            failures = len(recorder.failures)
            if failures:
                summary.append("failures=" + str(failures))
            errors = len(recorder.errors)
            if errors:
                summary.append("errors=" + str(errors))
            unexpected_successes = len(recorder.unexpected_successes)
            if unexpected_successes:
                summary.append("unexpected_successes=" + str(unexpected_successes))

            yield ", ".join(summary)
            yield ")"

        yield "\n"

    def test_started(self, test):
        cls = test.__class__
        module = cls.__module__

        if self._last_test_module != module:
            self._last_test_module = module
            yield module
            yield "\n"

        if self._last_test_class != cls:
            self._last_test_class = cls
            yield self.indent
            yield cls.__name__
            yield "\n"

    def test_stopped(self, test):
        pass

    def test_errored(self, test, exc_info):
        self._after.extend(
            [
                "\n",
                "=" * self.line_width,
                "\n",
                self.ERROR,
                "\n",
                fully_qualified_name(test.__class__),
                ".",
                test._testMethodName,
            ],
        )
        return self.format_line(test, self._error)

    def test_failed(self, test, exc_info):
        self._after.extend(
            [
                "\n",
                "=" * self.line_width,
                "\n",
                self.FAIL,
                format_exc(exc_info),
                "\n",
                fully_qualified_name(test.__class__),
                ".",
                test._testMethodName,
            ],
        )
        return self.format_line(test, self._fail)

    def test_skipped(self, test, reason):
        self._after.extend(
            [
                "\n",
                "=" * self.line_width,
                "\n",
                self.SKIPPED,
                "\n",
                reason,
                "\n",
                fully_qualified_name(test.__class__),
                ".",
                test._testMethodName,
            ],
        )
        return self.format_line(test, self._skipped)

    def test_succeeded(self, test):
        return self.format_line(test, self._ok)

    def format_line(self, test, result):
        before = "{indent}{indent}{test._testMethodName} ...".format(
            indent=self.indent, test=test,
        )
        space = self.line_width - len(before) - len(result)
        return before + " " * space + result + "\n"


class Recorder(object):
    def __init__(self):
        self.errors = []
        self.failures = []
        self.skips = []
        self.successes = []
        self.unexpected_successes = []

    @property
    def count(self):
        return sum(
            len(tests) for tests in (
                self.errors,
                self.failures,
                self.skips,
                self.successes,
                self.unexpected_successes,
            )
        )

    def startTestRun(self):
        pass

    def stopTestRun(self):
        pass

    def addError(self, test, exc_info):
        self.errors.append(test)

    def addFailure(self, test, exc_info):
        self.failures.append(test)

    def addSkip(self, test, reason):
        self.skips.append(test)

    def addSuccess(self, test):
        self.successes.append(test)

    def addUnexpectedSuccess(self, test):
        self.unexpected_successes.append(test)

    def wasSuccessful(self):
        return not (self.errors or self.failures or self.unexpected_successes)
