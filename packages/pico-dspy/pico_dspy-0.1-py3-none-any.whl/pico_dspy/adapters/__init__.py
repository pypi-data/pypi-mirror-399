import wrapt

Adapter = wrapt.lazy_import('pico_dspy.adapters.base', 'Adapter')
ChatAdapter = wrapt.lazy_import('pico_dspy.adapters.chat_adapter', 'ChatAdapter')
JSONAdapter = wrapt.lazy_import('pico_dspy.adapters.json_adapter', 'JSONAdapter')

History = wrapt.lazy_import('pico_dspy.adapters.types.history', 'History')
Type = wrapt.lazy_import('pico_dspy.adapters.types.base_type', 'Type')

__all__ = [
    "Adapter",
    "ChatAdapter",
    "JSONAdapter",
    "History",
    "Type",
]
