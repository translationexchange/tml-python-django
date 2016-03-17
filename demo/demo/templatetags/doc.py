from django.template import Library

register = Library()


@register.filter(name="map")
def map(iterable, key):
    if not hasattr(iterable, '__iter__'):
        return ""
    else:
        ret = [0] * len(iterable)
        for i, item in enumerate(iterable):
            if hasattr(item, '__getitem__'):
                try:
                    ret[i] = item.__getitem__(key)
                except KeyError:
                    ret[i] = ''
            else:
                ret[i] = getattr(item, key, '')
        return ret