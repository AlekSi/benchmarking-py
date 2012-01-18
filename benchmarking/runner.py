from __future__ import division, print_function, absolute_import

import gc
import time

from .suite import BenchmarkSuite
from .decorators import _get_metainfo
from .util import _no_data, range, class_from_instancemethod


class BenchmarkRunner(object):
    def __init__(self, reporter, repeats=10, disable_gc=False):
        self.reporter = reporter
        self.repeats = repeats
        self.disable_gc = disable_gc
        self.timer_func = time.time

    @staticmethod
    def _project_and_benchmark(instancemethod):
        """
        Return project and benchmark from instancemethod for reporter.
        """

        class_name = class_from_instancemethod(instancemethod).__name__.replace('BenchmarkCase', '')
        benchmark = instancemethod.__name__.replace('benchmark_' , '')
        project = _get_metainfo(instancemethod, 'project')
        if project:
            benchmark = class_name.lower() + '_' + benchmark
        else:
            project = class_name
        return {'project': project, 'benchmark': benchmark}

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

        project_and_benchmark = self._project_and_benchmark(method)

        total = []
        for n in range(repeats):
            instance.setUp()

            self.reporter.before_repeat(data_label=data_label, current=(n + 1), total=repeats, **project_and_benchmark)
            result, called = self.run_repeat(method, data)
            total.append((called, result))
            self.reporter.after_repeat(data_label=data_label, current=(n + 1), total=repeats, calls=called, result=result, **project_and_benchmark)

            instance.tearDown()

        return total

    def run_instance_method(self, instance, method):
        """
        Run instance method with all data.
        """

        project_and_benchmark = self._project_and_benchmark(method)

        data_function = _get_metainfo(method, 'data_function') or (lambda: ((_no_data, _no_data),))
        for (data_label, data) in data_function():
            self.reporter.before_benchmark(data_label=data_label, **project_and_benchmark)
            total = self.run_benchmark(instance, method, data_label, data)
            self.reporter.after_benchmark(data_label=data_label, results=total, **project_and_benchmark)

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
