from virtue import reporters
from virtue.compat import unittest


class TestRecorder(unittest.TestCase):
    def setUp(self):
        self.recorder = reporters.Recorder()

    def test_it_records_errors(self):
        error, exc_info = object(), object()
        self.recorder.addError(error, exc_info)
        self.assertEqual(self.recorder.errors, [error])

    def test_it_records_failures(self):
        failure, exc_info = object(), object()
        self.recorder.addFailure(failure, exc_info)
        self.assertEqual(self.recorder.failures, [failure])

    def test_it_records_successes(self):
        success = object()
        self.recorder.addSuccess(success)
        self.assertEqual(self.recorder.successes, [success])
