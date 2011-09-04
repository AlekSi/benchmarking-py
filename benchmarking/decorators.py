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
        _set_metainfo(method, 'data_function', lambda: args)
        return method
    return f


def data_function(func):
    """Specifies data function for benchmark."""

    def f(method):
        _set_metainfo(method, 'data_function', func)
        return method
    return f
