# Copyright (c) 2025 Tylt LLC. All rights reserved.
"""Preprocessing configuration."""

from dataclasses import dataclass, field


@dataclass
class PreprocessConfig:
    """Configuration for dataset preprocessing.

    Attributes:
        base_model: HuggingFace model name for the processor.
        num_workers: Number of parallel workers for processing.
        splits: Which dataset splits to preprocess (train, val).
    """

    base_model: str = "Qwen/Qwen3-VL-8B-Instruct"
    num_workers: int = 8
    splits: list[str] = field(default_factory=lambda: ["train", "val"])
