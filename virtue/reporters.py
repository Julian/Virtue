from collections import defaultdict
from traceback import format_exception
import sys
import time

from pyrsistent import m, v
from pyrsistent.typing import PMap, PVector
import attrs


@attrs.frozen
class _DelayedMessage:
    """
    A test status message that will be shown at the end of a run.
    """

    width: int
    status: str
    subject: str
    body: str = ""

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
    _current_subtests_test = None

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

    def run_stopped(self, recorder, runtime):
        for status in self._later.values():
            for messages in status.values():
                if not messages:
                    continue
                yield "\n"
                yield from messages[0].lines()
                for message in messages:
                    yield "\n"
                    yield message.subject.id()

        yield "\n"
        yield "-" * self.line_width

        count = recorder.testsRun
        tests = "tests" if count != 1 else "test"

        subcount = recorder.subtests
        if subcount:
            pluralized = "subtests" if subcount != 1 else "subtest"
            subtests = f" with {subcount} {pluralized}"
        else:
            subtests = ""

        yield f"\nRan {count} {tests}{subtests} in {runtime:.3f}s\n\n"
        if recorder.wasSuccessful():
            yield self._passed
        else:
            yield self._failed

        if recorder.testsRun:
            yield " ("
            summary = []
            for attribute in (
                "successes",
                "skips",
                "failures",
                "errors",
                "expected_failures",
                "unexpected_successes",
                "subtest_failures",
                "subtest_errors",
            ):
                subcount = len(getattr(recorder, attribute))
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

    def subtest_succeeded(self, test, subtest):
        pass

    def subtest_failed(self, test, subtest, exc_info):
        self._show_later(
            status=self.FAIL,
            body="".join(format_exception(*exc_info)),
            subject=subtest,
        )
        return self.format_subtest_result(test, subtest, self._fail)

    def subtest_errored(self, test, subtest, exc_info):
        self._show_later(
            status=self.ERROR,
            body="".join(format_exception(*exc_info)),
            subject=subtest,
        )
        return self.format_subtest_result(test, subtest, self._error)

    def format_line(self, test, result):
        before = f"{self.indent}{self.indent}{test._testMethodName} ..."
        return self._pad_center(left=before, right=result) + "\n"

    def format_subtest_result(self, test, subtest, result):
        if self._current_subtests_test != test.id():
            before = f"{self.indent}{self.indent}{test._testMethodName}\n"
        else:
            before = ""
        self._current_subtests_test = test.id()
        line = f"{self.indent * 3}{subtest._subDescription()[1:-1]} ..."
        return f"{before}{self._pad_center(left=line, right=result)}\n"

    def _pad_center(self, left, right):
        space = self.line_width - len(left) - len(right)
        return left + " " * space + right


@attrs.define(slots=False)
class Counter:
    """
    A counter is a recorder that does not hold references to tests it sees.
    """

    errors: int = 0
    failures: int = 0
    expected_failures: int = 0
    unexpected_successes: int = 0
    successes: int = 0

    subtest_successes: int = 0
    subtest_failures: int = 0
    subtest_errors: int = 0

    shouldStop = False

    @property
    def count(self):
        return sum(attrs.astuple(self))

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

    def addSubTest(self, test, subtest, outcome):
        if outcome is None:
            self.subtest_successes += 1
        elif issubclass(outcome[0], test.failureException):
            self.subtest_failures += 1
        else:
            self.subtest_errors += 1


@attrs.define(slots=False)
class Recorder:

    errors: PVector = v()
    failures: PVector = v()
    skips: PVector = v()
    successes: PVector = v()
    expected_failures: PVector = v()
    unexpected_successes: PVector = v()

    subtest_successes: PMap = m()
    subtest_failures: PMap = m()
    subtest_errors: PMap = m()

    shouldStop = False

    @property
    def testsRun(self):
        fields = attrs.astuple(
            self,
            filter=lambda f, _: not f.name.startswith("subtest_"),
        )
        # It seems addSuccess is called for tests with all passing subtests
        # but the reverse isn't true if a subtest fails...
        tests_with_subtests = len(self.subtest_failures | self.subtest_errors)
        return sum(len(each) for each in fields) + tests_with_subtests

    @property
    def subtests(self):
        return sum(
            1
            for each in (
                self.subtest_successes,
                self.subtest_failures,
                self.subtest_errors,
            )
            for value in each.values()
            for _ in value
        )

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

    def addExpectedFailure(self, test, exc_info):
        self.expected_failures = self.expected_failures.append(
            (test, exc_info),
        )

    def addSkip(self, test, reason):
        self.skips = self.skips.append(test)

    def addUnexpectedSuccess(self, test):
        self.unexpected_successes = self.unexpected_successes.append(test)

    def addSuccess(self, test):
        self.successes = self.successes.append(test)

    def addSubTest(self, test, subtest, outcome):
        if outcome is None:
            self.subtest_successes = self.subtest_successes.set(
                test,
                self.subtest_successes.get(test, v()).append(subtest),
            )
        elif issubclass(outcome[0], test.failureException):
            self.subtest_failures = self.subtest_failures.set(
                test,
                self.subtest_failures.get(test, v()).append(subtest),
            )
        else:
            self.subtest_errors = self.subtest_errors.set(
                test,
                self.subtest_errors.get(test, v()).append(subtest),
            )

    def wasSuccessful(self):
        return not (
            self.errors
            or self.failures
            or self.unexpected_successes
            or self.subtest_failures
            or self.subtest_errors
        )


@attrs.define(slots=False)
class ComponentizedReporter:

    outputter: Outputter = attrs.field(factory=Outputter)
    recorder = attrs.field(factory=Recorder, repr=False)
    stream = attrs.field(default=sys.stdout)
    _time = attrs.field(default=time.time, repr=False)

    failfast = False  # FIXME: needed for subtests?
    shouldStop = False

    @property
    def testsRun(self):
        return self.recorder.testsRun

    def startTestRun(self):
        self._start_time = self._time()
        self.recorder.startTestRun()
        self.stream.writelines(self.outputter.run_started() or "")

    def stopTestRun(self):
        self.recorder.stopTestRun()
        runtime = self._time() - self._start_time
        self.stream.writelines(
            self.outputter.run_stopped(self.recorder, runtime) or "",
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
            self.outputter.test_errored(test, exc_info) or "",
        )

    def addFailure(self, test, exc_info):
        self.recorder.addFailure(test, exc_info)
        self.stream.writelines(
            self.outputter.test_failed(test, exc_info) or "",
        )

    def addSkip(self, test, reason):
        self.recorder.addSkip(test, reason)
        self.stream.writelines(self.outputter.test_skipped(test, reason) or "")

    def addExpectedFailure(self, test, exc_info):
        self.recorder.addExpectedFailure(test, exc_info)
        self.stream.writelines(
            self.outputter.test_expectedly_failed(test, exc_info) or "",
        )

    def addUnexpectedSuccess(self, test):
        self.recorder.addUnexpectedSuccess(test)
        self.stream.writelines(
            self.outputter.test_unexpectedly_succeeded(test) or "",
        )

    def addSuccess(self, test):
        self.recorder.addSuccess(test)
        self.stream.writelines(self.outputter.test_succeeded(test) or "")

    def addSubTest(self, test, subtest, outcome):
        self.recorder.addSubTest(test, subtest, outcome)
        if outcome is None:
            output = self.outputter.subtest_succeeded(test, subtest)
        elif issubclass(outcome[0], test.failureException):
            output = self.outputter.subtest_failed(test, subtest, outcome)
        else:
            output = self.outputter.subtest_errored(test, subtest, outcome)
        self.stream.writelines(output or "")

    def wasSuccessful(self):
        return self.recorder.wasSuccessful()
