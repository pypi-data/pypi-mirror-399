from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClassificationResult(_message.Message):
    __slots__ = ("label", "score")
    LABEL_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    label: str
    score: float
    def __init__(self, label: _Optional[str] = ..., score: _Optional[float] = ...) -> None: ...

class ClassifyRequest(_message.Message):
    __slots__ = ("text", "top_k")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TOP_K_FIELD_NUMBER: _ClassVar[int]
    text: str
    top_k: int
    def __init__(self, text: _Optional[str] = ..., top_k: _Optional[int] = ...) -> None: ...

class ClassifyResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ClassificationResult]
    def __init__(self, results: _Optional[_Iterable[_Union[ClassificationResult, _Mapping]]] = ...) -> None: ...
