"""Frozen Stage-F architecture definitions and paired seed namespaces."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "studies" / "cnn_release_experiment"))
import core as legacy_core  # noqa: E402


@dataclass(frozen=True)
class ArchSpec:
    total_depth: int
    width: int
    pooling: str
    connectivity: str = "plain"
    batchnorm: bool = False


ARCH_SPECS = {
    "tiny_gmp": ArchSpec(1, 16, "max", "none", False),
    "tiny_gap": ArchSpec(1, 16, "avg", "none", False),
    "plain2_w16_gmp": ArchSpec(2, 16, "max"),
    "plain2_w16_gap": ArchSpec(2, 16, "avg"),
    "plain4_w16_gmp": ArchSpec(4, 16, "max"),
    "plain4_w16_gap": ArchSpec(4, 16, "avg"),
    "plain2_w64_gmp": ArchSpec(2, 64, "max"),
    "plain2_w64_gap": ArchSpec(2, 64, "avg"),
    "plain4_w64_gmp": ArchSpec(4, 64, "max"),
    "plain4_w64_gap": ArchSpec(4, 64, "avg"),
    "res4_w16_gmp": ArchSpec(4, 16, "max", "residual", False),
    "res4_w16_gap": ArchSpec(4, 16, "avg", "residual", False),
    "bn2_w16_gmp": ArchSpec(2, 16, "max", "plain", True),
    "bn2_w16_gap": ArchSpec(2, 16, "avg", "plain", True),
    "bn4_w16_gmp": ArchSpec(4, 16, "max", "plain", True),
    "bn4_w16_gap": ArchSpec(4, 16, "avg", "plain", True),
}
ARCHS = tuple(ARCH_SPECS)
TASKS = tuple(legacy_core.TASKS)
TREATMENTS = ("retention_1", "release_default")
MASTER = legacy_core.MASTER


def _seed(namespace: int, block: int, task: str, arch: str, init_rep: int) -> int:
    return int(
        np.random.SeedSequence(
            [
                MASTER,
                namespace,
                int(block),
                TASKS.index(task),
                ARCHS.index(arch),
                int(init_rep),
            ]
        ).generate_state(1)[0]
    )


def model_seed(block: int, task: str, arch: str, init_rep: int) -> int:
    return _seed(60, block, task, arch, init_rep)


def shuffle_seed(block: int, task: str, arch: str, init_rep: int) -> int:
    return _seed(61, block, task, arch, init_rep)


def control_rng(block: int, task: str, arch: str, init_rep: int):
    return np.random.default_rng(
        np.random.SeedSequence(
            [MASTER, 62, int(block), TASKS.index(task), ARCHS.index(arch), int(init_rep)]
        )
    )


class ArchitectureNet(nn.Module):
    def __init__(self, arch: str):
        super().__init__()
        if arch not in ARCH_SPECS:
            raise ValueError(f"Unknown Stage-F architecture: {arch}")
        self.arch = arch
        self.spec = ARCH_SPECS[arch]

        self.conv = nn.Conv2d(1, 16, 9, padding=4, bias=False)

        if self.spec.total_depth == 1:
            self.down_convs = nn.ModuleList()
            self.down_bns = nn.ModuleList()
            out_width = 16
        else:
            n_down = self.spec.total_depth - 1
            convs = []
            bns = []
            in_ch = 16
            for _ in range(n_down):
                out_ch = self.spec.width
                convs.append(nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=not self.spec.batchnorm))
                if self.spec.batchnorm:
                    bns.append(nn.BatchNorm2d(out_ch))
                in_ch = out_ch
            self.down_convs = nn.ModuleList(convs)
            self.down_bns = nn.ModuleList(bns)
            out_width = self.spec.width

        if self.spec.connectivity == "residual":
            if self.spec.total_depth != 4 or self.spec.width != 16 or self.spec.batchnorm:
                raise ValueError("Frozen residual architecture must be depth4/width16/no-BN")

        self.classifier = nn.Linear(out_width, 4)

    def features(self, x):
        """Frozen intervention tensor: ReLU output of the first 16-channel conv."""
        return F.relu(self.conv(x))

    def tail_features(self, h):
        if self.spec.connectivity == "residual":
            z = F.relu(self.down_convs[0](h))
            z = F.relu(self.down_convs[1](z))
            z = F.relu(self.down_convs[2](z) + h)
        else:
            z = h
            for i, conv in enumerate(self.down_convs):
                z = conv(z)
                if self.spec.batchnorm:
                    z = self.down_bns[i](z)
                z = F.relu(z)

        if self.spec.pooling == "max":
            return z.amax((2, 3))
        if self.spec.pooling == "avg":
            return z.mean((2, 3))
        raise AssertionError(self.spec.pooling)

    def tail(self, h):
        return self.classifier(self.tail_features(h))

    def forward(self, x):
        return self.tail(self.features(x))


def setup_model(arch: str, block: int, task: str, init_rep: int):
    torch.manual_seed(model_seed(block, task, arch, init_rep))
    model = ArchitectureNet(arch)
    anchor = torch.from_numpy(legacy_core.bank()[:, None].copy())
    with torch.no_grad():
        model.conv.weight.copy_(anchor)
    return model, anchor


def retention_strength(treatment: str, epoch: int) -> float:
    if treatment == "retention_1":
        return 1.0
    if treatment == "release_default":
        return float(np.clip((80 - epoch) / (80 - 10), 0.0, 1.0))
    raise ValueError(treatment)


def parameter_count(arch: str) -> int:
    return sum(p.numel() for p in ArchitectureNet(arch).parameters())


def architecture_manifest():
    return {
        name: {
            "total_depth": spec.total_depth,
            "width": spec.width,
            "pooling": spec.pooling,
            "connectivity": spec.connectivity,
            "batchnorm": spec.batchnorm,
            "parameters": parameter_count(name),
        }
        for name, spec in ARCH_SPECS.items()
    }
