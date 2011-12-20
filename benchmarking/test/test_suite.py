from __future__ import division, absolute_import

import unittest

from ..case import BenchmarkCase
from ..suite import BenchmarkSuite


class SuiteBenchmarkCase(BenchmarkCase):
    def benchmark_1(self):
        pass

    def benchmark_2(self):
        pass

    def other(self):
        pass


class SuiteTestCase(unittest.TestCase):
    def test_collect_method_names(self):
        self.assertEqual(['benchmark_1', 'benchmark_2'], BenchmarkSuite.collect_method_names(SuiteBenchmarkCase))
