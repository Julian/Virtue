from time import time
from traceback import format_exception
import sys

from pyrsistent import v
from twisted.python.reflect import fullyQualifiedName as fully_qualified_name
import attr


class Outputter(object):

    _last_test_class = None
    _last_test_module = None

    FAILED, PASSED = "FAILED", "PASSED"
    ERROR, FAIL, OK, SKIPPED = "[ERROR]", "[FAIL]", "[OK]", "[SKIPPED]"

    _COLORS = [
        ("_error", "RED", ERROR),
        ("_fail", "RED", FAIL),
        ("_failed", "RED", FAILED),
        ("_ok", "GREEN", OK),
        ("_passed", "GREEN", PASSED),
        ("_skipped", "BLUE", SKIPPED),
    ]

    def __init__(self, colored=True, indent=" " * 2, line_width=120):
        self.indent = indent
        self.line_width = line_width

        if colored:
            from colorama import Fore, Style
            message = "{Style.BRIGHT}{color}{text}{Style.RESET_ALL}"
            for attribute, color, text in self._COLORS:
                setattr(
                    self, attribute, message.format(
                        Style=Style, color=getattr(Fore, color), text=text,
                    )
                )
        else:
            for attribute, _, text in self._COLORS:
                setattr(self, attribute, text)

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
            for attribute in (
                "successes",
                "skips",
                "failures",
                "errors",
                "unexpected_successes",
            ):
                subcount = len(getattr(recorder, attribute))
                if subcount:
                    summary.append("{0}={1}".format(attribute, subcount))
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
            ] + format_exception(*exc_info) + [
                "\n",
                _test_name(test),
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
                "\n",
            ] + format_exception(*exc_info) + [
                "\n",
                _test_name(test),
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
        before = "{indent}{indent}{name} ...".format(
            indent=self.indent, name=test._testMethodName,
        )
        return self._pad_center(left=before, right=result) + "\n"

    def _pad_center(self, left, right):
        space = self.line_width - len(left) - len(right)
        return left + " " * space + right


@attr.s
class Counter(object):
    """
    A counter is a recorder that does not hold references to tests it sees.
    """

    errors = attr.ib(default=0)
    failures = attr.ib(default=0)
    expected_failures = attr.ib(default=0)
    unexpected_successes = attr.ib(default=0)
    successes = attr.ib(default=0)

    shouldStop = False

    @property
    def count(self):
        return sum(attr.astuple(self))

    testsRun = count

    def startTest(self, test):
        pass

    def stopTest(self, test):
        pass

    def addError(self, test, exc_info):
        self.errors += 1

    def addFailure(self, test, exc_info):
        self.failures += 1

    def addExpectedFailure(self, *args, **kwargs):
        self.expected_failures += 1

    def addUnexpectedSuccess(self, test):
        self.unexpected_successes += 1

    def addSuccess(self, test):
        self.successes += 1


@attr.s
class Recorder(object):

    errors = attr.ib(default=v())
    failures = attr.ib(default=v())
    skips = attr.ib(default=v())
    successes = attr.ib(default=v())
    unexpected_successes = attr.ib(default=v())

    shouldStop = False

    @property
    def count(self):
        return sum(len(tests) for tests in attr.astuple(self))

    def startTestRun(self):
        pass

    def stopTestRun(self):
        pass

    def startTest(self, test):
        pass

    def stopTest(self, test):
        pass

    def addError(self, test, exc_info):
        self.errors = self.errors.append((test, exc_info))

    def addFailure(self, test, exc_info):
        self.failures = self.failures.append((test, exc_info))

    def addSkip(self, test, reason):
        self.skips = self.skips.append(test)

    def addSuccess(self, test):
        self.successes = self.successes.append(test)

    def addUnexpectedSuccess(self, test):
        self.unexpected_successes = self.unexpected_successes.append(test)

    def wasSuccessful(self):
        return not (self.errors or self.failures or self.unexpected_successes)


@attr.s
class ComponentizedReporter(object):

    outputter = attr.ib(default=attr.Factory(Outputter))
    recorder = attr.ib(default=attr.Factory(Recorder), repr=False)
    stream = attr.ib(default=sys.stdout)
    _time = attr.ib(default=time, repr=False)

    shouldStop = False

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
        self.recorder.startTest(test)
        self.stream.writelines(self.outputter.test_started(test) or "")

    def stopTest(self, test):
        self.recorder.stopTest(test)
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


def _test_name(test):
    """
    Retrieve the name of the given test.

    Arguments:

        test (TestCase):

            a test case instance

    """

    return ".".join(
        (fully_qualified_name(test.__class__), test._testMethodName),
    )
