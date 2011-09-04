import benchmarking

from examples.fibonacci import FibonacciRecursive, FibonacciRecursiveMemo, FibonacciIterational, \
                               FibonacciMatrix


class FibonacciBenchmarkCase(benchmarking.BenchmarkCase):
    @benchmarking.calls(500)
    @benchmarking.data(20)
    def benchmark_recursive(self, n):
        FibonacciRecursive().get(n)

    @benchmarking.repeats(3)
    @benchmarking.data(20)
    def benchmark_recursive_memo(self, n):
        FibonacciRecursiveMemo().get(n)

    @benchmarking.seconds(1)
    @benchmarking.data(5, 10, 20)
    def benchmark_iterational(self, n):
        FibonacciIterational().get(n)

    @benchmarking.seconds(2)
    @benchmarking.data(20)
    def benchmark_matrix(self, n):
        FibonacciMatrix().get(n)
