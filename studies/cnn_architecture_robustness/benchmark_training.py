"""Benchmark Stage-F training throughput on CPU multiprocessing versus CUDA.

This is an implementation benchmark only. It does not inspect patching outcomes,
does not contribute inferential data, and writes to a separate benchmark root.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import multiprocessing as mp
import shutil
import sys
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(Path(__file__).resolve().parent))
import architecture_core as ac  # noqa: E402
import train_grid as tg  # noqa: E402


REPRESENTATIVE_ARCHS = (
    "tiny_gmp",
    "tiny_gap",
    "plain2_w16_gmp",
    "plain2_w16_gap",
    "plain4_w16_gmp",
    "plain4_w16_gap",
    "plain2_w64_gmp",
    "plain2_w64_gap",
    "plain4_w64_gmp",
    "plain4_w64_gap",
    "res4_w16_gmp",
    "res4_w16_gap",
    "bn2_w16_gmp",
    "bn2_w16_gap",
    "bn4_w16_gmp",
    "bn4_w16_gap",
)


def make_jobs(root: Path, device: str, workers: int, repeats: int):
    jobs = []
    # Fixed fresh benchmark namespace. These runs are never part of Stage-F inference.
    block = 6999
    task = "two_concepts"
    for rep in range(repeats):
        init_rep = 100 + rep
        for arch in REPRESENTATIVE_ARCHS:
            # One treatment is enough for raw throughput. Alternate treatment by
            # architecture index so both regularization schedules are represented.
            treatment = ac.TREATMENTS[ac.ARCHS.index(arch) % 2]
            jobs.append(
                {
                    "root": str(root),
                    "task": task,
                    "architecture": arch,
                    "block": block,
                    "init_rep": init_rep,
                    "treatment": treatment,
                    "epochs": 200,
                    "threads_per_worker": 1,
                    "device": device,
                }
            )
    return jobs


def run_cpu(jobs, workers):
    start = time.perf_counter()
    ctx = mp.get_context("spawn")
    with cf.ProcessPoolExecutor(max_workers=workers, mp_context=ctx) as ex:
        futures = [ex.submit(tg.train_one, job) for job in jobs]
        for i, fut in enumerate(cf.as_completed(futures), 1):
            fut.result()
            print(f"CPU [{i}/{len(jobs)}] complete", flush=True)
    return time.perf_counter() - start


def run_cuda(jobs):
    start = time.perf_counter()
    for i, job in enumerate(jobs, 1):
        tg.train_one(job)
        print(f"CUDA [{i}/{len(jobs)}] complete", flush=True)
    torch.cuda.synchronize()
    return time.perf_counter() - start


def summary(name, seconds, n):
    return {
        "mode": name,
        "models": n,
        "seconds": seconds,
        "seconds_per_model_effective": seconds / n,
        "models_per_hour": 3600.0 * n / seconds,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True)
    p.add_argument("--cpu-workers", type=int, default=12)
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--mode", choices=("both", "cpu", "cuda"), default="both")
    p.add_argument("--keep-checkpoints", action="store_true")
    args = p.parse_args()

    if args.cpu_workers < 1 or args.repeats < 1:
        p.error("cpu-workers and repeats must be positive")
    if args.mode in ("both", "cuda") and not torch.cuda.is_available():
        p.error("CUDA benchmark requested but CUDA is unavailable")

    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    results = []

    if args.mode in ("both", "cpu"):
        cpu_root = out / "cpu"
        shutil.rmtree(cpu_root, ignore_errors=True)
        cpu_root.mkdir(parents=True, exist_ok=True)
        ac.legacy_core.ROOT = cpu_root
        jobs = make_jobs(cpu_root, "cpu", args.cpu_workers, args.repeats)
        seconds = run_cpu(jobs, args.cpu_workers)
        results.append(summary(f"cpu_{args.cpu_workers}_workers", seconds, len(jobs)))

    if args.mode in ("both", "cuda"):
        cuda_root = out / "cuda"
        shutil.rmtree(cuda_root, ignore_errors=True)
        cuda_root.mkdir(parents=True, exist_ok=True)
        ac.legacy_core.ROOT = cuda_root
        jobs = make_jobs(cuda_root, "cuda", 1, args.repeats)
        seconds = run_cuda(jobs)
        results.append(summary("cuda_sequential", seconds, len(jobs)))

    payload = {
        "status": "implementation_benchmark_only",
        "epochs_per_model": 200,
        "architectures": list(REPRESENTATIVE_ARCHS),
        "repeats": args.repeats,
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "results": results,
    }
    (out / "benchmark.json").write_text(json.dumps(payload, indent=2) + "\n")
    print("\nTraining throughput benchmark")
    for r in results:
        print(
            f"{r['mode']}: {r['models_per_hour']:.2f} models/hour "
            f"({r['seconds_per_model_effective']:.2f} effective seconds/model)"
        )
    print("Benchmark JSON:", out / "benchmark.json")

    if not args.keep_checkpoints:
        shutil.rmtree(out / "cpu", ignore_errors=True)
        shutil.rmtree(out / "cuda", ignore_errors=True)


if __name__ == "__main__":
    main()
