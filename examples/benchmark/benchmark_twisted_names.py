"""
Benchmark on Twisted Names subsystem.
"""

from twisted.names.dns import DNSDatagramProtocol
from twisted.names.server import DNSServerFactory
from twisted.names import hosts, client
from twisted.internet import reactor

import benchmarking


@benchmarking.project("Twisted")
@benchmarking.deferred(max_seconds=15)
class ResolverBenchmarkCase(benchmarking.BenchmarkCase):
    def setUp(self):
        controller = DNSServerFactory([hosts.Resolver()])
        self._port = reactor.listenUDP(0, DNSDatagramProtocol(controller))
        self._resolver = client.Resolver(servers=[('127.0.0.1', self._port.getHost().port)])
        self._timeout = 1

    def tearDown(self):
        return self._port.stopListening()

    @benchmarking.repeats(15)
    @benchmarking.async(concurrency=10, duration=5)
    def benchmark_lookup(self):
        return self._resolver.lookupAddress('localhost', timeout=(self._timeout,))
