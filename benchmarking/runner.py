from __future__ import division
import gc
import timeit

from .suite import BenchmarkSuite
from .decorators import _get_metainfo
from . import _is_py3k


class BenchmarkRunner(object):
    def __init__(self, reporter, max_seconds=10, disable_gc=False):
        self.reporter = reporter
        self.max_seconds = max_seconds
        self.disable_gc = disable_gc

    def run_benchmark(self, method, setup, repeats, runs):
        """
        @param method: function or code C{str} to be benchmarked
        @param setup:  function or code C{str} to be called once before L{method}
        """
        timer = timeit.Timer(method, setup)
        res = []
        for _ in xrange(repeats):
            gc.collect()
            try:
                res.append(timer.timeit(number=runs))
            except Exception:
                timer.print_exc()
                raise
        return res

    def run(self):
        """
        @returns: C{False} if there were exceptions
        """
        classes = BenchmarkSuite.collect_classes()

        for klass in classes:
            klass.setUpClass()

            method_names = BenchmarkSuite.collect_method_names(klass)

            for method_name in method_names:
                instance = klass()
                instance.setUp()

                method = getattr(instance, method_name)
                if _is_py3k:
                    _im_class = method.__self__.__class__
                else:
                    _im_class = method.im_class
                method_name = '%s.%s' % (_im_class.__name__, method_name)
                self.reporter.before_benchmark(method_name)

                setup = 'pass' if self.disable_gc else 'gc.enable()'
                seconds = _get_metainfo(method, 'seconds') or self.max_seconds
                repeats = _get_metainfo(method, 'repeats') or 3
                runs = _get_metainfo(method, 'runs')

                # calculate number of runs
                if not runs:
                    single = self.run_benchmark(method, setup, 1, 1)[0]

                    if single > seconds:  # benchmark is slow
                        runs = 1
                    else:
                        runs = int(seconds / single)

                # run benchmark
                total = self.run_benchmark(method, setup, repeats, runs)

                self.reporter.after_benchmark(method_name, runs, total)
                instance.tearDown()
                del instance

            klass.tearDownClass()

        self.reporter.after_run()
