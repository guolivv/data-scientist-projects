"""Motor do projeto 020 — Visualizações exportadas."""

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
    frame = pd.read_csv(source)
    fig_dir = destination.parent / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)
    numeric = frame.select_dtypes("number")
    col = numeric.columns[0]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(numeric[col].dropna(), bins=15, color="#38BDF8")
    ax.set_title(str(col))
    fig.tight_layout()
    fig.savefig(fig_dir / "01-hist.png", dpi=110)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(numeric[col].dropna().reset_index(drop=True), color="#FBBF24")
    ax.set_title("Série")
    fig.tight_layout()
    fig.savefig(fig_dir / "02-serie.png", dpi=110)
    plt.close(fig)
    if numeric.shape[1] >= 2:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.scatter(numeric.iloc[:, 0], numeric.iloc[:, 1], s=12, c="#38BDF8")
        fig.tight_layout()
        fig.savefig(fig_dir / "03-scatter.png", dpi=110)
        plt.close(fig)
    figuras = sorted(p.name for p in fig_dir.glob("*.png"))
    payload = {"figuras": figuras, "diretorio": str(fig_dir)}
    return dump_json(destination, payload)
