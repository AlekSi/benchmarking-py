from __future__ import division, absolute_import

from twisted.internet import defer, reactor
import unittest

from ..decorators import calls, repeats
from ..runner import BenchmarkRunner, TimeoutError
from ..case import BenchmarkCase
from ..reporters import Reporter
from ..util import _no_data


def count(obj, key):
    setattr(obj, key, getattr(obj, key, 0) + 1)


class RunnerBenchmarkCase(BenchmarkCase):
    @classmethod
    def setUpClass(cls):
        count(cls, 'count_class_up')

    @classmethod
    def tearDownClass(cls):
        count(cls, 'count_class_down')

    def setUp(self):
        count(self, 'count_instance_up')

    def tearDown(self):
        count(self, 'count_instance_down')

    @calls(2)
    @repeats(3)
    def benchmark_1(self):
        count(self, 'count_benchmark_1')


class RunnerTestCase(unittest.TestCase):
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

    def test_run_benchmark(self):
        instance = RunnerBenchmarkCase()
        self.runner.run_benchmark(instance, instance.benchmark_1, _no_data)
        self.assertEqual(3, instance.count_instance_up)
        self.assertEqual(3, instance.count_instance_down)
        self.assertEqual(6, instance.count_benchmark_1)

    def test_run(self):
        self.runner.run([RunnerBenchmarkCase])
        self.assertEqual(1, RunnerBenchmarkCase.count_class_up)
        self.assertEqual(1, RunnerBenchmarkCase.count_class_down)
        self.assertFalse(hasattr(RunnerBenchmarkCase, 'count_instance_up'))
        self.assertFalse(hasattr(RunnerBenchmarkCase, 'count_instance_down'))
        self.assertFalse(hasattr(RunnerBenchmarkCase, 'count_benchmark_1'))
        self.assertFalse(hasattr(RunnerBenchmarkCase, 'count_benchmark_2'))
