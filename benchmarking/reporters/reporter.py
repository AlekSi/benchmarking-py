from __future__ import division, print_function, absolute_import


class Reporter(object):
    """
    Interface for other reporters; also contains common methods for them.
    """

    @classmethod
    def name(cls):
        return cls.__name__.replace('Reporter', '')

    @staticmethod
    def min_max_time_per_call(calls, results):
        return (min(results) / calls, max(results) / calls)

    @staticmethod
    def times_per_call(calls, results):
        return [time / calls for time in results]

    @staticmethod
    def min_max_speed(calls, results):
        return (calls / max(results), calls / min(results))

    @staticmethod
    def speeds(calls, results):
        return [calls / time for time in results]

    def before_repeat(self, method_name, current, total):
        """
        @param method_name: benchmark method name
        @param current: number of current repeat
        @param total: total number of repeats
        """
        pass

    def after_repeat(self, method_name, current, total, calls, result):
        """
        @param method_name: benchmark method name
        @param current: number of current repeat
        @param total: total number of repeats
        @param calls: number of calls per repeat
        @param result: number of seconds for current repeat
        """
        pass

    def before_benchmark(self, method_name):
        """
        @param method_name: benchmark method name
        """
        pass

    def after_benchmark(self, method_name, calls, results):
        """
        @param method_name: benchmark method name
        @param calls: number of benchmark method calls per repeat
        @param results: number of seconds per each repeat
        @type results: C{list}
        """
        pass

    def after_run(self):
        pass


class MultiReporter(object):
    """Proxy for several reporters."""

    def __init__(self, reporters):
        self.reporters = reporters

for method_name in dir(Reporter):
    if not (method_name.startswith('before_') or method_name.startswith('after_')):
        continue

    def decorator(m):
        def f(self, *args, **kwargs):
            for reporter in self.reporters:
                getattr(reporter, m)(*args, **kwargs)
        return f

    setattr(MultiReporter, method_name, decorator(method_name))
