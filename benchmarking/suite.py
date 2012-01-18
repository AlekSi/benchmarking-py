from __future__ import division, print_function, absolute_import

from .case import BenchmarkCase


class BenchmarkSuite(object):
    @staticmethod
    def collect_classes():
        classes = BenchmarkCase.__subclasses__()
        errors = [klass for klass in classes if not klass.__name__.endswith('BenchmarkCase')]
        if errors:
            raise NameError('Benchmark class should be called XXXBenchmarkCase: %r' % (errors,))
        return sorted(classes, key=str)

    @staticmethod
    def collect_method_names(klass):
        methods = [item for item in dir(klass) if item.startswith('benchmark_')]
        return sorted(methods)
