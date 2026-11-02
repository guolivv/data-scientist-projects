"""Motor do projeto 011 — Distribuições univariadas."""

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
    col = "ticket" if "ticket" in frame.columns else frame.select_dtypes("number").columns[0]
    series = pd.to_numeric(frame[col], errors="coerce").dropna()
    fig_dir = destination.parent / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(series, bins=20, color="#38BDF8", edgecolor="white")
    ax.set_title(f"Distribuição de {col}")
    ax.set_xlabel(col)
    fig.tight_layout()
    png = fig_dir / "histograma.png"
    fig.savefig(png, dpi=120)
    plt.close(fig)
    qs = series.quantile([0.1, 0.5, 0.9]).to_dict()
    payload = {
        "coluna": str(col),
        "media": float(series.mean()),
        "mediana": float(series.median()),
        "assimetria": float(series.skew()),
        "quantis": {str(k): float(v) for k, v in qs.items()},
        "figura": str(png),
    }
    return dump_json(destination, payload)
