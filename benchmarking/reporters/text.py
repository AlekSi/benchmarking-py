from __future__ import division, print_function, absolute_import

import sys
if sys.version_info.major < 3:
    import repr as reprlib
else:
    import reprlib

from .reporter import Reporter


r = reprlib.Repr()
r.maxlevel = 2
r.maxother = 60
repr = r.repr


class TextReporter(Reporter):
    """Prints text results to stdout."""

    def before_repeat(self, method_name, data, current, total):
        print("  %5d / %d" % (current, total), end=': ')
        sys.stdout.flush()

    def after_repeat(self, method_name, data, current, total, calls, result):
        print('%f usec per call' % (result * 1000000 / calls))

    def before_benchmark(self, method_name, data):
        print('%s(%s)' % (method_name, repr(data)), end=':\n')
        sys.stdout.flush()

    def after_benchmark(self, method_name, data, calls, results):
        repeats = len(results)
        print("  %d calls per repeat, best of %d repeats: %f usec per call" % (calls, repeats, self.min_max_time_per_call(calls, results)[0] * 1000000))
        sys.stdout.flush()
