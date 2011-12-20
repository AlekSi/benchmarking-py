from __future__ import division, absolute_import

from twisted.internet import defer, reactor
import unittest

from ..runner import BenchmarkRunner, TimeoutError
from ..reporters import Reporter
from ..util import _no_data


class BenchmarkRunnerTest(unittest.TestCase):
    def setUp(self):
        self.runner = BenchmarkRunner(reporter=Reporter(), max_seconds=1)

    def test_run_repeat_exception(self):
        def func():
            raise RuntimeError()

        self.assertRaises(RuntimeError, self.runner.run_repeat, func, _no_data, 1)

    def test_run_repeat_errback_sync(self):
        def func():
            return defer.fail(RuntimeError())

        self.assertRaises(RuntimeError, self.runner.run_repeat, func, _no_data, 1)

    def test_run_repeat_errback(self):
        def func():
            d = defer.Deferred()
            reactor.callLater(0, d.errback, RuntimeError())
            return d

        self.assertRaises(RuntimeError, self.runner.run_repeat, func, _no_data, 1)

    def test_run_repeat_timeout(self):
        def func():
            d = defer.Deferred()
            reactor.callLater(999, d.callback, 'never called')
            return d

        self.assertRaises(TimeoutError, self.runner.run_repeat, func, _no_data, 1)
