from twisted.internet import defer, reactor

import benchmarking


class DeferredBenchmarkCase(benchmarking.BenchmarkCase):
    @benchmarking.calls(1)
    @benchmarking.repeats(1)
    def benchmark_callback(self):
        d = defer.Deferred()
        reactor.callLater(0, d.callback, None)
        return d

    @benchmarking.calls(1)
    @benchmarking.repeats(1)
    def benchmark_errback(self):
        d = defer.Deferred()
        reactor.callLater(0, d.errback, Exception())
        return d
