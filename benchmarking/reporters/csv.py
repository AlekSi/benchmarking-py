from __future__ import division, print_function, absolute_import

import sys

from .reporter import Reporter


class CsvReporter(Reporter):
    """Prints comma-separated results in microseconds."""

    def __init__(self, csvfile=sys.stdout, dialect='excel', **fmtparam):
        import csv
        self.writer = csv.writer(csvfile, dialect=dialect, **fmtparam)

    def after_repeat(self, method_name, data, current, total, calls, result):
        self.writer.writerow([method_name, data, current, total, result * 1000000 / calls])
