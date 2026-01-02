"""
Combined LoRA + steering evaluation.

Loads an existing LoRA adapter, generates a steering vector on the LoRA model,
and evaluates LoRA+steering.
"""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path

import torch

from wisent.core.models.wisent_model import WisentModel
from wisent.core.trainers.steering_trainer import WisentSteeringTrainer
from wisent.core.steering_methods import get_steering_method
from wisent.core.activations.extraction_strategy import ExtractionStrategy
from wisent.core.contrastive_pairs.core.set import ContrastivePairSet
from wisent.core.contrastive_pairs.core.pair import ContrastivePair
from wisent.core.contrastive_pairs.core.response import PositiveResponse, NegativeResponse

from wisent.comparison.lora import apply_lora_to_model, remove_lora
from wisent.comparison.utils import (
    apply_steering_to_model,
    remove_steering,
    create_test_only_task,
    extract_accuracy,
    run_lm_eval_evaluation,
    run_ll_evaluation,
    generate_contrastive_pairs,
)


def evaluate_lora_with_steering(
    model_name: str,
    lora_path: str | Path,
    task: str,
    method: str = "caa",
    layers: str = "12",
    num_pairs: int = 50,
    steering_scale: float = 1.0,
    train_ratio: float = 0.8,
    device: str = "cuda:0",
    batch_size: int = 1,
    max_batch_size: int = 8,
    limit: int | None = None,
    output_dir: str | Path = None,
    extraction_strategy: str = "mc_balanced",
) -> dict:
    """
    Evaluate LoRA + steering.

    Generates steering vector ON the LoRA model, then evaluates.
    Only evaluates LoRA+steering (not base or LoRA-only).
    """
    lora_path = Path(lora_path)

    # Setup output directory
    if output_dir:
        output_dir = Path(output_dir)
        model_dir_name = model_name.replace("/", "_")
        output_dir = output_dir / model_dir_name
        output_dir.mkdir(parents=True, exist_ok=True)
        vectors_dir = output_dir / "steering_vectors"
        vectors_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(".")
        vectors_dir = Path(".")

    # Step 1: Load model
    print(f"\n{'='*60}")
    print(f"Loading model: {model_name}")
    print(f"{'='*60}")
    wisent_model = WisentModel(model_name=model_name, device=device)

    # Step 2: Apply LoRA
    print(f"\n{'='*60}")
    print(f"Applying LoRA adapter from: {lora_path}")
    print(f"{'='*60}")
    apply_lora_to_model(wisent_model, lora_path)

    # Step 3: Generate contrastive pairs
    print(f"\n{'='*60}")
    print(f"Generating {num_pairs} contrastive pairs from {task}")
    print(f"{'='*60}")
    pairs_data, pairs_file = generate_contrastive_pairs(task, num_pairs)

    # Convert to ContrastivePairSet
    pairs = []
    for p in pairs_data:
        pair = ContrastivePair(
            prompt=p["prompt"],
            positive_response=PositiveResponse(model_response=p["positive_response"]["model_response"]),
            negative_response=NegativeResponse(model_response=p["negative_response"]["model_response"]),
        )
        pairs.append(pair)
    pair_set = ContrastivePairSet(pairs=pairs)
    print(f"Created {len(pair_set)} contrastive pairs")

    # Step 4: Generate steering vector on LoRA model
    print(f"\n{'='*60}")
    print(f"Generating {method.upper()} steering vector on LoRA model")
    print(f"Layers: {layers}")
    print(f"{'='*60}")

    # Get steering method
    steering_method = get_steering_method(method, device=device)

    # Get extraction strategy
    strategy = ExtractionStrategy(extraction_strategy)

    # Create trainer and run
    trainer = WisentSteeringTrainer(
        model=wisent_model,
        pair_set=pair_set,
        steering_method=steering_method,
    )

    result = trainer.run(
        layers_spec=layers,
        strategy=strategy,
        accept_low_quality_vector=True,
    )

    # Convert to our format
    steering_vectors = {}
    for layer_name, tensor in result.steered_vectors.to_dict().items():
        if tensor is not None:
            steering_vectors[layer_name] = tensor.cpu().float().tolist()

    steering_data = {
        "steering_vectors": steering_vectors,
        "layers": list(steering_vectors.keys()),
        "model": model_name,
        "method": method,
        "task": task,
        "num_pairs": len(pairs),
        "generated_on": "lora_model",
    }

    # Save steering vector
    vector_path = vectors_dir / f"{task}_{method}_on_lora_steering_vector.json"
    with open(vector_path, "w") as f:
        json.dump(steering_data, f, indent=2)
    print(f"Saved steering vector to {vector_path}")

    # Cleanup temp file
    import os
    os.unlink(pairs_file)

    # Step 5: Apply steering
    print(f"\n{'='*60}")
    print(f"Applying {method.upper()} steering (scale={steering_scale})")
    print(f"{'='*60}")
    apply_steering_to_model(wisent_model, steering_data, scale=steering_scale)

    # Step 6: Create test task and evaluate
    print(f"\n{'='*60}")
    print(f"Creating test task for: {task}")
    print(f"{'='*60}")
    task_dict = create_test_only_task(task, train_ratio=train_ratio)

    print(f"\n{'='*60}")
    print(f"Running LORA+{method.upper()} evaluation")
    print(f"{'='*60}")

    lora_steer_results = run_lm_eval_evaluation(wisent_model, task_dict, task, batch_size, max_batch_size, limit)
    lora_steer_acc_lm_eval = extract_accuracy(lora_steer_results, task)
    print(f"LoRA+{method.upper()} accuracy (lm-eval): {lora_steer_acc_lm_eval:.4f}")

    lora_steer_acc_ll = run_ll_evaluation(wisent_model, task_dict, task, limit)
    print(f"LoRA+{method.upper()} accuracy (LL): {lora_steer_acc_ll:.4f}")

    # Cleanup
    remove_steering(wisent_model)
    remove_lora(wisent_model)
    del wisent_model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Results
    results = {
        "task": task,
        "model": model_name,
        "method": method,
        "lora_path": str(lora_path),
        "steering_vector_path": str(vector_path),
        "steering_layers": list(steering_vectors.keys()),
        "steering_scale": steering_scale,
        "num_pairs": num_pairs,
        "train_ratio": train_ratio,
        "generated_on": "lora_model",
        "lora_steer_accuracy_lm_eval": lora_steer_acc_lm_eval,
        "lora_steer_accuracy_ll": lora_steer_acc_ll,
    }

    # Print summary
    print(f"\n{'='*70}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"Task: {task}")
    print(f"Model: {model_name}")
    print(f"LoRA: {lora_path}")
    print(f"Steering: {method.upper()} (layers={list(steering_vectors.keys())}, scale={steering_scale})")
    print(f"Generated on: LoRA model")
    print(f"{'-'*70}")
    print(f"{'lm-eval accuracy':<25} {lora_steer_acc_lm_eval:.4f}")
    print(f"{'LL accuracy':<25} {lora_steer_acc_ll:.4f}")
    print(f"{'='*70}")

    # Save results
    if output_dir:
        results_file = output_dir / f"{task}_lora_{method}_eval_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {results_file}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate LoRA + steering (generated on LoRA model)")
    parser.add_argument("--model", required=True, help="HuggingFace model name")
    parser.add_argument("--lora-path", required=True, help="Path to trained LoRA adapter")
    parser.add_argument("--task", default="boolq", help="lm-eval task name")
    parser.add_argument("--method", default="caa", choices=["caa"], help="Steering method")
    parser.add_argument("--layers", default="12", help="Layers for steering vector")
    parser.add_argument("--num-pairs", type=int, default=50, help="Number of pairs for steering generation")
    parser.add_argument("--steering-scale", type=float, default=1.0, help="Steering scale")
    parser.add_argument("--device", default="cuda:0", help="Device")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="Train/test split ratio")
    parser.add_argument("--batch-size", type=int, default=1, help="Eval batch size")
    parser.add_argument("--max-batch-size", type=int, default=8, help="Max batch size")
    parser.add_argument("--limit", type=int, default=None, help="Limit eval examples")
    parser.add_argument("--output-dir", default="./steering_lora_results", help="Output directory")
    parser.add_argument("--extraction-strategy", default="mc_balanced", help="Extraction strategy")

    args = parser.parse_args()

    evaluate_lora_with_steering(
        model_name=args.model,
        lora_path=args.lora_path,
        task=args.task,
        method=args.method,
        layers=args.layers,
        num_pairs=args.num_pairs,
        steering_scale=args.steering_scale,
        train_ratio=args.train_ratio,
        device=args.device,
        batch_size=args.batch_size,
        max_batch_size=args.max_batch_size,
        limit=args.limit,
        output_dir=args.output_dir,
        extraction_strategy=args.extraction_strategy,
    )


if __name__ == "__main__":
    main()
