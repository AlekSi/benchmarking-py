import unittest

from examples.fibonacci import FibonacciRecursive, FibonacciRecursiveMemo, FibonacciIterational, \
                               FibonacciMatrix


class FibonacciTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = [0,    1,     1,     2,     3,     5,     8,      13,     21,     34,
                        55,   89,    144,   233,   377,   610,   987,    1597,   2584,   4181,
                        6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229]

    def do_test(self, fibonacci):
        for i in xrange(len(self.expected)):
            self.assertEqual(self.expected[i], fibonacci.get(i))

    def test_recursive(self):
        self.do_test(FibonacciRecursive())

    def test_recursive_memo(self):
        self.do_test(FibonacciRecursiveMemo())

    def test_iterational(self):
        self.do_test(FibonacciIterational())

    def test_matrix(self):
        self.do_test(FibonacciMatrix())
