def _set_metainfo(method, key, value):
    key = '_benchmarking_%s' % key
    setattr(method, key, value)

def _get_metainfo(method, key):
    key = '_benchmarking_%s' % key
    return getattr(method, key, None)


def runs(number):
    def f(method):
        _set_metainfo(method, 'runs', number)
        return method
    return f

def seconds(number):
    def f(method):
        _set_metainfo(method, 'seconds', number)
        return method
    return f

def repeats(number):
    def f(method):
        _set_metainfo(method, 'repeats', number)
        return method
    return f
