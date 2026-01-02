# Copyright (c) 2025 Tylt LLC. All rights reserved.
# CONFIDENTIAL AND PROPRIETARY. Unauthorized use, copying, or distribution
# is strictly prohibited. For licensing inquiries: hello@claimhawk.app

"""Tool call parsing and validation using BAML-generated types.

This module provides type-safe parsing and validation of VLM tool calls
using Pydantic models.

Usage:
    from cudag.prompts.baml_parser import parse_tool_call, validate_computer_use

    # Parse from model output
    result = parse_tool_call("<tool_call>{...}</tool_call>")

    # Validate a computer_use call
    call = validate_computer_use({"name": "computer_use", "arguments": {...}})
"""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

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

__all__ = [
    # Types (re-exported)
    "Action",
    "TerminateStatus",
    "ComputerUseArgs",
    "ComputerUseCall",
    "GetBboxArgs",
    "GetBboxCall",
    "TextVerificationArgs",
    "TextVerificationCall",
    "VerificationRegion",
    # Functions
    "parse_tool_call",
    "parse_computer_use",
    "parse_get_bbox",
    "parse_text_verification",
    "validate_computer_use",
    "validate_get_bbox",
    "validate_text_verification",
    "to_dict",
    "format_tool_call",
    "ParseError",
    # Mappings
    "ACTION_MAP",
    "ACTION_MAP_REVERSE",
]

# Regex pattern for extracting tool calls from model output
TOOL_CALL_PATTERN = re.compile(
    r"<tool_call>\s*(?P<json>\{.*?\})\s*</tool_call>",
    re.DOTALL | re.IGNORECASE,
)

# Action name mapping: snake_case -> PascalCase enum
ACTION_MAP: dict[str, Action] = {
    "key": Action.Key,
    "type": Action.Type,
    "mouse_move": Action.MouseMove,
    "left_click": Action.LeftClick,
    "left_click_drag": Action.LeftClickDrag,
    "right_click": Action.RightClick,
    "middle_click": Action.MiddleClick,
    "double_click": Action.DoubleClick,
    "triple_click": Action.TripleClick,
    "scroll": Action.Scroll,
    "hscroll": Action.HScroll,
    "wait": Action.Wait,
    "terminate": Action.Terminate,
    "answer": Action.Answer,
}

# Reverse mapping for serialization: PascalCase enum -> snake_case
ACTION_MAP_REVERSE: dict[Action, str] = {v: k for k, v in ACTION_MAP.items()}

# Status mapping
STATUS_MAP: dict[str, TerminateStatus] = {
    "success": TerminateStatus.Success,
    "failure": TerminateStatus.Failure,
}


class ParseError(Exception):
    """Error parsing tool call from model output."""

    pass


def _normalize_action(action_str: str) -> Action:
    """Convert action string to Action enum."""
    action_lower = action_str.lower()
    if action_lower in ACTION_MAP:
        return ACTION_MAP[action_lower]
    # Try direct enum lookup
    try:
        return Action(action_str)
    except ValueError:
        raise ParseError(f"Invalid action: {action_str}")


def _normalize_status(status_str: str | None) -> TerminateStatus | None:
    """Convert status string to TerminateStatus enum."""
    if status_str is None:
        return None
    status_lower = status_str.lower()
    if status_lower in STATUS_MAP:
        return STATUS_MAP[status_lower]
    try:
        return TerminateStatus(status_str)
    except ValueError:
        raise ParseError(f"Invalid status: {status_str}")


def parse_tool_call(
    text: str,
) -> ComputerUseCall | GetBboxCall | TextVerificationCall | None:
    """Parse tool call from model output text.

    Extracts the JSON from <tool_call>...</tool_call> tags and validates
    against the appropriate schema.

    Args:
        text: Model output containing <tool_call>...</tool_call>

    Returns:
        Validated tool call object or None if not found

    Raises:
        ParseError: If tool call found but invalid
    """
    match = TOOL_CALL_PATTERN.search(text)
    if not match:
        return None

    try:
        data = json.loads(match.group("json"))
    except json.JSONDecodeError as e:
        raise ParseError(f"Invalid JSON in tool call: {e}")

    tool_name = data.get("name")

    if tool_name == "computer_use":
        return parse_computer_use(data)
    elif tool_name == "get_bbox":
        return parse_get_bbox(data)
    elif tool_name == "text_verification":
        return parse_text_verification(data)
    else:
        raise ParseError(f"Unknown tool name: {tool_name}")


def parse_computer_use(data: dict[str, Any]) -> ComputerUseCall:
    """Parse and validate a computer_use tool call from a dict.

    Handles snake_case action names and validates all arguments.

    Args:
        data: Dict with {"name": "computer_use", "arguments": {...}}

    Returns:
        Validated ComputerUseCall

    Raises:
        ParseError: If validation fails
    """
    if data.get("name") != "computer_use":
        raise ParseError(f"Expected computer_use, got: {data.get('name')}")

    args = data.get("arguments", {})

    # Normalize action
    action_str = args.get("action")
    if not action_str:
        raise ParseError("Missing action in computer_use arguments")

    try:
        action = _normalize_action(action_str)
        status = _normalize_status(args.get("status"))

        validated_args = ComputerUseArgs(
            action=action,
            coordinate=args.get("coordinate"),
            keys=args.get("keys"),
            text=args.get("text"),
            pixels=args.get("pixels"),
            time=args.get("time"),
            status=status,
        )

        return ComputerUseCall(name="computer_use", arguments=validated_args)

    except ValidationError as e:
        raise ParseError(f"Invalid computer_use arguments: {e}")


# Actions that require a coordinate
COORDINATE_ACTIONS = {
    Action.LeftClick,
    Action.RightClick,
    Action.MiddleClick,
    Action.DoubleClick,
    Action.TripleClick,
    Action.Scroll,
    Action.HScroll,
    Action.MouseMove,
    Action.LeftClickDrag,
}


def validate_computer_use(call: ComputerUseCall) -> list[str]:
    """Validate a ComputerUseCall and return a list of error strings.

    Checks semantic validity like required fields and coordinate ranges.

    Args:
        call: ComputerUseCall to validate

    Returns:
        List of error strings (empty if valid)
    """
    errors: list[str] = []
    args = call.arguments
    action = args.action

    # Check coordinate for actions that require it
    if action in COORDINATE_ACTIONS:
        if args.coordinate is None:
            errors.append(f"Action '{action.value}' requires coordinate")
        else:
            x, y = args.coordinate
            if not (0 <= x <= 1000):
                errors.append(f"X coordinate {x} out of range [0, 1000]")
            if not (0 <= y <= 1000):
                errors.append(f"Y coordinate {y} out of range [0, 1000]")

    # Check scroll requires pixels
    if action == Action.Scroll or action == Action.HScroll:
        if args.pixels is None:
            errors.append(f"Action 'scroll' requires 'pixels' field")

    # Check key requires keys
    if action == Action.Key:
        if args.keys is None or len(args.keys) == 0:
            errors.append("Action 'key' requires 'keys' field")

    # Check type requires text
    if action == Action.Type:
        if args.text is None:
            errors.append("Action 'type' requires 'text' field")

    # Check terminate requires status
    if action == Action.Terminate:
        if args.status is None:
            errors.append("Action 'terminate' requires 'status' field")

    return errors


def parse_get_bbox(data: dict[str, Any]) -> GetBboxCall:
    """Parse a get_bbox tool call from a dict.

    Args:
        data: Dict with {"name": "get_bbox", "arguments": {...}}

    Returns:
        Validated GetBboxCall

    Raises:
        ParseError: If validation fails
    """
    if data.get("name") != "get_bbox":
        raise ParseError(f"Expected get_bbox, got: {data.get('name')}")

    args = data.get("arguments", {})

    try:
        validated_args = GetBboxArgs(
            bbox_2d=args.get("bbox_2d", []),
            label=args.get("label"),
        )

        return GetBboxCall(name="get_bbox", arguments=validated_args)

    except ValidationError as e:
        raise ParseError(f"Invalid get_bbox arguments: {e}")


def validate_get_bbox(call: GetBboxCall) -> list[str]:
    """Validate a GetBboxCall and return a list of error strings.

    Args:
        call: GetBboxCall to validate

    Returns:
        List of error strings (empty if valid)
    """
    errors: list[str] = []
    args = call.arguments

    if args.bbox_2d is None or len(args.bbox_2d) != 4:
        errors.append("bbox_2d must be a list of 4 integers [x1, y1, x2, y2]")
    else:
        for i, coord in enumerate(args.bbox_2d):
            if not (0 <= coord <= 1000):
                errors.append(f"bbox_2d[{i}] = {coord} out of range [0, 1000]")

    return errors


def parse_text_verification(data: dict[str, Any]) -> TextVerificationCall:
    """Parse a text_verification tool call from a dict.

    Args:
        data: Dict with {"name": "text_verification", "arguments": {...}}

    Returns:
        Validated TextVerificationCall

    Raises:
        ParseError: If validation fails
    """
    if data.get("name") != "text_verification":
        raise ParseError(f"Expected text_verification, got: {data.get('name')}")

    args = data.get("arguments", {})

    try:
        regions_data = args.get("regions", [])
        regions = [
            VerificationRegion(bbox_2d=r.get("bbox_2d", []), label=r.get("label", ""))
            for r in regions_data
        ]

        validated_args = TextVerificationArgs(regions=regions)

        return TextVerificationCall(name="text_verification", arguments=validated_args)

    except ValidationError as e:
        raise ParseError(f"Invalid text_verification arguments: {e}")


def validate_text_verification(call: TextVerificationCall) -> list[str]:
    """Validate a TextVerificationCall and return a list of error strings.

    Args:
        call: TextVerificationCall to validate

    Returns:
        List of error strings (empty if valid)
    """
    errors: list[str] = []
    args = call.arguments

    if len(args.regions) != 2:
        errors.append(f"Expected exactly 2 regions, got {len(args.regions)}")

    for i, region in enumerate(args.regions):
        if region.bbox_2d is None or len(region.bbox_2d) != 4:
            errors.append(f"Region {i}: bbox_2d must be a list of 4 integers")
        if not region.label:
            errors.append(f"Region {i}: label is required")

    return errors


def to_dict(
    call: ComputerUseCall | GetBboxCall | TextVerificationCall,
) -> dict[str, Any]:
    """Convert a validated tool call back to dict for JSON serialization.

    Uses snake_case for actions to match the canonical format.

    Args:
        call: Validated tool call object

    Returns:
        Dict suitable for JSON serialization
    """
    if isinstance(call, ComputerUseCall):
        args = call.arguments
        result: dict[str, Any] = {
            "action": ACTION_MAP_REVERSE.get(args.action, args.action.value.lower())
        }

        if args.coordinate is not None:
            result["coordinate"] = args.coordinate
        if args.keys is not None:
            result["keys"] = args.keys
        if args.text is not None:
            result["text"] = args.text
        if args.pixels is not None:
            result["pixels"] = args.pixels
        if args.time is not None:
            result["time"] = args.time
        if args.status is not None:
            result["status"] = args.status.value.lower()

        return {"name": "computer_use", "arguments": result}

    elif isinstance(call, GetBboxCall):
        args = call.arguments
        result = {"bbox_2d": args.bbox_2d}
        if args.label is not None:
            result["label"] = args.label
        return {"name": "get_bbox", "arguments": result}

    elif isinstance(call, TextVerificationCall):
        args = call.arguments
        regions = [{"bbox_2d": r.bbox_2d, "label": r.label} for r in args.regions]
        return {"name": "text_verification", "arguments": {"regions": regions}}

    else:
        raise TypeError(f"Unknown tool call type: {type(call)}")


def format_tool_call(
    call: ComputerUseCall | GetBboxCall | TextVerificationCall | dict[str, Any],
) -> str:
    """Format tool call as XML-wrapped JSON string.

    Args:
        call: Validated tool call object or dict

    Returns:
        Formatted string like:
        <tool_call>
        {"name": "computer_use", "arguments": {...}}
        </tool_call>
    """
    if isinstance(call, dict):
        data = call
    else:
        data = to_dict(call)
    json_str = json.dumps(data)
    return f"<tool_call>\n{json_str}\n</tool_call>"
