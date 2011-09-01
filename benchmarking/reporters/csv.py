from __future__ import division, print_function, absolute_import

import sys

from .reporter import Reporter


class CsvReporter(Reporter):
    """Prints comma-separated results in microseconds."""

    def __init__(self, csvfile=sys.stdout, dialect='excel', **fmtparam):
        import csv
        self.writer = csv.writer(csvfile, dialect=dialect, **fmtparam)

    def after_benchmark(self, method_name, calls, results):
        for n, time in enumerate([time * 1000000 for time in self.times_per_call(calls, results)]):
            self.writer.writerow([n, time])
        sys.stdout.flush()
