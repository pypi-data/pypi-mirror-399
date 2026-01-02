import logging
import random
from typing import TYPE_CHECKING

from pydantic import BaseModel

from pico_dspy.adapters.json_adapter import JSONAdapter
from pico_dspy.predict.parameter import Parameter
from pico_dspy.primitives.module import Module
from pico_dspy.primitives.prediction import Prediction
from pico_dspy.signatures.signature import Signature, ensure_signature

if TYPE_CHECKING:
    from pico_dspy.clients.lm import LM

logger = logging.getLogger(__name__)


class Predict(Module, Parameter):
    """Basic DSPy module that maps inputs to outputs using a language model.

    Args:
        signature: The input/output signature describing the task.
        callbacks: Optional list of callbacks for instrumentation.
        **config: Default keyword arguments forwarded to the underlying
            language model. These values can be overridden for a single
            invocation by passing a ``config`` dictionary when calling the
            module. For example::

                predict = dspy.Predict("q -> a", rollout_id=1, temperature=1.0)
                predict(q="What is 1 + 52?", config={"rollout_id": 2, "temperature": 1.0})
    """

    def __init__(self, signature: str | type[Signature], **config):
        super().__init__()
        self.stage = random.randbytes(8).hex()
        self.signature = ensure_signature(signature)
        self.config = config
        self.reset()

    def reset(self):
        self.lm = None
        self.traces = []
        self.train = []
        self.demos = []

    def dump_state(self, json_mode=True):
        state_keys = ["traces", "train"]
        state = {k: getattr(self, k) for k in state_keys}

        state["demos"] = []
        for demo in self.demos:
            demo = demo.copy()

            for field in demo:
                # FIXME: Saving BaseModels as strings in examples doesn't matter because you never re-access as an object
                demo[field] = serialize_object(demo[field])

            if isinstance(demo, dict) or not json_mode:
                state["demos"].append(demo)
            else:
                state["demos"].append(demo.toDict())

        state["signature"] = self.signature.dump_state()
        state["lm"] = self.lm.dump_state() if self.lm else None
        return state

    def _get_positional_args_error_message(self):
        input_fields = list(self.signature.input_fields.keys())
        return (
            "Positional arguments are not allowed when calling `dspy.Predict`, must use keyword arguments "
            f"that match your signature input fields: '{', '.join(input_fields)}'. For example: "
            f"`predict({input_fields[0]}=input_value, ...)`."
        )

    def __call__(self, *args, **kwargs):
        if args:
            raise ValueError(self._get_positional_args_error_message())

        return super().__call__(**kwargs)

    def _forward_preprocess(self, **kwargs):
        # Extract the three privileged keyword arguments.
        assert "new_signature" not in kwargs, "new_signature is no longer a valid keyword argument."
        signature = ensure_signature(kwargs.pop("signature", self.signature))
        demos = kwargs.pop("demos", self.demos)
        config = {**self.config, **kwargs.pop("config", {})}

        if "prediction" in kwargs:
            if (
                isinstance(kwargs["prediction"], dict)
                and kwargs["prediction"].get("type") == "content"
                and "content" in kwargs["prediction"]
            ):
                # If the `prediction` is the standard predicted outputs format
                # (https://platform.openai.com/docs/guides/predicted-outputs), we remove it from input kwargs and add it
                # to the lm kwargs.
                config["prediction"] = kwargs.pop("prediction")

        if not all(k in kwargs for k in signature.input_fields):
            present = [k for k in signature.input_fields if k in kwargs]
            missing = [k for k in signature.input_fields if k not in kwargs]
            logger.warning(
                "Not all input fields were provided to module. Present: %s. Missing: %s.",
                present,
                missing,
            )
        return config, signature, demos, kwargs

    def _forward_postprocess(self, completions, signature, usage, **kwargs):
        return Prediction.from_completions(completions, signature=signature, usage=usage)

    def forward(self, lm: 'LM', **kwargs):
        config, signature, demos, kwargs = self._forward_preprocess(**kwargs)

        adapter = JSONAdapter()

        completions, usage = adapter(lm, lm_kwargs=config, signature=signature, demos=demos, inputs=kwargs)

        return self._forward_postprocess(completions, signature, usage, **kwargs)

    def update_config(self, **kwargs):
        self.config = {**self.config, **kwargs}

    def get_config(self):
        return self.config

    def __repr__(self):
        return f"{self.__class__.__name__}({self.signature})"


def serialize_object(obj):
    """
    Recursively serialize a given object into a JSON-compatible format.
    Supports Pydantic models, lists, dicts, and primitive types.
    """
    if isinstance(obj, BaseModel):
        # Use model_dump with mode="json" to ensure all fields (including HttpUrl, datetime, etc.)
        # are converted to JSON-serializable types (strings)
        return obj.model_dump(mode="json")
    elif isinstance(obj, list):
        return [serialize_object(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(serialize_object(item) for item in obj)
    elif isinstance(obj, dict):
        return {key: serialize_object(value) for key, value in obj.items()}
    else:
        return obj


# # TODO: FIXME: Hmm, I guess expected behavior is that contexts can
# affect execution. Well, we need to determine whether context dominates, __init__ demoninates, or forward dominates.
# Generally, unless overwritten, we'd see n=None, temperature=None.
# That will eventually mean we have to learn them.
