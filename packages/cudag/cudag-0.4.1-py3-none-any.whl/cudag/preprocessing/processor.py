# Copyright (c) 2025 Tylt LLC. All rights reserved.
"""Dataset preprocessing for Qwen3-VL training.

This module provides functions to preprocess raw JSONL + images datasets
into tokenized .pt files ready for LoRA fine-tuning.
"""

from __future__ import annotations

import json
import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from transformers import AutoProcessor as ProcessorType

from .config import PreprocessConfig

# fmt: off
# ruff: noqa: E501
SYSTEM_PROMPT = """# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{
\t"type": "function",
\t"function": {
\t\t"name_for_human": "computer_use",
\t\t"name": "computer_use",
\t\t"description": "Perform computer actions",
\t\t"parameters": {
\t\t\t"properties": {
\t\t\t\t"action": {
\t\t\t\t\t"description": "* `key`: Press keys in order, release in reverse.\\n* `type`: Type a string of text.\\n* `mouse_move`: Move the cursor to (x, y).\\n* `left_click`: Left click at (x, y).\\n* `left_click_drag`: Click and drag from current to (x, y).\\n* `right_click`: Right click at (x, y).\\n* `middle_click`: Middle click at (x, y).\\n* `double_click`: Double-click at (x, y).\\n* `triple_click`: Triple-click at (x, y) (simulated as double-click).\\n* `scroll`: Scroll the mouse wheel.\\n* `hscroll`: Horizontal scroll.\\n* `wait`: Wait N seconds.\\n* `terminate`: End the task with a status.\\n* `answer`: Answer a question.",
\t\t\t\t\t"enum": ["key", "type", "mouse_move", "left_click", "left_click_drag", "right_click", "middle_click", "double_click", "scroll", "wait", "terminate"],
\t\t\t\t\t"type": "string"
\t\t\t\t},
\t\t\t\t"keys": {"description": "Required only by `action=key`.", "type": "array"},
\t\t\t\t"text": {"description": "Required only by `action=type`.", "type": "string"},
\t\t\t\t"coordinate": {"description": "Mouse coordinates (1000x1000 normalized).", "type": "array"},
\t\t\t\t"pixels": {"description": "The amount of scrolling.", "type": "number"},
\t\t\t\t"time": {"description": "The seconds to wait.", "type": "number"},
\t\t\t\t"status": {"description": "The status of the task.", "type": "string", "enum": ["success", "failure"]}
\t\t\t},
\t\t\t"required": ["action"],
\t\t\t"type": "object"
\t\t},
\t\t"args_format": "Format the arguments as a JSON object."
\t}
}
</tools>

For each function call, return a json object with function name and arguments within
<tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>

# Response format

Response format for every step:
1) Action: a short imperative describing what to do in the UI.
2) One or more <tool_call>...</tool_call> blocks, one per line, each containing only the JSON:
\t{"name": <function-name>, "arguments": <args-json-object>}.

Rules:
- Output exactly in the order: Action, <tool_call>(s).
- Be brief: one sentence for Action.
- Multiple tool calls can be output, one per line.
- Do not output anything else outside those parts.
- If finishing, use action=terminate in the tool call."""
# fmt: on


def is_modal_environment() -> bool:
    """Detect if running inside Modal."""
    return os.environ.get("MODAL_ENVIRONMENT") is not None


def get_dataset_root() -> Path:
    """Get the root path for datasets based on environment."""
    if is_modal_environment():
        return Path("/data/datasets")
    return Path.cwd() / "datasets"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSONL file into a list of dicts."""
    data = []
    with open(path) as f:
        for line in f:
            data.append(json.loads(line))
    return data


def preprocess_dataset(
    dataset_path: Path,
    config: PreprocessConfig | None = None,
) -> dict[str, int]:
    """Preprocess a dataset for Qwen3-VL training.

    This function:
    1. Loads train/val JSONL files
    2. Caches unique images for efficiency
    3. Tokenizes samples with the Qwen3-VL processor
    4. Saves preprocessed tensors as .pt files

    Args:
        dataset_path: Path to the dataset directory containing train.jsonl, val.jsonl, images/
        config: Preprocessing configuration. Uses defaults if None.

    Returns:
        Dict with counts: {"train": N, "val": M}
    """
    # Lazy imports to avoid requiring torch when not preprocessing
    import torch
    from PIL import Image
    from qwen_vl_utils import process_vision_info
    from tqdm import tqdm
    from transformers import AutoProcessor

    if config is None:
        config = PreprocessConfig()

    dataset_path = Path(dataset_path)
    preprocessed_path = dataset_path / "preprocessed"

    print(f"\n{'='*70}")
    print(f"CUDAG Preprocessing: {dataset_path.name}")
    print(f"{'='*70}\n")

    # Load processor
    print(f"Loading processor: {config.base_model}")
    processor: ProcessorType = AutoProcessor.from_pretrained(
        config.base_model, trust_remote_code=True
    )
    print("Processor loaded\n")

    # Load data for each split
    all_data: dict[str, list[dict[str, Any]]] = {}
    for split in config.splits:
        jsonl_path = dataset_path / f"{split}.jsonl"
        if jsonl_path.exists():
            all_data[split] = load_jsonl(jsonl_path)
            print(f"{split.capitalize()} samples: {len(all_data[split])}")
        else:
            print(f"Skipping {split} (no {split}.jsonl found)")

    if not all_data:
        raise FileNotFoundError(f"No JSONL files found in {dataset_path}")

    # Collect unique images
    unique_images: set[str] = set()
    for split_data in all_data.values():
        for sample in split_data:
            unique_images.add(sample["image"])

    print(f"\nCaching {len(unique_images)} unique images...")

    # Cache images in parallel
    image_cache: dict[str, dict[str, Any]] = {}

    def process_single_image(img_path: str) -> tuple[str, dict[str, Any] | None]:
        # Try relative to dataset first, then relative to cwd (for router datasets)
        full_path = dataset_path / img_path
        if not full_path.exists():
            full_path = Path.cwd() / img_path
        if not full_path.exists():
            full_path = Path(img_path)  # Try as absolute path
        if not full_path.exists():
            return (img_path, None)
        try:
            img = Image.open(full_path)
            image_inputs, _ = process_vision_info(
                [{"role": "user", "content": [{"type": "image", "image": f"file://{full_path}"}]}],
                image_patch_size=16,
            )
            return (img_path, {"pixel_values": image_inputs[0] if image_inputs else None, "image": img})
        except Exception as e:
            print(f"Warning: Failed to process {full_path}: {e}")
            return (img_path, None)

    num_workers = min(config.num_workers, multiprocessing.cpu_count())

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_single_image, p): p for p in sorted(unique_images)}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Caching images"):
            img_path, cached = future.result()
            if cached:
                image_cache[img_path] = cached

    print(f"Cached {len(image_cache)} images\n")

    # Prepare sample function
    # NOTE: System prompt is NOT included - it's added at training/inference time
    def prepare_sample(sample: dict[str, Any]) -> dict[str, Any]:
        img_path = sample["image"]
        if img_path not in image_cache:
            raise FileNotFoundError(f"Image not in cache: {img_path}")

        cached_image = image_cache[img_path]
        messages: list[dict[str, Any]] = []

        for msg in sample["conversations"]:
            if msg["from"] == "system":
                continue
            role = "user" if msg["from"] == "human" else "assistant"
            content_list = []
            value = msg["value"]
            if "<image>" in value:
                content_list.append({"type": "image"})
                text = value.replace("<image>", "").strip()
                if text:
                    content_list.append({"type": "text", "text": text})
            else:
                content_list.append({"type": "text", "text": value})
            messages.append({"role": role, "content": content_list})

        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        image_inputs = [cached_image["pixel_values"]] if cached_image["pixel_values"] is not None else None

        model_inputs = processor(
            text=[text],
            images=image_inputs,
            videos=None,
            return_tensors="pt",
            padding=False,
            do_resize=False,
        )

        input_ids = model_inputs["input_ids"][0]
        if not isinstance(input_ids, torch.Tensor):
            input_ids = torch.tensor(input_ids)
        attention_mask = model_inputs["attention_mask"][0]
        if not isinstance(attention_mask, torch.Tensor):
            attention_mask = torch.tensor(attention_mask)

        # Labels: only train on assistant responses
        labels = torch.full_like(input_ids, -100)
        input_ids_list = input_ids.tolist()
        pos = 0
        while pos < len(input_ids_list):
            if input_ids_list[pos] == 77091:  # <|im_start|>assistant
                ans_start = pos + 2
                ans_end = ans_start
                while ans_end < len(input_ids_list) and input_ids_list[ans_end] != 151645:
                    ans_end += 1
                if ans_end < len(input_ids_list):
                    labels[ans_start:ans_end + 2] = input_ids[ans_start:ans_end + 2]
                    pos = ans_end
            pos += 1

        result = {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}
        if "pixel_values" in model_inputs:
            result["pixel_values"] = model_inputs["pixel_values"]
            result["image_grid_thw"] = model_inputs["image_grid_thw"]
        return result

    def process_and_save(args: tuple[int, dict[str, Any], Path]) -> tuple[int, str | None, str | None]:
        idx, sample, out_dir = args
        try:
            processed = prepare_sample(sample)
            processed_cpu = {k: v.cpu() for k, v in processed.items()}
            sample_path = out_dir / f"sample_{idx:06d}.pt"
            torch.save(processed_cpu, sample_path)
            return (idx, str(sample_path), None)
        except Exception as e:
            return (idx, None, str(e))

    # Process each split
    results: dict[str, int] = {}

    for split, split_data in all_data.items():
        print(f"Processing {split} data...")
        out_dir = preprocessed_path / split
        out_dir.mkdir(parents=True, exist_ok=True)

        processed_paths: list[str] = []
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {
                executor.submit(process_and_save, (i, s, out_dir)): i
                for i, s in enumerate(split_data)
            }
            for future in tqdm(as_completed(futures), total=len(futures), desc=split.capitalize()):
                idx, path, error = future.result()
                if error:
                    raise RuntimeError(f"Failed sample {idx}: {error}")
                if path:
                    processed_paths.append(path)

        results[split] = len(processed_paths)
        print(f"  {split.capitalize()}: {len(processed_paths)} samples\n")

    # Save metadata
    metadata = {
        "model_name": config.base_model,
        "dataset_name": dataset_path.name,
        **{f"{k}_samples": v for k, v in results.items()},
    }
    with open(preprocessed_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    total_size = sum(f.stat().st_size for f in preprocessed_path.rglob("*.pt")) / (1024**3)
    print(f"Total preprocessed size: {total_size:.2f} GB")

    print(f"\n{'='*70}")
    print("PREPROCESSING COMPLETE")
    print(f"{'='*70}\n")

    return results
