from __future__ import division, print_function, absolute_import

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


class ReactorError(Exception):
    pass


def deferred(func_or_class=None, max_seconds=120):
    """
    Class or function decorator that makes deferred synchronous with reactor stop/start around.

    For function: wraps up deferred function to become synchronous with reactor stop/start around.

    For class: wraps up all class methods starting with 'benchmark_' with deferred decorator, makes
    setUp and tearDown deferred and run inside the same reactor start/stop pair.

    @param max_seconds: maximum running time for reactor
    @type max_seconds: C{int}
    """

    def _deferred(func_or_class):
        if isinstance(func_or_class, type):
            klass = func_or_class
            setUp = klass.setUp
            tearDown = klass.tearDown

            klass.setUp = lambda self: None
            klass.tearDown = lambda self: None

            for method in dir(klass):
                if method.startswith('benchmark_'):
                    setattr(klass, method, deferred(max_seconds=max_seconds)(deferred_setup_teardown(setUp=setUp, tearDown=tearDown)(getattr(klass, method))))

            return klass
        else:
            func = func_or_class

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

                def stop_reactor():
                    if timeout_guard.active():
                        timeout_guard.cancel()

                    reactor.iterate(0)

                    reactor.disconnectAll()
                    reactor.crash()

                    if reactor.threadpool is not None:
                        reactor._stopThreadPool()

                    if len(reactor.getDelayedCalls()) != 0:
                        calls = reactor.getDelayedCalls()

                        for call in calls:
                            call.cancel()

                        if 'exception' not in res:
                            res['exception'] = ReactorError("Reactor unclean: delayed calls %s" % (map(str, calls), ))

                timeout_guard = reactor.callLater(max_seconds,
                    lambda: d.errback(TimeoutError("%r is still running after %d seconds" % (d, max_seconds))))
                reactor.callWhenRunning(d.addCallback, lambda _: reactor.callLater(0, stop_reactor))
                reactor.run()

                if 'exception' in res:
                    raise res['exception']

                return res['result']

            return wrapper

    if func_or_class is None:
        return _deferred
    else:
        return _deferred(func_or_class)


def deferred_setup_teardown(setUp, tearDown):
    """
    @param setUp: function to be called before running the deferred
    @type setUp: C{func}
    @param tearDown: function to be called after running the deferred
    @type tearDown: C{func}
    """
    def _deferred_setup_teardown(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Waits for deffered to callback.

            @type d: deferred; otherwise returns it as is.
            """
            from twisted.internet import defer

            return defer.maybeDeferred(setUp, args[0]).addCallback(lambda _: func(*args, **kwargs) \
                    .addBoth(lambda result: defer.maybeDeferred(tearDown, args[0]).addCallback(lambda _: result)))

        return wrapper

    return _deferred_setup_teardown


def async(func=None, concurrency=1, requests=None, duration=None):
    """
    Asynchronous benchmark runner.

    Runs wrapped deferred action with concurrency and limiting number of requests OR test duration.

    One of C{requests} or C{duration} should be specified, but not both.

    Example::

        @async(concurrency=10)
        def benchmark_example():
            return defer.succeed(None)

    @param concurrency: maximum number of concurrent actions
    @type concurrency: C{int}
    @param requests: overall number of calls to perform
    @type requests: C{int}
    @param duration: length of test in seconds
    @type duration: C{float}
    """
    assert requests is not None or duration is not None, "either duration or requests should be specified"
    assert requests is None or duration is None, "can't specify both duration and requests"

    def _async(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from twisted.internet import defer, task, reactor

            d = defer.Deferred()
            sem = defer.DeferredSemaphore(concurrency)
            req = {'done': 0}
            if requests is not None:
                req['left'] = requests
            else:
                def finish():
                    starter.stop()
                    if sem.tokens == concurrency:
                        d.callback(req['done'])

                reactor.callLater(duration, finish)

            def startMore():
                def release(_):
                    req['done'] += 1
                    sem.release()

                    if not starter.running and sem.tokens == concurrency:
                        d.callback(req['done'])

                    return _

                def gotError(fail):
                    if not d.called:
                        d.errback(fail)
                    else:
                        print(fail)

                def acquired(_):
                    d = defer.maybeDeferred(func, *args, **kwargs).addErrback(gotError).addBoth(release)

                    if sem.tokens > 0 and not d.called:
                        startMore()

                if requests is not None:
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
