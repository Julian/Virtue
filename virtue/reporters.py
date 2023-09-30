from collections import defaultdict
from traceback import format_exception
import sys
import time

from pyrsistent import v
from twisted.python.reflect import fullyQualifiedName as fully_qualified_name
import attr


@attr.s
class _DelayedMessage:
    """
    A test status message that will be shown at the end of a run.
    """

    width = attr.ib()
    status = attr.ib()
    subject = attr.ib()
    body = attr.ib(default=())

    def lines(self):
        yield "=" * self.width
        yield "\n"
        yield self.status
        yield "\n"
        if self.body:
            yield self.body


class Outputter:

    _last_test_class = None
    _last_test_module = None

    FAILED, PASSED = "FAILED", "PASSED"
    ERROR, FAIL, OK, SKIPPED = "[ERROR]", "[FAIL]", "[OK]", "[SKIPPED]"
    EXPECTED_FAILURE, UNEXPECTED_SUCCESS = "[XFAIL]", "[UNEXPECTED SUCCESS]"

    _COLORS = [
        ("_error", "RED", ERROR),
        ("_fail", "RED", FAIL),
        ("_failed", "RED", FAILED),
        ("_ok", "GREEN", OK),
        ("_passed", "GREEN", PASSED),
        ("_skipped", "BLUE", SKIPPED),
        ("_unexpected_success", "YELLOW", UNEXPECTED_SUCCESS),
        ("_expected_failure", "BLUE", EXPECTED_FAILURE),
    ]

    def __init__(self, colored=True, indent=" " * 2, line_width=120):
        self.indent = indent
        self.line_width = line_width

        if colored:
            from colorama import Fore, Style
            for attribute, color, text in self._COLORS:
                color = getattr(Fore, color)
                message = f"{Style.BRIGHT}{color}{text}{Style.RESET_ALL}"
                setattr(self, attribute, message)
        else:
            for attribute, _, text in self._COLORS:
                setattr(self, attribute, text)

        self._later = {
            status: defaultdict(list) for status in [
                self.SKIPPED,
                self.EXPECTED_FAILURE,
                self.FAIL,
                self.UNEXPECTED_SUCCESS,
                self.ERROR,
            ]
        }

    def _show_later(self, **kwargs):
        message = _DelayedMessage(width=self.line_width, **kwargs)
        self._later[message.status][message.body].append(message)

    def run_started(self):
        pass

    def run_stopped(self, counter, recorder):
        for status in self._later.values():
            for messages in status.values():
                if not messages:
                    continue
                yield "\n"
                yield from messages[0].lines()
                for message in messages:
                    yield "\n"
                    yield _test_name(message.subject)

        yield "\n"
        yield "-" * self.line_width

        # XXX
        total = counter.total

        tests = "tests" if total != 1 else "test"
        yield f"\nRan {total} {tests}{recorder.summary_extra}\n\n"
        if counter.succeeded:
            yield self._passed
        else:
            yield self._failed

        if total:
            yield " ("
            summary = []
            for attribute in (
                "successes",
                "skips",
                "failures",
                "errors",
                "expected_failures",
                "unexpected_successes",
            ):
                subcount = getattr(counter, attribute)
                if subcount:
                    summary.append(f"{attribute}={subcount}")
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
        self._show_later(
            status=self.ERROR,
            body="".join(format_exception(*exc_info)),
            subject=test,
        )
        return self.format_line(test, self._error)

    def test_failed(self, test, exc_info):
        self._show_later(
            status=self.FAIL,
            body="".join(format_exception(*exc_info)),
            subject=test,
        )
        return self.format_line(test, self._fail)

    def test_skipped(self, test, reason):
        self._show_later(status=self.SKIPPED, body=reason, subject=test)
        return self.format_line(test, self._skipped)

    def test_expectedly_failed(self, test, exc_info):
        self._show_later(status=self.EXPECTED_FAILURE, subject=test)
        return self.format_line(test, self._expected_failure)

    def test_unexpectedly_succeeded(self, test):
        self._show_later(status=self.UNEXPECTED_SUCCESS, subject=test)
        return self.format_line(test, self._unexpected_success)

    def test_succeeded(self, test):
        return self.format_line(test, self._ok)

    def format_line(self, test, result):
        before = f"{self.indent}{self.indent}{test._testMethodName} ..."
        return self._pad_center(left=before, right=result) + "\n"

    def _pad_center(self, left, right):
        space = self.line_width - len(left) - len(right)
        return left + " " * space + right


@attr.s
class Counter:
    """
    A counter is a recorder that does not hold references to tests it sees.
    """

    errors = attr.ib(default=0)
    failures = attr.ib(default=0)
    skips = attr.ib(default=0)
    expected_failures = attr.ib(default=0)
    unexpected_successes = attr.ib(default=0)
    successes = attr.ib(default=0)

    @property
    def total(self):
        return sum(attr.astuple(self))

    @property
    def succeeded(self):
        return not (self.errors or self.failures or self.unexpected_successes)

    def run_started(self):
        pass

    def run_stopped(self):
        pass

    def test_started(self, test):
        pass

    def test_stopped(self, test):
        pass

    def test_errored(self, test, exc_info):
        self.errors += 1

    def test_failed(self, test, exc_info):
        self.failures += 1

    def test_skipped(self, test, reason):
        self.skips += 1

    def test_expectedly_failed(self, *args, **kwargs):
        self.expected_failures += 1

    def test_unexpectedly_succeeded(self, test):
        self.unexpected_successes += 1

    def test_succeeded(self, test):
        self.successes += 1


@attr.s
class Recorder:

    errors = attr.ib(default=v())
    failures = attr.ib(default=v())
    skips = attr.ib(default=v())
    successes = attr.ib(default=v())
    expected_failures = attr.ib(default=v())
    unexpected_successes = attr.ib(default=v())

    summary_extra = ""

    def counts(self):
        return Counter(
            errors=len(self.errors),
            failures=len(self.failures),
            skips=len(self.skips),
            expected_failures=len(self.expected_failures),
            unexpected_successes=len(self.unexpected_successes),
            successes=len(self.successes),
        )

    def run_started(self):
        pass

    def run_stopped(self):
        pass

    def test_started(self, test):
        pass

    def test_stopped(self, test):
        pass

    def test_errored(self, test, exc_info):
        self.errors = self.errors.append((test, exc_info))

    def test_failed(self, test, exc_info):
        self.failures = self.failures.append((test, exc_info))

    def test_expectedly_failed(self, test, exc_info):
        self.expected_failures = self.expected_failures.append(
            (test, exc_info),
        )

    def test_skipped(self, test, reason):
        self.skips = self.skips.append(test)

    def test_succeeded(self, test):
        self.successes = self.successes.append(test)

    def test_unexpectedly_succeeded(self, test):
        self.unexpected_successes = self.unexpected_successes.append(test)


@attr.s
class Timer:
    """
    A timer is a recorder that records test runtime for tests that run.
    """

    _time = attr.ib(default=time.monotonic_ns, repr=False)
    _times = attr.ib(factory=list)
    _running = attr.ib(factory=dict)

    summary_extra = ""

    def run_started(self):
        self._start_time = self._time()

    def run_stopped(self, counter):
        took = self._time() - self._start_time
        equal = took / (counter.total or 1)
        for test, duration in self._times:
            if duration > 5 * equal:
                print(test, duration * 1e-6, "ms")
        self.summary_extra = f" in {took * 1e-9:.3f}s"

    def test_started(self, test):
        self._running[test] = self._time()

    def test_stopped(self, test):
        took = self._time() - self._running.pop(test)
        self._times.append((_test_name(test), took))

    def test_errored(self, test, exc_info):
        pass

    def test_failed(self, test, exc_info):
        pass

    def test_expectedly_failed(self, test, exc_info):
        pass

    def test_skipped(self, test, reason):
        pass

    def test_succeeded(self, test):
        pass

    def test_unexpectedly_succeeded(self, test):
        pass


@attr.s
class UnittestAdapter:

    _counter = attr.ib(factory=Counter)
    outputter = attr.ib(factory=Outputter)
    recorder = attr.ib(factory=Timer, repr=False)
    stream = attr.ib(default=sys.stdout)

    shouldStop = False

    @property
    def testsRun(self):
        return self._counter.total

    def startTestRun(self):
        self.recorder.run_started()
        self._counter.run_started()
        self.stream.writelines(self.outputter.run_started() or "")

    def stopTestRun(self):
        self.recorder.run_stopped(counter=self._counter)
        self._counter.run_stopped()
        self.stream.writelines(
            self.outputter.run_stopped(
                counter=self._counter,
                recorder=self.recorder
            ) or "",
        )

    def startTest(self, test):
        self.recorder.test_started(test)
        self._counter.test_started(test)
        self.stream.writelines(self.outputter.test_started(test) or "")

    def stopTest(self, test):
        self.recorder.test_stopped(test)
        self.stream.writelines(self.outputter.test_stopped(test) or "")

    def addError(self, test, exc_info):
        self.recorder.test_errored(test, exc_info)
        self.stream.writelines(
            self.outputter.test_errored(test, exc_info) or "",
        )

    def addFailure(self, test, exc_info):
        self.recorder.test_failed(test, exc_info)
        self.stream.writelines(
            self.outputter.test_failed(test, exc_info) or "",
        )

    def addSkip(self, test, reason):
        self.recorder.test_skipped(test, reason)
        self.stream.writelines(self.outputter.test_skipped(test, reason) or "")

    def addExpectedFailure(self, test, exc_info):
        self.recorder.test_expectedly_failed(test, exc_info)
        self.stream.writelines(
            self.outputter.test_expectedly_failed(test, exc_info) or "",
        )

    def addUnexpectedSuccess(self, test):
        self.recorder.test_unexpectedly_succeeded(test)
        self.stream.writelines(
            self.outputter.test_unexpectedly_succeeded(test) or "",
        )

    def addSuccess(self, test):
        self.recorder.test_succeeded(test)
        self.stream.writelines(self.outputter.test_succeeded(test) or "")

    def wasSuccessful(self):
        return self._counter.succeeded


def _test_name(test):
    """
    Retrieve the name of the given test.

    Arguments:

        test (TestCase):

            a test case instance

    """
    return f"{fully_qualified_name(test.__class__)}.{test._testMethodName}"
