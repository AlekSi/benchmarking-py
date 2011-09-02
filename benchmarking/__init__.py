from __future__ import division, print_function, absolute_import

from .case import BenchmarkCase
from .decorators import calls, seconds, repeats

__all__ = ['BenchmarkCase', 'calls', 'seconds', 'repeats']


def main(reporter=None):
    """
    Use it like this:
        if __name__ == '__main__':
            benchmarking.main()
    """

    if reporter is None:
        from .reporters import TextReporter
        reporter = TextReporter()

    from .runner import BenchmarkRunner
    runner = BenchmarkRunner(reporter=reporter)
    return runner.run()
