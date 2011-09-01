import benchmarking

from examples.fibonacci import FibonacciRecursive, FibonacciRecursiveMemo, FibonacciIterational, \
                               FibonacciMatrix


class FibonacciBenchmarkCase(benchmarking.BenchmarkCase):
    @classmethod
    def setUpClass(cls):
        cls.N = 20

    @benchmarking.calls(500)
    def benchmark_recursive(self):
        FibonacciRecursive().get(self.N)

    @benchmarking.repeats(3)
    def benchmark_recursive_memo(self):
        FibonacciRecursiveMemo().get(self.N)

    @benchmarking.seconds(1)
    def benchmark_iterational(self):
        FibonacciIterational().get(self.N)

    @benchmarking.seconds(2)
    def benchmark_matrix(self):
        FibonacciMatrix().get(self.N)
