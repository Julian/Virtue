from time import time
from traceback import format_exc
import sys

from colorama import Fore, Style
from twisted.python.reflect import fullyQualifiedName as fully_qualified_name


class ComponentizedReporter(object):

    shouldStop = False

    def __init__(self, outputter=None, recorder=None, stream=sys.stdout):
        if outputter is None:
            outputter = Outputter()
        if recorder is None:
            recorder = Recorder()

        self.outputter = outputter
        self.recorder = recorder
        self.stream = stream

    def startTestRun(self):
        self._start_time = time()
        self.recorder.startTestRun()
        self.stream.writelines(self.outputter.run_started() or "")

    def stopTestRun(self):
        self.recorder.stopTestRun()
        runtime = time() - self._start_time
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

    def addSuccess(self, test):
        self.recorder.addSuccess(test)
        self.stream.writelines(self.outputter.test_succeeded(test) or "")

    def wasSuccessful(self):
        return self.recorder.wasSuccessful()


class Outputter(object):

    _last_test_class = None
    _last_test_module = None

    def __init__(self, indent=" " * 2, line_width=120):
        self.indent = indent
        self.line_width = line_width

        self._after = []

    def run_started(self):
        pass

    def run_stopped(self, recorder, runtime):
        for line in self._after:
            yield line
        yield "\n"
        yield "-" * self.line_width
        yield "\n"
        yield "Ran {recorder.count} tests in {runtime:.3f}s\n".format(
            recorder=recorder, runtime=runtime,
        )
        yield "\n"
        if recorder.wasSuccessful():
            yield "{Style.BRIGHT}{Fore.GREEN}PASSED{Style.RESET_ALL}".format(
                Fore=Fore, Style=Style,
            )
        else:
            yield "{Style.BRIGHT}{Fore.RED}FAILED{Style.RESET_ALL}".format(
                Fore=Fore, Style=Style,
            )

        if recorder.count:
            yield " ("
            summary = []

            successes = len(recorder.successes)
            if successes:
                summary.append("successes=" + str(successes))
            failures = len(recorder.failures)
            if failures:
                summary.append("failures=" + str(failures))
            errors = len(recorder.errors)
            if errors:
                summary.append("errors=" + str(errors))

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
                "[ERROR]\n",
                format_exc(exc_info),
                "\n",
                fully_qualified_name(test.__class__),
                ".",
                test._testMethodName,
            ],
        )
        return self.format_line(
            test,
            "{Style.BRIGHT}{Fore.RED}[ERROR]{Style.RESET_ALL}".format(
                Fore=Fore, Style=Style,
            ),
        )

    def test_failed(self, test, exc_info):
        self._after.extend(
            [
                "\n",
                "=" * self.line_width,
                "\n",
                "[FAIL]\n",
                format_exc(exc_info),
                "\n",
                fully_qualified_name(test.__class__),
                ".",
                test._testMethodName,
            ],
        )
        return self.format_line(
            test,
            "{Style.BRIGHT}{Fore.RED}[FAIL]{Style.RESET_ALL}".format(
                Fore=Fore, Style=Style,
            ),
        )

    def test_succeeded(self, test):
        return self.format_line(
            test,
            "{Style.BRIGHT}{Fore.GREEN}[OK]{Style.RESET_ALL}".format(
                Fore=Fore, Style=Style,
            ),
        )

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
        self.successes = []

    @property
    def count(self):
        return len(self.errors) + len(self.failures) + len(self.successes)

    def startTestRun(self):
        pass

    def stopTestRun(self):
        pass

    def addError(self, test, exc_info):
        self.errors.append(test)

    def addFailure(self, test, exc_info):
        self.failures.append(test)

    def addSuccess(self, test):
        self.successes.append(test)

    def wasSuccessful(self):
        return not self.failures and not self.errors
