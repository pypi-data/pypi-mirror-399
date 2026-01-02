import wrapt

InputField = wrapt.lazy_import('dspy.signatures.field', 'InputField')
OldField = wrapt.lazy_import('dspy.signatures.field', 'OldField')
OldInputField = wrapt.lazy_import('dspy.signatures.field', 'OldInputField')
OldOutputField = wrapt.lazy_import('dspy.signatures.field', 'OldOutputField')
OutputField = wrapt.lazy_import('dspy.signatures.field', 'OutputField')
Signature = wrapt.lazy_import('dspy.signatures.signature', 'Signature')
SignatureMeta = wrapt.lazy_import('dspy.signatures.signature', 'SignatureMeta')
ensure_signature = wrapt.lazy_import('dspy.signatures.signature', 'ensure_signature')
infer_prefix = wrapt.lazy_import('dspy.signatures.signature', 'infer_prefix')
make_signature = wrapt.lazy_import('dspy.signatures.signature', 'make_signature')

__all__ = [
    "InputField",
    "OutputField",
    "OldField",
    "OldInputField",
    "OldOutputField",
    "SignatureMeta",
    "Signature",
    "infer_prefix",
    "ensure_signature",
    "make_signature",
]
