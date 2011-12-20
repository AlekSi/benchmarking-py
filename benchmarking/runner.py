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
    def _full_method_name(method):
        """
        Return instancemethod's name as string.
        """

        try:
            klass = method.__self__.__class__
        except AttributeError:
            # for old CPython, PyPy 1.5
            klass = method.im_class

        return '%s.%s' % (klass.__name__, method.__name__)

    def _wait_for_deferred(self, func):
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
            timeout_guard = reactor.callLater(self.max_seconds,
                lambda: d.errback(TimeoutError("%r is still running after %d seconds" % (d, self.max_seconds))))
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
            doit = lambda: self._wait_for_deferred(func)

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

    def run_benchmark(self, instance, method, data):
        """
        Runs instance's method with data. Handles setUp, tearDown. Delegates to run_repeat.
        """

        max_seconds = _get_metainfo(method, 'seconds') or self.max_seconds
        repeats = _get_metainfo(method, 'repeats') or self.repeats
        calls = _get_metainfo(method, 'calls') or self.get_calls(method, data, max_seconds)
        full_method_name = self._full_method_name(method)

        total = []
        for n in range(repeats):
            self.reporter.before_repeat(full_method_name, data, n + 1, repeats)
            instance.setUp()
            result = self.run_repeat(method, data, calls)
            total.append(result)
            instance.tearDown()
            self.reporter.after_repeat(full_method_name, data, n + 1, repeats, calls, result)
        return (calls, total)

    def run(self, classes):
        """
        @returns: result of L{after_run}
        """
        for klass in classes:
            klass.setUpClass()

            for method_name in BenchmarkSuite.collect_method_names(klass):
                instance = klass()

                method = getattr(instance, method_name)
                full_method_name = self._full_method_name(method)

                data_function = _get_metainfo(method, 'data_function') or (lambda: [_no_data])
                for data in data_function():
                    self.reporter.before_benchmark(full_method_name, data)
                    calls, total = self.run_benchmark(instance, method, data)
                    self.reporter.after_benchmark(full_method_name, data, calls, total)

                del instance

            klass.tearDownClass()

        return self.reporter.after_run()
