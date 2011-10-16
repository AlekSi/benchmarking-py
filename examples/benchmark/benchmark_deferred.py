from twisted.internet import defer, reactor
# defer.setDebugging(True)

import benchmarking


class DeferredBenchmarkCase(benchmarking.BenchmarkCase):
    @benchmarking.calls(1)
    @benchmarking.repeats(1)
    def benchmark_callback(self):
        d = defer.Deferred()
        reactor.callLater(0, d.callback, 'benchmark_callback')
        return d

    @benchmarking.calls(1)
    @benchmarking.repeats(1)
    def benchmark_errback(self):
        d = defer.Deferred()
        reactor.callLater(0, d.errback, Exception('benchmark_errback'))
        return d

    @benchmarking.calls(1)
    @benchmarking.repeats(1)
    def benchmark_timeout(self):
        d = defer.Deferred()
        reactor.callLater(999, d.callback, 'never reached')
        return d
