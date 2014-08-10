from time import time
import sys

from colorama import Fore, Style


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

    def run_started(self):
        pass

    def run_stopped(self, recorder, runtime):
        yield "\n"
        yield "-" * self.line_width
        yield "\n"
        yield "Ran {recorder.count} tests in {runtime:.3f}s\n".format(
            recorder=recorder, runtime=runtime,
        )
        yield "\n"
        yield "PASSED\n" if recorder.wasSuccessful() else "FAILED\n"

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
        return self.format_line(
            test,
            "{Style.BRIGHT}{Fore.RED}[ERROR]{Style.RESET_ALL}".format(
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
