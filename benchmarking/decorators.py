import signal
from functools import wraps

from .util import range


def _set_metainfo(method, key, value):
    key = '_benchmarking_%s' % key
    setattr(method, key, value)


def _get_metainfo(method, key):
    key = '_benchmarking_%s' % key
    return getattr(method, key, None)


def calls(number):
    """Specifies a number of benchmark method calls per single repeat."""

    def f(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            for _ in range(number):
                method(*args, **kwargs)

            return number

        return wrapper
    return f


def seconds(func=None, max_seconds=3):
    """Specifies a number of seconds for single repeat."""

    def f(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            cycle = {'stopped': False}
            def stop_cycle(_, __):
                cycle['stopped'] = True
            signal.signal(signal.SIGALRM, stop_cycle)
            signal.setitimer(signal.ITIMER_REAL, max_seconds)
            calls = 0
            try:
                while not cycle['stopped']:
                    method(*args, **kwargs)
                    calls += 1
            finally:
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                signal.setitimer(signal.ITIMER_REAL, 0)

            return calls

        return wrapper

    if func is None:
        return f
    else:
        return f(func)


def repeats(number):
    """Specifies a number of repeats."""

    def f(method):
        _set_metainfo(method, 'repeats', number)
        return method
    return f


def data(*args):
    """Specifies data arguments for benchmark."""

    def f(method):
        _set_metainfo(method, 'data_function', lambda: zip(args, args))
        return method
    return f


def data_function(func):
    """Specifies data function for benchmark."""

    def f(method):
        _set_metainfo(method, 'data_function', func)
        return method
    return f


def deferred_data_function(func):
    """Wraps up data function for benchmark when it returns Deferred."""

    def deferred_generator():
        for (label, data) in func():
            data = deferred(lambda: data)()

            yield (label, data)

    return data_function(deferred_generator)


class TimeoutError(Exception):
    pass


def deferred(func=None, max_seconds=120):
    """
    Wraps up deferred function to become synchronous with reactor stop/start around.

    Every deferred action should be wrapped up with this decorator before passing them to
    benchmark runner (because it's synchronous).

    @param max_seconds: maximum running time for reactor
    @type max_seconds: C{int}
    """

    def _deferred(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Waits for deffered to callback.

            @type d: deferred; otherwise returns it as is.
            """

            from twisted.internet import defer, reactor

            d = func(*args, **kwargs)

            if not isinstance(d, defer.Deferred):
                return d

            res = {}

            def store_result(result):
                res['result'] = result

            def store_exception(failure):
                res['exception'] = failure.value

            d.addCallbacks(store_result, store_exception)

            def stop_reactor(_):
                if timeout_guard.active():
                    timeout_guard.cancel()

                reactor.crash()

            if not d.called:
                timeout_guard = reactor.callLater(max_seconds,
                    lambda: d.errback(TimeoutError("%r is still running after %d seconds" % (d, max_seconds))))
                d.addCallback(stop_reactor)
                reactor.run()

            if 'exception' in res:
                raise res['exception']

            return res['result']

        return wrapper

    if func is None:
        return _deferred
    else:
        return _deferred(func)


def async(func=None, concurrency=1, requests=1000):
    """
    Asynchronous benchmark runner.

    Runs wrapped deferred action with concurrency and limiting number of requests.

    Example::

        @async(concurrency=10)
        def benchmark_example():
            return defer.succeed(None)

    @param concurrency: maximum number of concurrent actions
    @type concurrency: C{int}
    @param requests: overall number of calls to perform
    @type requests: C{int}
    """
    def _async(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from twisted.internet import defer, task

            d = defer.Deferred()
            sem = defer.DeferredSemaphore(concurrency)
            req = { 'left': requests }

            def startMore():
                def release(_):
                    sem.release()

                    if req['left'] == 0 and sem.tokens == concurrency:
                        d.callback(requests)

                    return _

                def gotError(fail):
                    d.errback(fail)

                def acquired(_):
                    defer.maybeDeferred(func, *args, **kwargs).addErrback(gotError).addBoth(release)

                req['left'] -= 1
                if req['left'] == 0:
                    starter.stop()

                return sem.acquire().addCallback(acquired)

            starter = task.LoopingCall(startMore)
            starter.start(0, True)

            return d

        return wrapper

    if func is None:
        return _async
    else:
        return _async(func)
