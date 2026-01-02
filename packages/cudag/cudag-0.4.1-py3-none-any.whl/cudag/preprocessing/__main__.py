# Copyright (c) 2025 Tylt LLC. All rights reserved.
"""CLI entrypoint for preprocessing module.

Usage:
    python -m cudag.preprocessing --dataset datasets/my-dataset
    python -m cudag.preprocessing --dataset datasets/my-dataset --splits train val
"""

import argparse
from pathlib import Path

from .config import PreprocessConfig
from .processor import preprocess_dataset


def main() -> None:
    """Run preprocessing from command line."""
    parser = argparse.ArgumentParser(
        description="Preprocess a dataset for Qwen3-VL training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dataset",
        "-d",
        type=Path,
        required=True,
        help="Path to dataset directory containing train.jsonl, val.jsonl, images/",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["train", "val"],
        help="Which splits to preprocess (default: train val)",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=8,
        help="Number of parallel workers (default: 8)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen3-VL-8B-Instruct",
        help="Base model for processor (default: Qwen/Qwen3-VL-8B-Instruct)",
    )

    args = parser.parse_args()

    config = PreprocessConfig(
        base_model=args.model,
        num_workers=args.workers,
        splits=args.splits,
    )

    preprocess_dataset(args.dataset, config)


if __name__ == "__main__":
    main()
