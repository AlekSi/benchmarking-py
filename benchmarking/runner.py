from __future__ import division, print_function, absolute_import

import sys
import gc
import time

from .suite import BenchmarkSuite
from .decorators import _get_metainfo
from .util import _no_data


if sys.version_info.major < 3:
    range = xrange


class TimeoutError(Exception):
    pass


class BenchmarkRunner(object):
    def __init__(self, reporter, max_seconds=3, repeats=10, disable_gc=False):
        self.reporter = reporter
        self.max_seconds = max_seconds
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

    @staticmethod
    def _wait_for_deferred(func, max_seconds):
        from twisted.internet import defer, reactor

        d = defer.maybeDeferred(func)
        res = {}

        def store_exception(failure):
            res['exc'] = failure.value

        def stop_reactor(_):
            if timeout_guard.active():
                timeout_guard.cancel()

            reactor.crash()

        d.addErrback(store_exception)

        if not d.called:
            timeout_guard = reactor.callLater(max_seconds,
                lambda: d.errback(TimeoutError("%r is still running after %d seconds" % (d, max_seconds))))
            d.addCallback(stop_reactor)
            reactor.run()

        if 'exc' in res:
            raise res['exc']

    def run_repeat(self, method, data, calls):
        """
        Call method(data) specified number of times.

        @param method: callable to be benchmarked
        @param data: argument for method
        @param calls: number of calls
        @return: number of seconds as C{float}
        """

        gc_enabled = gc.isenabled()
        gc.collect()
        if self.disable_gc:
            gc.disable()

        doit = method if data is _no_data else lambda: method(data)
        if 'twisted.internet' in sys.modules:
            func = doit
            doit = lambda: self._wait_for_deferred(func, self.max_seconds)

        try:
            timer_func = self.timer_func
            total = 0.0

            for _ in range(calls):
                start = timer_func()
                doit()
                stop = timer_func()
                total += stop - start

            return total

        finally:
            if gc_enabled:
                gc.enable()

    def get_calls(self, method, data, max_seconds):
        """
        Calculate number of calls.
        """

        calls, prev_time, time = 1, 0, 0
        while True:
            prev_time, time = time, self.run_repeat(method, data, calls)
            if prev_time <= time < (max_seconds * 0.9):
                calls = int(max_seconds / time * calls)
            else:
                return calls

    def run_benchmark(self, instance, method, data_label, data):
        """
        Runs instance's method with data. Handles setUp, tearDown. Delegates to run_repeat.
        """

        max_seconds = _get_metainfo(method, 'seconds') or self.max_seconds
        repeats = _get_metainfo(method, 'repeats') or self.repeats
        calls = _get_metainfo(method, 'calls') or self.get_calls(method, data, max_seconds)
        full_method_name = self._full_method_name(method)

        total = []
        for n in range(repeats):
            instance.setUp()

            self.reporter.before_repeat(full_method_name, data_label, n + 1, repeats)
            result = self.run_repeat(method, data, calls)
            total.append(result)
            self.reporter.after_repeat(full_method_name, data_label, n + 1, repeats, calls, result)

            instance.tearDown()

        return (calls, total)

    def run_instance_method(self, instance, method):
        """
        Run instance method with all data.
        """

        full_method_name = self._full_method_name(method)

        data_function = _get_metainfo(method, 'data_function') or (lambda: ((_no_data, _no_data),))
        for data_label, data in data_function():
            self.reporter.before_benchmark(full_method_name, data_label)
            calls, total = self.run_benchmark(instance, method, data_label, data)
            self.reporter.after_benchmark(full_method_name, data_label, calls, total)

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
