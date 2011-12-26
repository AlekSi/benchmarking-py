from __future__ import division, print_function, absolute_import

import gc
import time

from .suite import BenchmarkSuite
from .decorators import _get_metainfo
from .util import _no_data, range


class BenchmarkRunner(object):
    def __init__(self, reporter, repeats=10, disable_gc=False):
        self.reporter = reporter
        self.repeats = repeats
        self.disable_gc = disable_gc
        self.timer_func = time.time

    @staticmethod
    def _full_method_name(instancemethod):
        """
        Return instancemethod's name as string.
        """

        try:
            klass = instancemethod.__self__.__class__
        except AttributeError:
            # for old CPython, PyPy 1.5
            klass = instancemethod.im_class

        return '%s.%s' % (klass.__name__, instancemethod.__name__)

    def run_repeat(self, method, data):
        """
        Call method(data) specified number of times.

        @param method: callable to be benchmarked
        @param data: argument for method
        @return: tupe (number of seconds as C{float}, number of calls as C{int})
        """

        gc_enabled = gc.isenabled()
        gc.collect()
        if self.disable_gc:
            gc.disable()

        doit = method if data is _no_data else lambda: method(data)

        try:
            timer_func = self.timer_func

            start = timer_func()
            called = doit()
            stop = timer_func()

            assert isinstance(called, int), "Benchmark method should return number of times it has been called"

            return (stop - start, called)

        finally:
            if gc_enabled:
                gc.enable()

    def run_benchmark(self, instance, method, data_label, data):
        """
        Runs instance's method with data. Handles setUp, tearDown. Delegates to run_repeat.
        """

        repeats = _get_metainfo(method, 'repeats') or self.repeats

        full_method_name = self._full_method_name(method)

        total = []
        for n in range(repeats):
            instance.setUp()

            self.reporter.before_repeat(full_method_name, data_label, n + 1, repeats)
            result, called = self.run_repeat(method, data)
            total.append((called, result))
            self.reporter.after_repeat(full_method_name, data_label, n + 1, repeats, called, result)

            instance.tearDown()

        return total

    def run_instance_method(self, instance, method):
        """
        Run instance method with all data.
        """

        full_method_name = self._full_method_name(method)

        data_function = _get_metainfo(method, 'data_function') or (lambda: ((_no_data, _no_data),))
        for (data_label, data) in data_function():
            self.reporter.before_benchmark(full_method_name, data_label)
            total = self.run_benchmark(instance, method, data_label, data)
            self.reporter.after_benchmark(full_method_name, data_label, total)

    def run(self, classes):
        """
        @returns: result of L{after_run}
        """

        for klass in classes:
            klass.setUpClass()

            for method_name in BenchmarkSuite.collect_method_names(klass):
                instance = klass()
                self.run_instance_method(instance, getattr(instance, method_name))
                del instance

            klass.tearDownClass()

        return self.reporter.after_run()
