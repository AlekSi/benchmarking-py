from __future__ import division, print_function, absolute_import

import sys
import gc
import timeit

from .suite import BenchmarkSuite
from .decorators import _get_metainfo


if sys.version_info.major < 3:
    range = xrange


class BenchmarkRunner(object):
    def __init__(self, reporter, max_seconds=3, repeats=10, disable_gc=False):
        self.reporter = reporter
        self.max_seconds = max_seconds
        self.repeats = repeats
        self.disable_gc = disable_gc

    @staticmethod
    def _method_name(method):
        klass = method.__self__.__class__
        return '%s.%s' % (klass.__name__, method.__name__)

    @staticmethod
    def run_repeat(method, setup, calls):
        """
        @param method: function or code C{str} to be benchmarked
        @param setup:  function or code C{str} to be called once before L{method}
        """
        timer = timeit.Timer(method, setup)
        gc.collect()
        try:
            return timer.timeit(number=calls)
        except Exception:
            timer.print_exc()
            raise

    @classmethod
    def get_calls(cls, method, setup, max_seconds):
        calls, prev_time, time = 1, 0, 0
        while True:
            prev_time, time = time, cls.run_repeat(method, setup, calls)
            if prev_time <= time < (max_seconds * 0.9):
                calls = int(max_seconds / time * calls)
            else:
                return calls

    def run_benchmark(self, method):
        setup = 'pass' if self.disable_gc else 'gc.enable()'
        max_seconds = _get_metainfo(method, 'seconds') or self.max_seconds
        repeats = _get_metainfo(method, 'repeats') or self.repeats
        calls = _get_metainfo(method, 'calls') or self.get_calls(method, setup, max_seconds)
        method_name = self._method_name(method)

        res = []
        for n in range(repeats):
            self.reporter.before_repeat(method_name, n + 1, repeats)
            result = self.run_repeat(method, setup, calls)
            res.append(result)
            self.reporter.after_repeat(method_name, n + 1, repeats, calls, result)
        return (calls, res)

    def run(self):
        """
        @returns: C{False} if there were exceptions
        """
        for klass in BenchmarkSuite.collect_classes():
            klass.setUpClass()

            for method_name in BenchmarkSuite.collect_method_names(klass):
                instance = klass()
                instance.setUp()

                method = getattr(instance, method_name)
                method_name = self._method_name(method)

                self.reporter.before_benchmark(method_name)
                calls, total = self.run_benchmark(method)
                self.reporter.after_benchmark(method_name, calls, total)

                instance.tearDown()
                del instance

            klass.tearDownClass()

        self.reporter.after_run()
