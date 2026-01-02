import logging
from typing import TYPE_CHECKING

from pico_dspy.adapters.json_adapter import JSONAdapter
from pico_dspy.primitives.prediction import Prediction
from pico_dspy.signatures.signature import Signature

if TYPE_CHECKING:
    from pico_dspy.clients.lm import LM

logger = logging.getLogger(__name__)


class Predict:
    """Basic DSPy module that maps inputs to outputs using a language model.

    Args:
        signature: The input/output signature describing the task.
        **config: Default keyword arguments forwarded to the underlying
            language model. These values can be overridden for a single
            invocation by passing a ``config`` dictionary when calling the
            module. For example::

                predict = dspy.Predict("q -> a", rollout_id=1, temperature=1.0)
                predict(q="What is 1 + 52?", config={"rollout_id": 2, "temperature": 1.0})
    """

    def __init__(self, signature: type[Signature], **config):
        self.signature = signature
        self.config = config

    def __call__(self, /, **kwargs):
        return self.forward(**kwargs)

    def _forward_preprocess(self, **kwargs):
        kwargs.pop("signature", None)
        demos = kwargs.pop("demos", [])
        config = {**self.config, **kwargs.pop("config", {})}

        if not all(k in kwargs for k in self.signature.input_fields):
            present = [k for k in self.signature.input_fields if k in kwargs]
            missing = [k for k in self.signature.input_fields if k not in kwargs]
            logger.warning(
                "Not all input fields were provided to module. Present: %s. Missing: %s.",
                present,
                missing,
            )
        return config, self.signature, demos, kwargs

    def forward(self, lm: 'LM', **kwargs):
        config, signature, demos, kwargs = self._forward_preprocess(**kwargs)

        adapter = JSONAdapter()
        completions, usage = adapter(lm, lm_kwargs=config, signature=signature, demos=demos, inputs=kwargs)

        return Prediction.from_completions(completions, usage=usage)
