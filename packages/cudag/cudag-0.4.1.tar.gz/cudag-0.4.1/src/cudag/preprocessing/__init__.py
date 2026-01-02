# Copyright (c) 2025 Tylt LLC. All rights reserved.
"""CUDAG Preprocessing Module.

This module provides functions to preprocess raw JSONL + images datasets
into tokenized .pt files ready for Qwen3-VL LoRA fine-tuning.

Example:
    from cudag.preprocessing import preprocess_dataset, PreprocessConfig

    config = PreprocessConfig(splits=["train", "val"])
    preprocess_dataset(Path("datasets/my-dataset"), config)
"""

from .config import PreprocessConfig
from .processor import (
    SYSTEM_PROMPT,
    get_dataset_root,
    is_modal_environment,
    load_jsonl,
    preprocess_dataset,
)

__all__ = [
    "PreprocessConfig",
    "SYSTEM_PROMPT",
    "get_dataset_root",
    "is_modal_environment",
    "load_jsonl",
    "preprocess_dataset",
]
