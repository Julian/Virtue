from unittest import TestCase

from virtue import reporters


class TestRecorder(TestCase):
    def setUp(self):
        self.recorder = reporters.Recorder()

    def test_it_records_errors(self):
        error, exc_info = object(), object()
        self.recorder.addError(error, exc_info)
        self.assertEqual(self.recorder.errors, [(error, exc_info)])
        self.assertFalse(self.recorder.wasSuccessful())

    def test_it_records_failures(self):
        failure, exc_info = object(), object()
        self.recorder.addFailure(failure, exc_info)
        self.assertEqual(self.recorder.failures, [(failure, exc_info)])
        self.assertFalse(self.recorder.wasSuccessful())

    def test_it_records_successes(self):
        success = object()
        self.recorder.addSuccess(success)
        self.assertEqual(self.recorder.successes, [success])
        self.assertTrue(self.recorder.wasSuccessful())

    def test_it_records_unexpected_successes(self):
        success = object()
        self.recorder.addUnexpectedSuccess(success)
        self.assertEqual(self.recorder.unexpected_successes, [success])
        self.assertFalse(self.recorder.wasSuccessful())

    def test_testsRun(self):
        test, exc_info, reason = object(), object(), "Because!"
        self.recorder.addError(test=test, exc_info=exc_info)
        self.recorder.addFailure(test=test, exc_info=exc_info)
        self.recorder.addSkip(test=test, reason=reason)
        self.recorder.addSuccess(test=test)
        self.recorder.addUnexpectedSuccess(test=test)
        self.assertEqual(self.recorder.testsRun, 5)
