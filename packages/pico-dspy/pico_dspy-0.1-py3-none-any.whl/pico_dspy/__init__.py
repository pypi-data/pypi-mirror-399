from typing import TYPE_CHECKING

import wrapt

if TYPE_CHECKING:
    from pico_dspy.adapters.base import Adapter
    from pico_dspy.adapters.chat_adapter import ChatAdapter
    from pico_dspy.adapters.json_adapter import JSONAdapter
    from pico_dspy.adapters.types.history import History
    from pico_dspy.clients.lm import LM
    from pico_dspy.predict.predict import Predict
    from pico_dspy.signatures.field import InputField, OutputField
    from pico_dspy.signatures.signature import Signature
else:
    LM = wrapt.lazy_import('pico_dspy.clients.lm', 'LM')
    Signature = wrapt.lazy_import('pico_dspy.signatures.signature', 'Signature')
    InputField = wrapt.lazy_import('pico_dspy.signatures.field', 'InputField')
    OutputField = wrapt.lazy_import('pico_dspy.signatures.field', 'OutputField')
    Adapter = wrapt.lazy_import('pico_dspy.adapters.base', 'Adapter')
    ChatAdapter = wrapt.lazy_import('pico_dspy.adapters.chat_adapter', 'ChatAdapter')
    JSONAdapter = wrapt.lazy_import('pico_dspy.adapters.json_adapter', 'JSONAdapter')
    Predict = wrapt.lazy_import('pico_dspy.predict.predict', 'Predict')
    History = wrapt.lazy_import('pico_dspy.adapters.types.history', 'History')
