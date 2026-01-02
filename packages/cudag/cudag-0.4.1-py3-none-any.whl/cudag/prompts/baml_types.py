# Copyright (c) 2025 Tylt LLC. All rights reserved.
# CONFIDENTIAL AND PROPRIETARY. Unauthorized use, copying, or distribution
# is strictly prohibited. For licensing inquiries: hello@claimhawk.app

"""BAML-generated Pydantic types for computer use tool calls.

This module contains type-safe models for VLM tool call validation.
Originally generated from BAML schemas in baml_src/computer_use.baml.
"""

from __future__ import annotations

import typing
import typing_extensions
from enum import Enum

from pydantic import BaseModel


class Action(str, Enum):
    """Valid actions for computer_use tool."""

    Key = "Key"
    Type = "Type"
    MouseMove = "MouseMove"
    LeftClick = "LeftClick"
    LeftClickDrag = "LeftClickDrag"
    RightClick = "RightClick"
    MiddleClick = "MiddleClick"
    DoubleClick = "DoubleClick"
    TripleClick = "TripleClick"
    Scroll = "Scroll"
    HScroll = "HScroll"
    Wait = "Wait"
    Terminate = "Terminate"
    Answer = "Answer"


class TerminateStatus(str, Enum):
    """Status for terminate action."""

    Success = "Success"
    Failure = "Failure"


class BoundingBox(BaseModel):
    """Bounding box coordinates in RU (0-1000)."""

    x1: int
    y1: int
    x2: int
    y2: int


class Coordinate(BaseModel):
    """Point coordinate in RU (0-1000)."""

    x: int
    y: int


class ComputerUseArgs(BaseModel):
    """Arguments for computer_use tool call."""

    action: Action
    coordinate: typing.Optional[typing.List[int]] = None
    keys: typing.Optional[typing.List[str]] = None
    text: typing.Optional[str] = None
    pixels: typing.Optional[int] = None
    time: typing.Optional[float] = None
    status: typing.Optional[TerminateStatus] = None


class ComputerUseCall(BaseModel):
    """A computer_use tool call."""

    name: typing_extensions.Literal["computer_use"]
    arguments: ComputerUseArgs


class GetBboxArgs(BaseModel):
    """Arguments for get_bbox tool call."""

    bbox_2d: typing.List[int]
    label: typing.Optional[str] = None


class GetBboxCall(BaseModel):
    """A get_bbox tool call for element grounding."""

    name: typing_extensions.Literal["get_bbox"]
    arguments: GetBboxArgs


class VerificationRegion(BaseModel):
    """A region for text verification."""

    bbox_2d: typing.List[int]
    label: str


class TextVerificationArgs(BaseModel):
    """Arguments for text_verification tool call."""

    regions: typing.List[VerificationRegion]


class TextVerificationCall(BaseModel):
    """A text_verification tool call."""

    name: typing_extensions.Literal["text_verification"]
    arguments: TextVerificationArgs
