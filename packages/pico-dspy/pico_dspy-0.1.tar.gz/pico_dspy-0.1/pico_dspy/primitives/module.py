import inspect
import logging
from typing import Any

from pico_dspy.primitives.base_module import BaseModule
from pico_dspy.primitives.prediction import Prediction

logger = logging.getLogger(__name__)


class ProgramMeta(type):
    """Metaclass ensuring every ``dspy.Module`` instance is properly initialised."""

    def __call__(cls, *args, **kwargs):
        # Create the instance without invoking ``__init__`` so we can inject
        # the base initialization beforehand.
        obj = cls.__new__(cls, *args, **kwargs)
        if isinstance(obj, cls):
            # ``_base_init`` sets attributes that should exist on all modules
            # even when a subclass forgets to call ``super().__init__``.
            Module._base_init(obj)
            cls.__init__(obj, *args, **kwargs)
        return obj


class Module(BaseModule, metaclass=ProgramMeta):
    def _base_init(self):
        self._compiled = False

    def __init__(self, callbacks=None):
        self._compiled = False

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __call__(self, *args, **kwargs) -> Prediction:
        return self.forward(*args, **kwargs)

    def named_predictors(self):
        from pico_dspy.predict.predict import Predict

        return [(name, param) for name, param in self.named_parameters() if isinstance(param, Predict)]

    def predictors(self):
        return [param for _, param in self.named_predictors()]

    def set_lm(self, lm):
        for _, param in self.named_predictors():
            param.lm = lm

    def get_lm(self):
        all_used_lms = [param.lm for _, param in self.named_predictors()]

        if len(set(all_used_lms)) == 1:
            return all_used_lms[0]

        raise ValueError("Multiple LMs are being used in the module. There's no unique LM to return.")

    def __repr__(self):
        s = []

        for name, param in self.named_predictors():
            s.append(f"{name} = {param}")

        return "\n".join(s)

    def _set_lm_usage(self, tokens: dict[str, Any], output: Any):
        # Some optimizers (e.g., GEPA bootstrap tracing) temporarily patch
        # module.forward to return a tuple: (prediction, trace).
        # When usage tracking is enabled, ensure we attach usage to the
        # prediction object if present.
        prediction_in_output = None
        if isinstance(output, Prediction):
            prediction_in_output = output
        elif isinstance(output, tuple) and len(output) > 0 and isinstance(output[0], Prediction):
            prediction_in_output = output[0]
        if prediction_in_output:
            prediction_in_output.set_lm_usage(tokens)
        else:
            logger.warning(
                "Failed to set LM usage. Please return `dspy.Prediction` object from dspy.Module to enable usage tracking."
            )

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)

        if name == "forward" and callable(attr):
            # Check if forward is called through __call__ or directly
            stack = inspect.stack()
            forward_called_directly = len(stack) <= 1 or stack[1].function != "__call__"

            if forward_called_directly:
                logger.warning(
                    f"Calling module.forward(...) on {self.__class__.__name__} directly is discouraged. "
                    f"Please use module(...) instead."
                )

        return attr
