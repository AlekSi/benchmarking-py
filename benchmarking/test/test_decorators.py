from __future__ import division, absolute_import

import unittest

from ..decorators import calls, seconds, deferred, TimeoutError, ReactorError
from ..util import is_py3k

if not is_py3k:
    from twisted.internet import defer, reactor


class DecoratorsTestCase(unittest.TestCase):
    def test_calls(self):
        res = {'n': 0}

        @calls(5)
        def f():
            res['n'] += 1
            return -1

        self.assertEqual(f(), 5)
        self.assertEqual(res['n'], 5)

    def test_seconds(self):
        res = {'n': 0}

        @seconds(0.1)
        def f():
            res['n'] += 1
            import time
            time.sleep(0.01)

        calls = f()
        self.assertTrue(1 < calls < 15)
        self.assertEqual(calls, res['n'])


class DecoratorsTwistedTestCase(unittest.TestCase):
    def test_deferred_syncronous_result(self):
        @deferred
        def simple_result():
            return 1

        self.assertEqual(simple_result(), 1)

    def test_deferred_wait_for_deferred(self):
        @deferred
        def deferred_result():
            d = defer.Deferred()
            reactor.callLater(0, d.callback, 1)
            return d

        self.assertEqual(deferred_result(), 1)

    def test_deferred_timeout(self):
        @deferred(max_seconds=0.1)
        def never_returns():
            return defer.Deferred()

        self.assertRaises(TimeoutError, never_returns)

    def test_deferred_unclean_reactor(self):
        @deferred
        def unclean():
            reactor.callLater(10000, lambda: None)
            return defer.succeed(1)

        self.assertRaises(ReactorError, unclean)

if is_py3k:
    DecoratorsTwistedTestCase = unittest.skip("Python 3 is not supported by Twisted")(DecoratorsTwistedTestCase)
