class Dict(dict):
    """dict with d.x feature"""

    def __init__(self, keys=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(keys, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"Dict object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value