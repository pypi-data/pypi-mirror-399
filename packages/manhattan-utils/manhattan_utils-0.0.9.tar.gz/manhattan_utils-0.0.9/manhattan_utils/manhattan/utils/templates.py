
__all__ = ['css']


def css(m):
    """Return a string containing CSS classes flagged as True in the map"""
    return ' '.join([c for c, f in m.items() if f])
