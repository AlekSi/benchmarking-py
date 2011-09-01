from __future__ import division, print_function, absolute_import

from .case import BenchmarkCase
from .decorators import calls, seconds, repeats

__all__ = ['BenchmarkCase', 'calls', 'seconds', 'repeats']

import platform
if platform.python_version_tuple()[0] == '3':
    _is_py3k = True
    xrange = range
else:
    _is_py3k = False


def main(reporter=None):
    """
    Use it like this:
        if __name__ == '__main__':
            benchmarking.main()
    """

    if reporter is None:
        from .reporters import TextReporter, CsvReporter, CodeSpeedReporter, MultiReporter
        r1 = TextReporter(min_only=False)
        r2 = CodeSpeedReporter('http://localhost:8000', less_is_better=True,  project='Test Time Project',  commitid=123, environment='test')
        r3 = CodeSpeedReporter('http://localhost:8000', less_is_better=False, project='Test Speed Project', commitid=123, environment='test')
        r4 = CsvReporter()
        reporter = MultiReporter([r1, r2, r3, r4])

    from .runner import BenchmarkRunner
    runner = BenchmarkRunner(reporter=reporter)
    return runner.run()
