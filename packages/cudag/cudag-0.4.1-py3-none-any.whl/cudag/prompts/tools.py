# Copyright (c) 2025 Tylt LLC. All rights reserved.
# CONFIDENTIAL AND PROPRIETARY. Unauthorized use, copying, or distribution
# is strictly prohibited. For licensing inquiries: hello@claimhawk.app

"""Computer use tool definition and tool_call formatting.

This module provides type-safe tool call creation and validation using
BAML-generated Pydantic models. All tool calls use the canonical format
for consistency across generators and inference.

Example:
    from cudag.prompts.tools import left_click, scroll, parse_tool_call

    # Create tool calls with factory functions
    call = left_click(500, 300)
    call = scroll(400, 200, pixels=-100)

    # Parse from model output
    result = parse_tool_call("<tool_call>{...}</tool_call>")
"""

from __future__ import annotations

from typing import Any

# Re-export BAML types and parser functions
from cudag.prompts.baml_types import (
    Action,
    ComputerUseArgs,
    ComputerUseCall,
    GetBboxArgs,
    GetBboxCall,
    TerminateStatus,
    TextVerificationArgs,
    TextVerificationCall,
    VerificationRegion,
)
from cudag.prompts.baml_parser import (
    ACTION_MAP,
    ACTION_MAP_REVERSE,
    COORDINATE_ACTIONS,
    ParseError,
    format_tool_call,
    parse_computer_use,
    parse_get_bbox,
    parse_text_verification,
    parse_tool_call,
    to_dict,
    validate_computer_use,
    validate_get_bbox,
    validate_text_verification,
)

__all__ = [
    # BAML Types
    "Action",
    "TerminateStatus",
    "ComputerUseArgs",
    "ComputerUseCall",
    "GetBboxArgs",
    "GetBboxCall",
    "TextVerificationArgs",
    "TextVerificationCall",
    "VerificationRegion",
    # Parser functions
    "parse_tool_call",
    "format_tool_call",
    "to_dict",
    "validate_computer_use",
    "validate_get_bbox",
    "validate_text_verification",
    "ParseError",
    # Factory functions
    "left_click",
    "double_click",
    "right_click",
    "middle_click",
    "triple_click",
    "scroll",
    "hscroll",
    "key_press",
    "type_text",
    "wait",
    "terminate",
    "mouse_move",
    "left_click_drag",
    "answer",
    "get_bbox",
    "text_verification",
    # Constants
    "TOOL_ACTIONS",
    "ACTION_DESCRIPTIONS",
    "COORDINATE_ACTIONS",
    "COMPUTER_USE_TOOL",
    "TEXT_VERIFICATION_TOOL",
    # Mappings
    "ACTION_MAP",
    "ACTION_MAP_REVERSE",
]

# Valid actions for computer_use tool (for backwards compat with Literal type)
TOOL_ACTIONS = [
    "key",
    "type",
    "mouse_move",
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "triple_click",
    "scroll",
    "hscroll",
    "wait",
    "terminate",
    "answer",
]

# Action descriptions for system prompt
ACTION_DESCRIPTIONS: dict[str, str] = {
    "key": "Press keys in order, release in reverse.",
    "type": "Type a string of text.",
    "mouse_move": "Move the cursor to (x, y).",
    "left_click": "Left click at (x, y).",
    "left_click_drag": "Click and drag from current to (x, y).",
    "right_click": "Right click at (x, y).",
    "middle_click": "Middle click at (x, y).",
    "double_click": "Double-click at (x, y).",
    "triple_click": "Triple-click at (x, y) (simulated as double-click).",
    "scroll": "Scroll the mouse wheel.",
    "hscroll": "Horizontal scroll.",
    "wait": "Wait N seconds.",
    "terminate": "End the task with a status.",
    "answer": "Answer a question.",
}

# Actions that require coordinate parameter
COORDINATE_ACTIONS: set[str] = {
    "mouse_move",
    "left_click",
    "left_click_drag",
    "right_click",
    "middle_click",
    "double_click",
    "triple_click",
    "scroll",
    "hscroll",
}

# Canonical computer_use tool definition (JSON schema)
COMPUTER_USE_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name_for_human": "computer_use",
        "name": "computer_use",
        "description": "Perform computer actions",
        "parameters": {
            "properties": {
                "action": {
                    "description": "\n".join(
                        f"* `{action}`: {desc}"
                        for action, desc in ACTION_DESCRIPTIONS.items()
                    ),
                    "enum": list(ACTION_DESCRIPTIONS.keys()),
                    "type": "string",
                },
                "keys": {
                    "description": "Required only by `action=key`.",
                    "type": "array",
                },
                "text": {
                    "description": "Required only by `action=type`.",
                    "type": "string",
                },
                "coordinate": {
                    "description": "Mouse coordinates (1000x1000 normalized).",
                    "type": "array",
                },
                "pixels": {
                    "description": "The amount of scrolling.",
                    "type": "number",
                },
                "time": {
                    "description": "The seconds to wait.",
                    "type": "number",
                },
                "status": {
                    "description": "The status of the task.",
                    "type": "string",
                    "enum": ["success", "failure"],
                },
            },
            "required": ["action"],
            "type": "object",
        },
        "args_format": "Format the arguments as a JSON object.",
    },
}

# Text verification tool definition (JSON schema)
TEXT_VERIFICATION_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name_for_human": "text_verification",
        "name": "text_verification",
        "description": "Request OCR verification of text in two screen regions",
        "parameters": {
            "properties": {
                "regions": {
                    "description": "Array of exactly 2 regions to compare",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "bbox_2d": {
                                "description": "Bounding box [x1, y1, x2, y2] in RU",
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 4,
                                "maxItems": 4,
                            },
                            "label": {
                                "description": "Human-readable label for the region",
                                "type": "string",
                            },
                        },
                        "required": ["bbox_2d", "label"],
                    },
                    "minItems": 2,
                    "maxItems": 2,
                },
            },
            "required": ["regions"],
            "type": "object",
        },
        "args_format": "Format the arguments as a JSON object.",
    },
}


# =============================================================================
# Factory Functions for ComputerUseCall
# =============================================================================


def left_click(x: int, y: int) -> ComputerUseCall:
    """Create a left_click tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.LeftClick, coordinate=[x, y]),
    )


def double_click(x: int, y: int) -> ComputerUseCall:
    """Create a double_click tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.DoubleClick, coordinate=[x, y]),
    )


def right_click(x: int, y: int) -> ComputerUseCall:
    """Create a right_click tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.RightClick, coordinate=[x, y]),
    )


def middle_click(x: int, y: int) -> ComputerUseCall:
    """Create a middle_click tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.MiddleClick, coordinate=[x, y]),
    )


def triple_click(x: int, y: int) -> ComputerUseCall:
    """Create a triple_click tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.TripleClick, coordinate=[x, y]),
    )


def scroll(x: int, y: int, pixels: int) -> ComputerUseCall:
    """Create a scroll tool call. Negative pixels = scroll up."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(
            action=Action.Scroll, coordinate=[x, y], pixels=pixels
        ),
    )


def hscroll(x: int, y: int, pixels: int) -> ComputerUseCall:
    """Create a horizontal scroll tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(
            action=Action.HScroll, coordinate=[x, y], pixels=pixels
        ),
    )


def key_press(keys: list[str]) -> ComputerUseCall:
    """Create a key press tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.Key, keys=keys),
    )


def type_text(text: str) -> ComputerUseCall:
    """Create a type tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.Type, text=text),
    )


def wait(seconds: float) -> ComputerUseCall:
    """Create a wait tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.Wait, time=seconds),
    )


def terminate(status: str = "success") -> ComputerUseCall:
    """Create a terminate tool call."""
    term_status = (
        TerminateStatus.Success if status == "success" else TerminateStatus.Failure
    )
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.Terminate, status=term_status),
    )


def mouse_move(x: int, y: int) -> ComputerUseCall:
    """Create a mouse_move tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.MouseMove, coordinate=[x, y]),
    )


def left_click_drag(x: int, y: int) -> ComputerUseCall:
    """Create a left_click_drag tool call."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.LeftClickDrag, coordinate=[x, y]),
    )


def answer(text: str) -> ComputerUseCall:
    """Create an answer tool call for responding to questions."""
    return ComputerUseCall(
        name="computer_use",
        arguments=ComputerUseArgs(action=Action.Answer, text=text),
    )


# =============================================================================
# Factory Functions for GetBboxCall
# =============================================================================


def get_bbox(
    bbox_2d: tuple[int, int, int, int] | list[int],
    label: str | None = None,
) -> GetBboxCall:
    """Create a get_bbox tool call for element grounding.

    Args:
        bbox_2d: Bounding box [x1, y1, x2, y2] in RU units (0-1000)
        label: Optional human-readable label of the element

    Returns:
        GetBboxCall instance
    """
    return GetBboxCall(
        name="get_bbox",
        arguments=GetBboxArgs(bbox_2d=list(bbox_2d), label=label),
    )


# =============================================================================
# Factory Functions for TextVerificationCall
# =============================================================================


def text_verification(
    region1: tuple[tuple[int, int, int, int] | list[int], str],
    region2: tuple[tuple[int, int, int, int] | list[int], str],
) -> TextVerificationCall:
    """Create a text verification call.

    Args:
        region1: (bbox_2d, label) for first region
        region2: (bbox_2d, label) for second region

    Returns:
        TextVerificationCall instance
    """
    regions = [
        VerificationRegion(bbox_2d=list(region1[0]), label=region1[1]),
        VerificationRegion(bbox_2d=list(region2[0]), label=region2[1]),
    ]
    return TextVerificationCall(
        name="text_verification",
        arguments=TextVerificationArgs(regions=regions),
    )
