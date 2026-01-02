class Prediction(dict):
    """A prediction object that contains the output of a DSPy module."""

    def __init__(self, completions: dict):
        super().__init__(completions)
        self._lm_usage = None

    def get_lm_usage(self):
        return self._lm_usage

    def set_lm_usage(self, value):
        self._lm_usage = value

    @classmethod
    def from_completions(cls, list_or_dict, usage=None):
        completions = _get_completions(list_or_dict)
        obj = cls({k: v[0] for k, v in completions.items()})

        if usage:
            obj.set_lm_usage({'usage': usage})

        return obj

    def __repr__(self):
        store_repr = ",\n    ".join(f"{k}={v!r}" for k, v in self.items())
        return f"Prediction(\n    {store_repr}\n)"

    def __str__(self):
        return self.__repr__()

    __getattr__ = dict.__getitem__


def _get_completions(list_or_dict: list | dict):
    if isinstance(list_or_dict, list):
        kwargs: dict = {}
        for arg in list_or_dict:
            for k, v in arg.items():
                kwargs.setdefault(k, []).append(v)
    else:
        kwargs = list_or_dict

    assert all(isinstance(v, list) for v in kwargs.values()), "All values must be lists"

    if kwargs:
        length = len(next(iter(kwargs.values())))
        assert all(len(v) == length for v in kwargs.values()), "All lists must have the same length"

    return kwargs
