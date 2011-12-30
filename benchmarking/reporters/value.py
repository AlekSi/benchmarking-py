from __future__ import division, print_function, absolute_import

from .reporter import Reporter


class ValueReporter(Reporter):
    """
    Accumulates results and returns them in L{after_run}.
    """

    def __init__(self):
        self.results = {}

    def after_benchmark(self, method_name, data_label, results):
        self.results.setdefault(method_name, dict())
        self.results[method_name][data] = results

    def after_run(self):
        return self.results
