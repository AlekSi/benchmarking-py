from __future__ import division, print_function, absolute_import

from .reporter import Reporter


class ReporterFactory(object):
    @staticmethod
    def all_reporters():
        """Returns all known reporters names."""

        return [reporter.name() for reporter in Reporter.__subclasses__()]

    @staticmethod
    def by_name(name, **kwargs):
        """Creates new reporter."""

        if name == '_test':
            return Reporter()

        for reporter in Reporter.__subclasses__():
            if reporter.name().lower() == name.lower():
                return reporter(**kwargs)
        raise KeyError(name)
