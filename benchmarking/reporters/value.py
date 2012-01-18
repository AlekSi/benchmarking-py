from __future__ import division, print_function, absolute_import

from .reporter import Reporter


class ValueReporter(Reporter):
    """
    Accumulates results and returns them in L{after_run}.
    """

    def __init__(self):
        self.results = {}

    def after_benchmark(self, project, benchmark, data_label, results):
        self.results.setdefault(project, dict())
        self.results[project].setdefault(benchmark, dict())
        self.results[project][benchmark][data_label] = results

    def after_run(self):
        return self.results
