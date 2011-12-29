import sys


class NoData(object):
    def __repr__(self):
        return ''


_no_data = NoData()


range = xrange if sys.version_info.major < 3 else range


def class_from_instancemethod(instancemethod):
    """
    Returns class from given instancemethod.
    """

    try:
        return instancemethod.__self__.__class__
    except AttributeError:
        # for PyPy 1.5
        return instancemethod.im_class
