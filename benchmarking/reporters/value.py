from __future__ import division, print_function, absolute_import

from .reporter import Reporter


class ValueReporter(Reporter):
    """
    Accumulates results and returns them in L{after_run}.
    """

    def __init__(self):
        self.results = {}

    def after_benchmark(self, method_name, calls, results):
        self.results[method_name] = (calls, results)

    def after_run(self):
        return self.results
