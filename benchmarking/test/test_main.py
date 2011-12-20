from __future__ import division, absolute_import

import unittest

from ..case import BenchmarkCase
from .. import main

class MainBenchmarkCase(BenchmarkCase):
    pass


class MainTestCase(unittest.TestCase):
    def test_main(self):
        main(classes=[MainBenchmarkCase])
