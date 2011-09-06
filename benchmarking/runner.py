from __future__ import division, print_function, absolute_import

import sys
import gc
import time

from .suite import BenchmarkSuite
from .decorators import _get_metainfo
from .util import _no_data


if sys.version_info.major < 3:
    range = xrange


class BenchmarkRunner(object):
    def __init__(self, reporter, max_seconds=3, repeats=10, disable_gc=False):
        self.reporter = reporter
        self.max_seconds = max_seconds
        self.repeats = repeats
        self.disable_gc = disable_gc
        self.timer_func = time.time

    @staticmethod
    def _method_name(method):
        try:
            klass = method.__self__.__class__
        except AttributeError:
            # for old CPython, PyPy 1.5
            klass = method.im_class

        return '%s.%s' % (klass.__name__, method.__name__)

    def run_repeat(self, method, data, calls):
        """
        @param method: callable to be benchmarked
        @param data: benchmark method argument
        @param calls: number of calls
        @return: number of seconds as C{float}
        """

        gc_enabled = gc.isenabled()
        gc.collect()
        if self.disable_gc:
            gc.disable()

        # TODO: alternatives??
        #  1) getsourcelines, add loop, compile, exec
        #  2) start and stop timer inside loop
        def without_data():
            for _ in range(calls):
                method()

        def with_data():
            for _ in range(calls):
                method(data)

        doit = without_data if data is _no_data else with_data

        try:
            timer_func = self.timer_func
            start = timer_func()
            doit()
            stop = timer_func()
            return stop - start

        finally:
            if gc_enabled:
                gc.enable()

    def get_calls(self, method, data, max_seconds):
        """Calculate number of calls."""

        calls, prev_time, time = 1, 0, 0
        while True:
            prev_time, time = time, self.run_repeat(method, data, calls)
            if prev_time <= time < (max_seconds * 0.9):
                calls = int(max_seconds / time * calls)
            else:
                return calls

    def run_benchmark(self, method, data):
        max_seconds = _get_metainfo(method, 'seconds') or self.max_seconds
        repeats = _get_metainfo(method, 'repeats') or self.repeats
        calls = _get_metainfo(method, 'calls') or self.get_calls(method, data, max_seconds)
        method_name = self._method_name(method)

        res = []
        for n in range(repeats):
            self.reporter.before_repeat(method_name, data, n + 1, repeats)
            result = self.run_repeat(method, data, calls)
            res.append(result)
            self.reporter.after_repeat(method_name, data, n + 1, repeats, calls, result)
        return (calls, res)

    def run(self):
        """
        @returns: result of L{after_run}
        """
        for klass in BenchmarkSuite.collect_classes():
            klass.setUpClass()

            for method_name in BenchmarkSuite.collect_method_names(klass):
                instance = klass()
                instance.setUp()

                method = getattr(instance, method_name)
                method_name = self._method_name(method)

                data_function = _get_metainfo(method, 'data_function') or (lambda: [_no_data])
                for data in data_function():
                    self.reporter.before_benchmark(method_name, data)
                    calls, total = self.run_benchmark(method, data)
                    self.reporter.after_benchmark(method_name, data, calls, total)

                instance.tearDown()
                del instance

            klass.tearDownClass()

        return self.reporter.after_run()
