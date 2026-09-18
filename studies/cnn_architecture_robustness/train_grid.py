"""Train the frozen Stage-F architecture-robustness grid."""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import multiprocessing as mp
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(Path(__file__).resolve().parent))
import architecture_core as ac  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    os.replace(tmp, path)


def atomic_checkpoint(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    torch.save(value, tmp)
    os.replace(tmp, path)


def configure_determinism():
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    if hasattr(torch.backends, "cuda"):
        torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False


@torch.inference_mode()
def validation_metrics(model, data, device):
    model.eval()
    x = torch.from_numpy(data["val"]["x"]).to(device)
    y = torch.from_numpy(data["val"]["y"]).to(device)
    logits = model(x)
    return {
        "val_ce": float(F.cross_entropy(logits, y)),
        "val_acc": float((logits.argmax(1) == y).float().mean()),
    }


def cpu_state_dict(model):
    return {k: v.detach().cpu() for k, v in model.state_dict().items()}


def train_one(job: dict) -> dict:
    root = Path(job["root"]).resolve()
    task = job["task"]
    arch = job["architecture"]
    block = int(job["block"])
    init_rep = int(job["init_rep"])
    treatment = job["treatment"]
    epochs = int(job["epochs"])
    threads = int(job["threads_per_worker"])
    device_name = job["device"]

    torch.set_num_threads(threads)
    configure_determinism()
    device = torch.device(device_name)
    ac.legacy_core.ROOT = root

    out = (
        root
        / "runs"
        / task
        / arch
        / f"block{block:04d}"
        / f"init{init_rep:02d}"
        / treatment
    )
    complete = out / "complete.json"
    final_cp = out / f"epoch_{epochs:04d}.pt"
    if complete.exists() and final_cp.exists():
        return {
            "status": "skip",
            "task": task,
            "architecture": arch,
            "block": block,
            "init_rep": init_rep,
            "treatment": treatment,
        }

    data = ac.legacy_core.data_for(task, block)
    model, anchor = ac.setup_model(arch, block, task, init_rep)
    model.to(device)
    anchor = anchor.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
    shuffle = torch.Generator().manual_seed(ac.shuffle_seed(block, task, arch, init_rep))

    X = torch.from_numpy(data["train"]["x"])
    Y = torch.from_numpy(data["train"]["y"])

    start_all = time.perf_counter()
    last = {}
    for epoch in range(1, epochs + 1):
        model.train()
        order = torch.randperm(len(X), generator=shuffle)
        ce_sum = reg_sum = correct = grad_sum = 0.0
        batches = 0
        lam = ac.retention_strength(treatment, epoch)

        for st in range(0, len(X), 128):
            ix = order[st : st + 128]
            xb = X[ix].to(device)
            yb = Y[ix].to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(xb)
            ce = F.cross_entropy(logits, yb)
            reg = (model.conv.weight - anchor).square().sum() / anchor.square().sum()
            (ce + lam * reg).backward()
            grad_sum += float(model.conv.weight.grad.detach().norm())
            optimizer.step()

            ce_sum += float(ce.detach()) * len(ix)
            reg_sum += float(reg.detach()) * len(ix)
            correct += int((logits.detach().argmax(1) == yb).sum())
            batches += 1

        last = {
            "epoch": epoch,
            "lambda_retention": lam,
            "train_ce": ce_sum / len(X),
            "train_acc": correct / len(X),
            "retention_penalty": reg_sum / len(X),
            "conv_gradient_norm": grad_sum / batches,
        }

    val = validation_metrics(model, data, device)
    alignment = ac.legacy_core.alignment(
        model.conv.weight.detach().cpu().numpy(), ac.legacy_core.bank()
    )
    elapsed = time.perf_counter() - start_all

    state = {
        "epoch": epochs,
        "model": cpu_state_dict(model),
        "metadata": {
            "task": task,
            "architecture": arch,
            "block": block,
            "init_rep": init_rep,
            "treatment": treatment,
            "model_seed": ac.model_seed(block, task, arch, init_rep),
            "shuffle_seed": ac.shuffle_seed(block, task, arch, init_rep),
        },
    }
    atomic_checkpoint(final_cp, state)

    summary = {
        **state["metadata"],
        **last,
        **val,
        "alignment": alignment,
        "seconds": elapsed,
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "checkpoint_sha256": sha256(final_cp),
    }
    atomic_json(out / "summary.json", summary)
    atomic_json(complete, {"status": "complete", "epoch": epochs})

    return {"status": "done", **summary}


def build_jobs(args, root):
    return [
        {
            "root": str(root),
            "task": task,
            "architecture": arch,
            "block": block,
            "init_rep": init_rep,
            "treatment": treatment,
            "epochs": args.epochs,
            "threads_per_worker": args.threads_per_worker,
            "device": args.device,
        }
        for block in range(args.start_block, args.start_block + args.blocks)
        for init_rep in range(args.init_reps)
        for task in args.tasks
        for arch in args.architectures
        for treatment in args.treatments
    ]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", default="results/architecture_robustness_001/training")
    p.add_argument("--start-block", type=int, default=6000)
    p.add_argument("--blocks", type=int, default=100)
    p.add_argument("--init-reps", type=int, default=4)
    p.add_argument("--epochs", type=int, default=200)
    p.add_argument("--tasks", nargs="+", choices=ac.TASKS, default=list(ac.TASKS))
    p.add_argument("--architectures", nargs="+", choices=ac.ARCHS, default=list(ac.ARCHS))
    p.add_argument("--treatments", nargs="+", choices=ac.TREATMENTS, default=list(ac.TREATMENTS))
    p.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    p.add_argument("--workers", type=int, default=12)
    p.add_argument("--threads-per-worker", type=int, default=1)
    p.add_argument("--smoke", action="store_true")
    args = p.parse_args()

    if args.start_block < 6000:
        p.error("Stage-F blocks must start at 6000 or later.")
    if min(args.blocks, args.init_reps, args.epochs, args.workers, args.threads_per_worker) < 1:
        p.error("blocks/init-reps/epochs/workers/threads-per-worker must be positive.")
    if args.device == "cuda" and args.workers != 1:
        p.error("CUDA training uses one worker; use CPU multiprocessing for the full grid.")
    if args.device == "cuda" and not torch.cuda.is_available():
        p.error("CUDA requested but unavailable.")

    configure_determinism()
    root = Path(args.output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    ac.legacy_core.ROOT = root

    design = {
        "study": "cnn_architecture_robustness_stage_f",
        "protocol_status": "prospectively_frozen_fresh_sample",
        "start_block": args.start_block,
        "blocks": args.blocks,
        "init_reps": args.init_reps,
        "epochs": args.epochs,
        "tasks": args.tasks,
        "architectures": args.architectures,
        "architecture_specs": ac.architecture_manifest(),
        "treatments": args.treatments,
        "treatment_specs": {
            "retention_1": {"kind": "constant", "lambda": 1.0},
            "release_default": {"kind": "linear_release", "start": 10, "end": 80},
        },
        "lr": 0.003,
        "batch_size": 128,
        "master_seed": ac.MASTER,
        "paired_treatment_initialization": True,
        "device": args.device,
        "workers": args.workers,
        "threads_per_worker": args.threads_per_worker,
        "protocol_sha256": sha256(Path(__file__).with_name("PROTOCOL.md")),
        "architecture_core_sha256": sha256(Path(ac.__file__)),
        "trainer_sha256": sha256(Path(__file__)),
    }

    if args.smoke:
        design["smoke"] = True

    design_path = root / "design.json"
    if design_path.exists():
        if json.loads(design_path.read_text()) != design:
            raise SystemExit("Existing Stage-F training design differs. Use a new output root.")
    else:
        atomic_json(design_path, design)

    atomic_json(
        root / "environment.json",
        {
            "python": sys.version,
            "torch": torch.__version__,
            "numpy": np.__version__,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "cuda_available": torch.cuda.is_available(),
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        },
    )

    blocks = list(range(args.start_block, args.start_block + args.blocks))
    if args.smoke:
        blocks = blocks[:1]
        args.tasks = [args.tasks[0]]
        args.architectures = [args.architectures[0], args.architectures[1]]
        args.treatments = list(ac.TREATMENTS)
        args.init_reps = 1

    print("Pre-generating frozen Stage-F datasets...", flush=True)
    for block in blocks:
        for task in args.tasks:
            ac.legacy_core.data_for(task, block)

    jobs = build_jobs(args, root)
    if args.smoke:
        jobs = [j for j in jobs if j["block"] in blocks]

    print(
        f"Planned model jobs: {len(jobs)} | device={args.device} | "
        f"workers={args.workers} | threads/worker={args.threads_per_worker}",
        flush=True,
    )

    if args.workers == 1:
        for i, job in enumerate(jobs, 1):
            result = train_one(job)
            print(f"[{i}/{len(jobs)}] {result['status']} {job['task']} {job['architecture']} "
                  f"block={job['block']} init={job['init_rep']} {job['treatment']}", flush=True)
    else:
        ctx = mp.get_context("spawn")
        done = 0
        with cf.ProcessPoolExecutor(max_workers=args.workers, mp_context=ctx) as ex:
            future_to_job = {ex.submit(train_one, job): job for job in jobs}
            for fut in cf.as_completed(future_to_job):
                job = future_to_job[fut]
                try:
                    result = fut.result()
                except Exception as exc:
                    print("FAILED JOB:", job, flush=True)
                    raise RuntimeError(f"Stage-F training job failed: {job}") from exc
                done += 1
                print(
                    f"[{done}/{len(jobs)}] {result['status']} {job['task']} {job['architecture']} "
                    f"block={job['block']} init={job['init_rep']} {job['treatment']}",
                    flush=True,
                )

    completed = list((root / "runs").glob("*/*/block*/init*/*/complete.json"))
    expected = len(jobs)
    if len(completed) != expected:
        raise SystemExit(f"Incomplete Stage-F grid: {len(completed)} / {expected}")
    atomic_json(root / "GRID_COMPLETE.json", {"planned": expected, "complete": len(completed), "smoke": args.smoke})
    print("Stage-F training complete:", root, flush=True)


if __name__ == "__main__":
    main()
