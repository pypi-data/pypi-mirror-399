#!/usr/bin/env python3
# Copyright (c) 2025 Tylt LLC. All rights reserved.
# CONFIDENTIAL AND PROPRIETARY. Unauthorized use, copying, or distribution
# is strictly prohibited. For licensing inquiries: hello@claimhawk.app

"""
CUDAG Dataset Preprocessing on Modal

Thin wrapper around cudag.preprocessing that runs on Modal's CPU instances.
Preprocesses raw JSONL + images into tokenized .pt files for training.

Usage:
    modal run preprocess.py --dataset-name my-dataset
"""

import sys
from pathlib import Path

import modal

# =============================================================================
# CENTRALIZED CONFIGURATION
# =============================================================================
# Volume names and model info are loaded from config/adapters.yaml via the SDK.

try:
    from sdk.modal_compat import get_volume_name

    DEFAULT_VOLUME = get_volume_name("lora_training")
except ImportError:
    # Fallback when SDK not available
    DEFAULT_VOLUME = "claimhawk-lora-training"


def _get_generator_name() -> str:
    """Extract generator name from --dataset-name arg for dynamic app naming."""
    for i, arg in enumerate(sys.argv):
        if arg == "--dataset-name" and i + 1 < len(sys.argv):
            ds_name = sys.argv[i + 1]
            # Generator name is first part before dash (e.g., "desktop" from "desktop-mike-...")
            return ds_name.split("-")[0] if ds_name else "cudag"
    return "cudag"


# Modal App Setup - dynamically named based on generator
app = modal.App(f"{_get_generator_name()}-preprocess")

# Volume - matches modal-volumes.md structure
VOLUME = modal.Volume.from_name(DEFAULT_VOLUME, create_if_missing=True)

# Docker Image with Dependencies (CPU-only, no GPU needed)
# Install cudag from git main branch for latest preprocessing code
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "torch==2.4.0",
        "torchvision==0.19.0",
    )
    .pip_install(
        "transformers>=4.57.0",
        "qwen-vl-utils>=0.0.8",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "tqdm>=4.65.0",
    )
    .pip_install(
        "cudag @ git+https://github.com/claimhawk/cudag.git@main",
    )
)


@app.function(
    image=image,
    cpu=16,
    memory=32768,  # 32GB RAM
    timeout=7200,  # 2 hours max
    volumes={
        "/data": VOLUME,
    },
)
def preprocess_dataset_impl(dataset_name: str) -> dict[str, int]:
    """
    Preprocess the dataset on Modal CPU instance.

    Uses cudag.preprocessing module for the actual preprocessing logic.

    Reads from: /data/datasets/{dataset_name}/
    Writes to:  /data/datasets/{dataset_name}/preprocessed/
    """
    from cudag.preprocessing import PreprocessConfig, preprocess_dataset

    # Reload the mounted volume to see latest committed data
    VOLUME.reload()

    # Paths
    dataset_path = Path("/data/datasets") / dataset_name

    print(f"\n{'='*80}")
    print(f"Modal Preprocessing: {dataset_name}")
    print(f"{'='*80}\n")

    if not dataset_path.exists():
        print(f"Dataset not found: {dataset_path}")
        print("Available datasets:")
        datasets_dir = Path("/data/datasets")
        if datasets_dir.exists():
            for item in datasets_dir.iterdir():
                print(f"   - {item.name}")
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    # Run preprocessing
    config = PreprocessConfig(splits=["train", "val"])
    results = preprocess_dataset(dataset_path, config)

    # Commit volume changes
    VOLUME.commit()

    print(f"\nPreprocessed data saved to Modal volume: datasets/{dataset_name}/preprocessed/")

    return results


@app.local_entrypoint()
def main(dataset_name: str) -> None:
    """
    Local entrypoint for running preprocessing.

    Usage:
        modal run preprocess.py --dataset-name my-dataset
    """
    print(f"\n{'='*80}")
    print("Submitting preprocessing job to Modal...")
    print(f"Dataset: {dataset_name}")
    print(f"{'='*80}\n")

    result = preprocess_dataset_impl.remote(dataset_name)

    print(f"\n{'='*80}")
    print("Preprocessing job completed!")
    print(f"{'='*80}\n")
    print(f"Results: {result}")
