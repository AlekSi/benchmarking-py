import sys


class NoData(object):
    def __repr__(self):
        return ''


_no_data = NoData()


if sys.version_info.major < 3:
    range = xrange
