import benchmarking

from examples.fibonacci import FibonacciRecursive, FibonacciRecursiveMemo, FibonacciIterational, FibonacciMatrix


class FibonacciBenchmarkCase(benchmarking.BenchmarkCase):
    @benchmarking.repeats(3)
    @benchmarking.calls(500)
    def benchmark_recursive_memo(self):
        FibonacciRecursiveMemo().get(20)

    @benchmarking.data(5, 10, 20)
    @benchmarking.seconds(1)
    def benchmark_iterational(self, n):
        FibonacciIterational().get(n)

    @benchmarking.data_function({'5': 5, '10': 10, '20': 20}.iteritems)
    @benchmarking.seconds(3)
    def benchmark_recursive(self, n):
        FibonacciRecursive().get(n)

    def matrix_data():
        n = 1
        while n <= 16:
            yield (str(n), n)
            n *= 2

    @benchmarking.data_function(matrix_data)
    @benchmarking.seconds(3)
    def benchmark_matrix(self, n):
        FibonacciMatrix().get(n)
