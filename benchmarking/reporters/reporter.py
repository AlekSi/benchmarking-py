from __future__ import division, print_function, absolute_import


class Reporter(object):
    """
    Interface for other reporters; also contains common methods for them.
    """

    @classmethod
    def name(cls):
        return cls.__name__.replace('Reporter', '')

    @staticmethod
    def min_max_time_per_call(results):
        times_per_call = Reporter.times_per_call(results)
        return (min(times_per_call), max(times_per_call))

    @staticmethod
    def times_per_call(results):
        return [time / calls for calls, time in results]

    @staticmethod
    def min_max_speed(results):
        speeds = Reporter.speeds(results)
        return (min(speeds), max(speeds))

    @staticmethod
    def speeds(results):
        return [calls / time for calls, time in results]

    def before_repeat(self, method_name, data_label, current, total):
        """
        @param method_name: benchmark method name
        @param data_label: benchmark method argument label
        @param current: number of current repeat
        @param total: total number of repeats
        """
        assert isinstance(method_name, str)
        assert isinstance(current, int)
        assert isinstance(total, int)

    def after_repeat(self, method_name, data_label, current, total, calls, result):
        """
        @param method_name: benchmark method name
        @param data_label: benchmark method argument label
        @param current: number of current repeat
        @param total: total number of repeats
        @param calls: number of calls per repeat
        @param result: number of seconds for current repeat
        """
        assert isinstance(method_name, str)
        assert isinstance(current, int)
        assert isinstance(total, int)
        assert isinstance(calls, int)
        assert isinstance(result, float)

    def before_benchmark(self, method_name, data_label):
        """
        @param method_name: benchmark method name
        @param data_label: benchmark method argument label
        """
        assert isinstance(method_name, str)

    def after_benchmark(self, method_name, data_label, results):
        """
        @param method_name: benchmark method name
        @param data_label: benchmark method argument label
        @param results: number of (calls, seconds) per each repeat
        @type results: C{list}
        """
        assert isinstance(method_name, str)
        assert isinstance(results, list)
        for i in results:
            assert isinstance(i[0], int)
            assert isinstance(i[1], float)

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
