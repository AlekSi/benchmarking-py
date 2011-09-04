from __future__ import division, print_function, absolute_import

from .reporter import Reporter


class ValueReporter(Reporter):
    """
    Accumulates results and returns them in L{after_run}.
    """

    def __init__(self):
        self.results = {}

    def after_benchmark(self, method_name, data, calls, results):
        self.results.setdefault(method_name, dict())
        self.results[method_name][data] = (calls, results)

    def after_run(self):
        return self.results
