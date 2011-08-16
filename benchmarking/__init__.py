from .case import BenchmarkCase
from .decorators import runs, seconds, repeats

__all__ = ('BenchmarkCase', 'runs', 'seconds', 'repeats')

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
        r1 = TextReporter()
        r2 = CodeSpeedReporter('http://localhost:8000', project='Test Project', commitid=123)
        # r3 = CsvReporter()
        reporter = MultiReporter([r1, r2])

    from .runner import BenchmarkRunner
    runner = BenchmarkRunner(reporter=reporter)
    return runner.run()
