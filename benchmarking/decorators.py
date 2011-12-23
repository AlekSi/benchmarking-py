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

        _set_metainfo(wrapper, 'calls', number)
        return wrapper
    return f


def seconds(func=None, max_seconds=3):
    """Specifies a number of seconds for single repeat."""

    def f(method):
        params = {}

        def calculate_calls(runner, instance, method, data):
            """
            Calculate number of calls.
            """

            def repeater(func, calls):
                def f(*args, **kwargs):
                    for _ in range(calls):
                        func(*args, **kwargs)

                return f

            calls, prev_time, time = 1, 0, 0
            while True:
                instance.setUp()
                params['calls'] = calls
                prev_time, time = time, runner.run_repeat(method, data)
                instance.tearDown()

                if prev_time <= time < (max_seconds * 0.9):
                    calls = int(max_seconds / time * calls)
                else:
                    return calls

        @wraps(method)
        def wrapper(*args, **kwargs):
            for _ in range(params['calls']):
                method(*args, **kwargs)

        _set_metainfo(wrapper, 'calls', calculate_calls)
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
    """Wraps up deferred function to become synchronous with reactor stop/start around."""

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
    def _deferred(func):
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
                        d.callback(None)

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

        _set_metainfo(wrapper, 'calls', requests)
        return wrapper

    if func is None:
        return _deferred
    else:
        return _deferred(func)
