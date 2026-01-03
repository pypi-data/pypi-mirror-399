from __future__ import annotations

from typing import Any, Dict, List, TypedDict, Union

from typing_extensions import Literal, NotRequired, Required

AppInputValue = Union[str, int, bool]
AppCellValue = Union[str, int, bool, None]
ExtractType = Literal["url", "text"]
JsonSchema = Dict[str, Any]
ExtractSchema = Union[JsonSchema, Any]


class AppInput(TypedDict):
    key: str
    value: AppInputValue


class RunAppRequest(TypedDict):
    appId: str
    inputs: List[AppInput]


RunAppJsonRequest = RunAppRequest
RunAppTableRequest = RunAppRequest
AppJsonRow = Dict[str, AppCellValue]


class RunAppJsonResponse(TypedDict, total=False):
    success: Required[bool]
    data: NotRequired[List[AppJsonRow]]
    runId: NotRequired[str]
    elapsedTime: NotRequired[int]
    error: NotRequired[str]


class RunAppTableData(TypedDict):
    columns: List[str]
    tableData: List[List[AppCellValue]]


class RunAppTableResponse(TypedDict, total=False):
    success: Required[bool]
    data: NotRequired[RunAppTableData]
    runId: NotRequired[str]
    elapsedTime: NotRequired[int]
    error: NotRequired[str]


class GetCreditsData(TypedDict):
    credits: int


class GetCreditsResponse(TypedDict, total=False):
    success: Required[bool]
    data: NotRequired[GetCreditsData]
    error: NotRequired[str]


class ExtractRequest(TypedDict, total=False):
    type: Required[ExtractType]
    data: Required[List[str]]
    prompt: NotRequired[str]
    schema: NotRequired[ExtractSchema]


class ExtractResponse(TypedDict, total=False):
    success: Required[bool]
    data: NotRequired[Any]
