from __future__ import division, print_function

import sys


class Reporter(object):
    """
    Reporter interface / null reporter.

    Result values are ignored.
    """

    def before_benchmark(self, method_name):
        """
        @param method_name: benchmark method name
        """
        pass

    def after_benchmark(self, method_name, runs, results):
        """
        @param method_name: benchmark method name
        @param runs: number of runs per repeat
        @param results: C{list} of results
        """
        pass

    def after_run(self):
        pass


class MultiReporter(Reporter):
    """Proxy for several reporters."""

    def __init__(self, reporters):
        self.reporters = reporters

for method_name in dir(Reporter):
    if method_name.startswith('_'):
        continue

    def decorator(m):
        def f(self, *args, **kwargs):
            for reporter in self.reporters:
                getattr(reporter, m)(*args, **kwargs)
        return f

    setattr(MultiReporter, method_name, decorator(method_name))


class TextReporter(Reporter):
    """Prints text results to stdout."""

    def __init__(self, only_min=True, name_length=50):
        self.name_length = name_length
        self.only_min = only_min

    def before_benchmark(self, method_name):
        print(method_name.ljust(self.name_length), ': ', end='')
        sys.stdout.flush()

    def after_benchmark(self, method_name, runs, results):
        if self.only_min:
            result = min(results)
            print("max %10.2f runs/sec (%7d runs in %5.2f seconds)" % (runs / result, runs, result))
        else:
            print("%r (total %d * %d runs)" % (results, len(results), runs))
        sys.stdout.flush()


class CsvReporter(Reporter):
    """Prints comma-separated values."""

    def __init__(self, csvfile=sys.stdout, dialect='excel', **fmtparam):
        import csv
        self.writer = csv.writer(csvfile, dialect=dialect, **fmtparam)

    def after_benchmark(self, method_name, runs, results):
        for n, result in enumerate(results):
            self.writer.writerow([n, '%d' % (result * 1000000)])
        sys.stdout.flush()


class CodeSpeedReporter(Reporter):
    verbose = True

    def __init__(self, root_url, less_is_better=True, **kwargs):
        self.less_is_better = less_is_better

        try:
            from codespeed_client import Client
        except ImportError as e:
            msg = e.message + '\nPlease install codespeed_client package: pip install codespeed_client'
            raise ImportError(msg)

        self.client = Client(root_url, **kwargs)

    def after_benchmark(self, method_name, runs, results):
        result = min(results)
        if self.less_is_better:
            result_value = result / runs    # speed ^ -1 (less is better, default for new benchmarks)
        else:
            result_value = runs / result    # speed (more is better)

        project, benchmark = method_name.split('.')
        project = project.replace('BenchmarkCase', '')
        benchmark = benchmark.replace('benchmark_', '')
        self.client.add_result(project=project, benchmark=benchmark, result_value=result_value)

    def after_run(self):
        if self.verbose:
            print("Uploading %d results to %s... " % (len(self.client.data), self.client.url), end='', file=sys.stderr)
        code, body = self.client.upload_results()
        if self.verbose:
            print("%s - %s" % (code, body), file=sys.stderr)
