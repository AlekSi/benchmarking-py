import sys


class NoData(object):
    def __repr__(self):
        return ''


_no_data = NoData()


range = xrange if sys.version_info.major < 3 else range
