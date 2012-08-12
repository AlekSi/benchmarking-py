import sys

is_py3k = sys.version_info[0] == 3
range = range if is_py3k else xrange


class NoData(object):
    def __repr__(self):
        return ''


_no_data = NoData()


def class_from_instancemethod(instancemethod):
    """
    Returns class from given instancemethod.
    """

    try:
        return instancemethod.__self__.__class__
    except AttributeError:
        # for PyPy 1.5
        return instancemethod.im_class
