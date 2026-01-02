# Copyright (c) 2025 Tylt LLC. All rights reserved.
# CONFIDENTIAL AND PROPRIETARY. Unauthorized use, copying, or distribution
# is strictly prohibited. For licensing inquiries: hello@claimhawk.app

"""System prompts and tool definitions for computer use training.

This module provides type-safe tool call creation using BAML-generated
Pydantic models.

Example:
    from cudag.prompts import left_click, scroll, format_tool_call

    call = left_click(500, 300)
    output = format_tool_call(call)
"""

from cudag.prompts.system import (
    CUA_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    get_system_prompt,
)
from cudag.prompts.tools import (
    # BAML Types
    Action,
    ComputerUseArgs,
    ComputerUseCall,
    GetBboxArgs,
    GetBboxCall,
    TerminateStatus,
    TextVerificationArgs,
    TextVerificationCall,
    VerificationRegion,
    # Parser functions
    ParseError,
    format_tool_call,
    parse_tool_call,
    to_dict,
    validate_computer_use,
    validate_get_bbox,
    validate_text_verification,
    # Factory functions
    double_click,
    get_bbox,
    hscroll,
    key_press,
    left_click,
    left_click_drag,
    middle_click,
    mouse_move,
    right_click,
    scroll,
    terminate,
    text_verification,
    triple_click,
    type_text,
    wait,
    # Constants
    ACTION_DESCRIPTIONS,
    ACTION_MAP,
    ACTION_MAP_REVERSE,
    COMPUTER_USE_TOOL,
    COORDINATE_ACTIONS,
    TEXT_VERIFICATION_TOOL,
    TOOL_ACTIONS,
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
    "get_bbox",
    "text_verification",
    # Constants
    "TOOL_ACTIONS",
    "ACTION_DESCRIPTIONS",
    "COORDINATE_ACTIONS",
    "COMPUTER_USE_TOOL",
    "TEXT_VERIFICATION_TOOL",
    "ACTION_MAP",
    "ACTION_MAP_REVERSE",
    # System prompts
    "CUA_SYSTEM_PROMPT",
    "SYSTEM_PROMPT",
    "get_system_prompt",
]
