from typing import Any


class BaseLM:
    """Base class for handling LLM calls.

    Most users can directly use the `dspy.LM` class, which is a subclass of `BaseLM`. Users can also implement their
    own subclasses of `BaseLM` to support custom LLM providers and inject custom logic. To do so, simply override the
    `forward` method and make sure the return format is identical to the
    [OpenAI response format](https://platform.openai.com/docs/api-reference/responses/object).

    Example:

    ```python
    from openai import OpenAI

    import dspy


    class MyLM(dspy.BaseLM):
        def forward(self, prompt, messages=None, **kwargs):
            client = OpenAI()
            return client.chat.completions.create(
                model=self.model,
                messages=messages or [{"role": "user", "content": prompt}],
                **self.kwargs,
            )


    lm = MyLM(model="gpt-4o-mini")
    dspy.configure(lm=lm)
    print(dspy.Predict("q->a")(q="Why did the chicken cross the kitchen?"))
    ```
    """

    def __init__(self, model, model_type="chat", temperature=0.0, max_tokens=1000, cache=True, **kwargs):
        self.model = model
        self.model_type = model_type
        self.cache = cache
        self.kwargs = dict(temperature=temperature, max_tokens=max_tokens, **kwargs)

    def _process_lm_response(self, response, prompt, messages, **kwargs):
        raise NotImplementedError

    def __call__(
        self, prompt: str | None = None, messages: list[dict[str, Any]] | None = None, **kwargs
    ) -> tuple[list[dict[str, Any] | str], dict]:
        response = self.forward(prompt=prompt, messages=messages, **kwargs)
        return self._process_lm_response(response, prompt, messages, **kwargs)

    def forward(self, prompt: str | None = None, messages: list[dict[str, Any]] | None = None, **kwargs):
        """Forward pass for the language model.

        Subclasses must implement this method, and the response should be identical to either of the following formats:
        - [OpenAI response format](https://platform.openai.com/docs/api-reference/responses/object)
        - [OpenAI chat completion format](https://platform.openai.com/docs/api-reference/chat/object)
        - [OpenAI text completion format](https://platform.openai.com/docs/api-reference/completions/object)
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def copy(self, **kwargs):
        """Returns a copy of the language model with possibly updated parameters.

        Any provided keyword arguments update the corresponding attributes or LM kwargs of
        the copy. For example, ``lm.copy(rollout_id=1, temperature=1.0)`` returns an LM whose
        requests use a different rollout ID at non-zero temperature to bypass cache collisions.
        """

        import copy

        new_instance = copy.deepcopy(self)

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(new_instance, key, value)
            if (key in self.kwargs) or (not hasattr(self, key)):
                if value is None:
                    new_instance.kwargs.pop(key, None)
                else:
                    new_instance.kwargs[key] = value

        return new_instance
