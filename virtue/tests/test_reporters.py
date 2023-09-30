from unittest import TestCase

from virtue import reporters


class TestRecorder(TestCase):
    def setUp(self):
        self.recorder = reporters.Recorder()

    def test_it_records_errors(self):
        error, exc_info = object(), object()
        self.recorder.test_errored(error, exc_info)
        self.assertEqual(self.recorder.errors, [(error, exc_info)])

    def test_it_records_failures(self):
        failure, exc_info = object(), object()
        self.recorder.test_failed(failure, exc_info)
        self.assertEqual(self.recorder.failures, [(failure, exc_info)])

    def test_it_records_successes(self):
        success = object()
        self.recorder.test_succeeded(success)
        self.assertEqual(self.recorder.successes, [success])

    def test_it_records_unexpected_successes(self):
        success = object()
        self.recorder.test_unexpectedly_succeeded(success)
        self.assertEqual(self.recorder.unexpected_successes, [success])

    def test_counts(self):
        test, exc_info, reason = object(), object(), "Because!"
        self.recorder.test_errored(test=test, exc_info=exc_info)
        self.recorder.test_failed(test=test, exc_info=exc_info)
        self.recorder.test_skipped(test=test, reason=reason)
        self.recorder.test_succeeded(test=test)
        self.recorder.test_expectedly_failed(test=test, exc_info=exc_info)
        self.recorder.test_unexpectedly_succeeded(test=test)
        self.assertEqual(
            self.recorder.counts(), reporters.Counter(
                errors=1,
                failures=1,
                skips=1,
                successes=1,
                expected_failures=1,
                unexpected_successes=1,
            ),
        )
