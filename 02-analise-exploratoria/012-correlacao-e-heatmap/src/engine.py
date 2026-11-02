"""Motor do projeto 012 — Correlação e heatmap."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def dump_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source).select_dtypes(include=["number"])
    pearson = frame.corr(method="pearson")
    spearman = frame.corr(method="spearman")
    fig_dir = destination.parent / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(pearson, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(pearson.columns)), pearson.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pearson.columns)), pearson.columns)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    png = fig_dir / "heatmap.png"
    fig.savefig(png, dpi=120)
    plt.close(fig)
    payload = {
        "pearson": pearson.round(3).to_dict(),
        "spearman": spearman.round(3).to_dict(),
        "figura": str(png),
    }
    return dump_json(destination, payload)
