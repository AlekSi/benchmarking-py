from __future__ import division, print_function, absolute_import

from .case import BenchmarkCase
from .decorators import calls, seconds, repeats

__all__ = ['BenchmarkCase', 'calls', 'seconds', 'repeats']

import sys
if sys.version_info.major == 3:
    _is_py3k = True
    _range = range
else:
    _is_py3k = False
    _range = xrange


def main(reporter=None):
    """
    Use it like this:
        if __name__ == '__main__':
            benchmarking.main()
    """

    if reporter is None:
        from .reporters import TextReporter, CsvReporter, CodeSpeedReporter, MultiReporter
        r1 = TextReporter(min_only=True)
        r2 = CodeSpeedReporter('http://localhost:8000', project='Test Project',  commitid=123, environment='test')
        r3 = CsvReporter()
        reporter = MultiReporter([r1, r2, r3])

    from .runner import BenchmarkRunner
    runner = BenchmarkRunner(reporter=reporter)
    return runner.run()
