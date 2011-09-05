from __future__ import division, print_function, absolute_import

import sys

from .reporter import Reporter


class CodeSpeedReporter(Reporter):
    """Reporter for CodeSpeed."""

    verbose = True

    def __init__(self, root_url, less_is_better=True, **kwargs):
        self.less_is_better = less_is_better

        try:
            from codespeed_client import Client
        except ImportError as e:
            msg = str(e) + '\n\nPlease install codespeed_client package: pip install codespeed_client'
            raise ImportError(msg)

        self.client = Client(root_url, **kwargs)

    def after_benchmark(self, method_name, data, calls, results):
        if self.less_is_better:
            min_value, max_value = self.min_max_time_per_call(calls, results)  # less is better - default for new CodeSpeed benchmarks
            value = min_value
        else:
            min_value, max_value = self.min_max_speed(calls, results)
            value = max_value

        project, benchmark = method_name.split('.')
        project = project.replace('BenchmarkCase', '')
        benchmark = benchmark.replace('benchmark_', '')
        # TODO: use data
        self.client.add_result(project=project, benchmark=benchmark, result_value=value, min=min_value, max=max_value)

    def after_run(self):
        from codespeed_client import UploadError

        if self.verbose:
            print("Uploading %d results to %s... " % (len(self.client.data), self.client.url), end='', file=sys.stderr)

        try:
            code, body = self.client.upload_results()
        except UploadError as e:
            code, body = e.errno, e.strerror
            raise
        finally:
            if self.verbose:
                print("%s - %s" % (code, body), file=sys.stderr)
