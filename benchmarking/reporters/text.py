from __future__ import division, print_function, absolute_import

import sys
import repr as reprlib

from .reporter import Reporter


r = reprlib.Repr()
r.maxlevel = 2
r.maxother = 60
repr = r.repr


class TextReporter(Reporter):
    """Prints text results to stdout."""

    def __init__(self, min_only=True):
        self.min_only = min_only

    def before_repeat(self, method_name, data, current, total):
        print("  %5d / %d" % (current, total), end=': ')
        sys.stdout.flush()

    def after_repeat(self, method_name, data, current, total, calls, result):
        print(result)

    def before_benchmark(self, method_name, data):
        print('%s(%s)' % (method_name, repr(data)), end=':\n')
        sys.stdout.flush()

    def after_benchmark(self, method_name, data, calls, results):
        repeats = len(results)
        if self.min_only:
            print("  %d calls per repeat, best of %d repeats: %f usec per call" % (calls, repeats, self.min_max_time_per_call(calls, results)[0] * 1000000))
        else:
            print("  %d calls per repeat, %d repeats: %r usec per call" % (calls, repeats, [time * 1000000 for time in self.times_per_call(calls, results)]))
        sys.stdout.flush()
