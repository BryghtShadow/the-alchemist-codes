from functools import reduce


class Asdf:
    @staticmethod
    def parse_obj(obj):
        if obj is None:
            return None
        if isinstance(obj, str):
            return obj if obj.startswith("RECIPE_") else None
        if isinstance(obj, dict):
            return Asdf.parse_map(obj)
        if isinstance(obj, list):
            return Asdf.parse_list(obj)
        return None

    @staticmethod
    def parse_map(obj):
        m = dict()
        for k, v in obj.items():
            v = Asdf.parse_obj(v)
            if v is not None:
                m[k] = v
        return m or None

    @staticmethod
    def parse_list(obj):
        l = []
        for v in obj:
            v = Asdf.parse_obj(v)
            if v is not None:
                l.append(v)
        if len(l) > 0 and isinstance(l[0], dict):
            def fn(acc, val):
                acc.update(val)
                return acc
            l = [reduce(fn, l, dict())]
        return l or None
