from __future__ import division, print_function, absolute_import

from .case import BenchmarkCase
from .decorators import calls, seconds, repeats, data, data_function


__all__ = ['BenchmarkCase',
           'calls', 'seconds', 'repeats', 'data', 'data_function']


def main(reporter=None):
    """
    Use it like this:
        if __name__ == '__main__':
            benchmarking.main()

    @returns: value of L{BenchmarkRunner.run()}
    """

    if reporter is None:
        from .reporters import ValueReporter
        reporter = ValueReporter()

    from .runner import BenchmarkRunner
    runner = BenchmarkRunner(reporter=reporter)
    return runner.run()
