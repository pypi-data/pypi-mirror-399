import hashlib


class Hasher(object):
    """
    Simple helper that feeds normalized values into an MD5 digest.
    """

    def __init__(self):
        self._digest = hashlib.md5()

    @property
    def digest(self):
        # Maintain backward compatibility for callers using `.digest.hexdigest()`
        return self._digest

    def add(self, value):
        if isinstance(value, str):
            v = value.encode("utf-8", "ignore")
        elif isinstance(value, (int, float, complex, bool)):
            v = str(value).encode("utf-8", "ignore")
        elif isinstance(value, (tuple, list)):
            for v in value:
                self.add(v)
            return
        elif isinstance(value, dict):
            for key, v in sorted(list(value.items()), key=lambda x: x[0]):
                self.add(key)
                self.add(v)
            return
        elif hasattr(value, "__dict__"):
            self.add(value.__dict__)
            return
        elif value is None:
            v = b'1bcdadabdf0de99dbdb747e951e967c5'
        else:
            raise AttributeError("Unhashable type: %s" % str(type(value)))

        self._digest.update(v if isinstance(v, (bytes, bytearray)) else str(v).encode('utf-8'))


def get_hash(node, fields=None, exclude=['pk', '_id'], target='pk'):
    """
    Here we generate a unique hash for a given node in the syntax tree.
    """

    hasher = Hasher()

    def add_to_hash(value):

        if isinstance(value, dict):
            if target in value:
                add_to_hash(value[target])
            else:
                attribute_list = []
                for key, v in sorted(list(value.items()), key=lambda x: x[0]):

                    if (fields is not None and key not in fields) \
                            or (exclude is not None and key in exclude):
                        continue
                    add_to_hash(key)
                    add_to_hash(v)
        elif isinstance(value, (tuple, list)) and value:
            for i, v in enumerate(value):
                hasher.add(i)
                add_to_hash(v)
        else:
            hasher.add(value)

    add_to_hash(node)

    return hasher.digest.hexdigest()
