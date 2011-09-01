from __future__ import division, print_function, absolute_import

from .case import BenchmarkCase


class BenchmarkSuite(object):
    @staticmethod
    def collect_classes():
        klasses = BenchmarkCase.__subclasses__()
        return sorted(klasses)

    @staticmethod
    def collect_method_names(klass):
        methods = [item for item in dir(klass) if item.startswith('benchmark_')]
        return sorted(methods)
