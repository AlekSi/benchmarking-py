import benchmarking

from examples.fibonacci import FibonacciRecursive, FibonacciRecursiveMemo, FibonacciIterational, \
                               FibonacciMatrix


class FibonacciBenchmarkCase(benchmarking.BenchmarkCase):
    @benchmarking.calls(500)
    def benchmark_recursive(self):
        FibonacciRecursive().get(20)

    @benchmarking.repeats(3)
    def benchmark_recursive_memo(self):
        FibonacciRecursiveMemo().get(20)

    @benchmarking.seconds(1)
    @benchmarking.data(5, 10, 20)
    def benchmark_iterational(self, n):
        FibonacciIterational().get(n)

    def matrix_data():
        n = 1
        while n <= 16:
            yield (n, n)
            n *= 2

    @benchmarking.data_function(matrix_data)
    def benchmark_matrix(self, n):
        FibonacciMatrix().get(n)
