from __future__ import division, absolute_import

from twisted.internet import defer, reactor
import unittest

from ..decorators import deferred


@deferred
def simple_result():
    return 1


@deferred(max_seconds=3)
def deferred_result():
    d = defer.Deferred()
    reactor.callLater(0, d.callback, 1)

    return d


class DecoratorTestCase(unittest.TestCase):

    def test_wait_for_object(self):
        self.assertEqual(simple_result(), 1)

    def test_wait_for_deferred(self):
        self.assertEqual(deferred_result(), 1)
