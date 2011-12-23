from twisted.names.dns import DNSDatagramProtocol
from twisted.names.server import DNSServerFactory
from twisted.names import hosts, client
from twisted.internet import reactor

import benchmarking


class TwistedNamesBenchmarkCase(benchmarking.BenchmarkCase):
    def setUp(self):
        controller = DNSServerFactory([hosts.Resolver()])
        self._port = reactor.listenUDP(0, DNSDatagramProtocol(controller))
        self._resolver = client.Resolver(servers=[('127.0.0.1', self._port.getHost().port)])
        self._timeout = 1

    def tearDown(self):
        self._port.stopListening()

    @benchmarking.repeats(10)
    @benchmarking.deferred
    @benchmarking.async(concurrency=100, requests=10000)
    def benchmark_run(self):
        return self._resolver.lookupAddress(
            'localhost', timeout=(self._timeout,))
