from __future__ import division, print_function, absolute_import

from .case import BenchmarkCase
from .decorators import project, calls, seconds, repeats, data, data_function, deferred, deferred_setup_teardown, \
    deferred_data_function, async


__all__ = ['BenchmarkCase',
           'project', 'calls', 'seconds', 'repeats', 'data', 'data_function', 'deferred', 'deferred_setup_teardown',
           'deferred_data_function', 'async']

version = '0.2.dev'


def main(reporter=None, classes=None):
    """
    Use it like this:
        if __name__ == '__main__':
            benchmarking.main()

    @returns: value of L{BenchmarkRunner.run()}
    """

    if reporter is None:
        from .reporters import ValueReporter
        reporter = ValueReporter()

    if classes is None:
        from .suite import BenchmarkSuite
        classes = BenchmarkSuite.collect_classes()

    from .runner import BenchmarkRunner
    runner = BenchmarkRunner(reporter=reporter)
    return runner.run(classes=classes)
