from __future__ import division, print_function, absolute_import

import sys

from .reporter import Reporter


class TextReporter(Reporter):
    """Prints text results to stdout."""

    def __init__(self, min_only=True, name_length=50):
        self.name_length = name_length
        self.min_only = min_only

    def before_repeat(self, method_name, current, total):
        print("%d/%d" % (current, total), end='')

    def after_repeat(self, method_name, current, total, calls, result):
        print(result)

    def before_benchmark(self, method_name):
        print(method_name.ljust(self.name_length), ': ', end='')
        sys.stdout.flush()

    def after_benchmark(self, method_name, calls, results):
        repeats = len(results)
        if self.min_only:
            print("%d calls per repeat, best of %d repeats: %f usec per call" % (calls, repeats, self.min_max_time_per_call(calls, results)[0] * 1000000))
        else:
            print("%d calls per repeat, %d repeats: %r usec per call" % (calls, repeats, [time * 1000000 for time in self.times_per_call(calls, results)]))
        sys.stdout.flush()
