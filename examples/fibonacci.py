"""Fibonacci numbers computation, taken from http://en.literateprograms.org/Fibonacci_numbers_(Python)"""

import sys
if sys.version_info[0] == 3:
    xrange = range


class FibonacciRecursive(object):
    """Naive recursive implementation."""

    def get(self, n):
        if n < 2:
            return n
        return self.get(n - 1) + self.get(n - 2)


class FibonacciRecursiveMemo(object):
    """Recursive implementation with memoization."""

    def __init__(self):
        self.memo = {0: 0, 1: 1}

    def get(self, n):
        if n not in self.memo:
            self.memo[n] = self.get(n - 1) + self.get(n - 2)
        return self.memo[n]


class FibonacciIterational(object):
    """Iterative implementation."""

    def get(self, n):
        a, b = 0, 1
        for i in xrange(n):
            a, b = b, a + b
        return a


class FibonacciMatrix(object):
    """The way of Math."""

    @staticmethod
    def mul(A, B):
        a, b, c = A
        d, e, f = B
        return a * d + b * e, a * e + b * f, b * e + c * f

    @classmethod
    def pow(cls, A, n):
        if n == 1:
            return A
        elif n & 1 == 0:
            return cls.pow(cls.mul(A, A), n // 2)
        else:
            return cls.mul(A, cls.pow(cls.mul(A, A), (n - 1) // 2))

    def get(self, n):
        if n < 2:
            return n
        return self.pow((1, 1, 0), n - 1)[0]
