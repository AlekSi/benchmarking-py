from functools import wraps


def _set_metainfo(method, key, value):
    key = '_benchmarking_%s' % key
    setattr(method, key, value)


def _get_metainfo(method, key):
    key = '_benchmarking_%s' % key
    return getattr(method, key, None)


def calls(number):
    """Specifies a number of benchmark method calls per single repeat."""

    def f(method):
        _set_metainfo(method, 'calls', number)
        return method
    return f


def seconds(number):
    """Specifies a number of seconds for single repeat."""

    def f(method):
        _set_metainfo(method, 'seconds', number)
        return method
    return f


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
