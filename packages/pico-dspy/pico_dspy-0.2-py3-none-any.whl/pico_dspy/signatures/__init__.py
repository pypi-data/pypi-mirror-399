import wrapt

InputField = wrapt.lazy_import('dspy.signatures.field', 'InputField')
OutputField = wrapt.lazy_import('dspy.signatures.field', 'OutputField')
Signature = wrapt.lazy_import('dspy.signatures.signature', 'Signature')
SignatureMeta = wrapt.lazy_import('dspy.signatures.signature', 'SignatureMeta')

__all__ = [
    "InputField",
    "OutputField",
    "SignatureMeta",
    "Signature",
]
