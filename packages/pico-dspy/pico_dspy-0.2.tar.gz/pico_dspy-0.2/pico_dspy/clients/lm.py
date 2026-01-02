import logging
from dataclasses import asdict
from typing import Any


class LM:
    def __init__(self, model: str, temperature=0.0, max_tokens=1000, **kwargs):
        model = model.replace('/', ':', 1)
        model = model.replace('gemini:', 'google-gla:')
        self.model = model
        self.kwargs = dict(temperature=temperature, max_tokens=max_tokens, **kwargs)

    def __call__(
        self, prompt: str | None = None, messages: list[dict[str, Any]] | None = None, **kwargs
    ) -> tuple[list[dict[str, Any] | str], dict]:
        return self.forward(prompt=prompt, messages=messages, **kwargs)

    def forward(self, prompt=None, messages=None, **kwargs):
        from pydantic_ai import (
            ModelRequest,
            ModelResponse,
            ModelSettings,
            TextPart,
        )
        from pydantic_ai.direct import model_request_sync
        from pydantic_ai.messages import SystemPromptPart, UserPromptPart

        messages = messages or [{"role": "user", "content": prompt}]

        pydantic_messages: list[ModelRequest | ModelResponse] = []
        for message in messages:
            match message['role']:
                case 'user':
                    pydantic_messages.append(ModelRequest(parts=[UserPromptPart(content=message['content'])]))
                case 'system':
                    pydantic_messages.append(ModelRequest(parts=[SystemPromptPart(content=message['content'])]))
                case 'assistant':
                    pydantic_messages.append(ModelResponse(parts=[TextPart(content=message['content'])]))
                case '_':
                    raise AssertionError(f'invalid role: {message["role"]}')

        merged_kwargs = {**self.kwargs, **kwargs}
        model_kwargs = {}
        if 'temperature' in merged_kwargs:
            model_kwargs['temperature'] = merged_kwargs['temperature']
        if 'max_tokens' in merged_kwargs:
            model_kwargs['max_tokens'] = merged_kwargs['max_tokens']
        model_settings = ModelSettings(**model_kwargs)  # type: ignore

        results = model_request_sync(self.model, pydantic_messages, model_settings=model_settings)

        self._check_truncation(results)

        usage = asdict(results.usage) | {'total_tokens': results.usage.total_tokens}
        return [p.content for p in results.parts if p.part_kind == 'text'], usage

    def _check_truncation(self, results):
        if results.finish_reason == "length":
            logging.warning(
                f"LM response was truncated due to exceeding max_tokens={self.kwargs['max_tokens']}. "
                "You can inspect the latest LM interactions with `dspy.inspect_history()`. "
                "To avoid truncation, consider passing a larger max_tokens when setting up dspy.LM. "
                f"You may also consider increasing the temperature (currently {self.kwargs['temperature']}) "
                " if the reason for truncation is repetition."
            )
