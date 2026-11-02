"""Motor do projeto 096 — Previsão de demanda ponta a ponta."""

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
    frame = pd.read_csv(source, parse_dates=["data"]).sort_values("data")
    y = frame["y"].to_numpy(dtype=float)
    split = int(len(y) * 0.75)
    test = y[split:]
    naive = np.repeat(y[split - 1], len(test))
    roll = np.array([y[split - 7 + i : split + i].mean() if i == 0 else np.concatenate([y[split - 7 + i : split], test[:i]]).mean() for i in range(len(test))])
    payload = {
        "mae_naive": float(np.mean(np.abs(test - naive))),
        "mae_rolling": float(np.mean(np.abs(test - roll))),
        "n_teste": int(len(test)),
    }
    fig_dir = destination.parent / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(y, label="real")
    ax.axvline(split, color="#FBBF24")
    fig.tight_layout()
    fig.savefig(fig_dir / "serie.png", dpi=110)
    plt.close(fig)
    payload["figura"] = str(fig_dir / "serie.png")
    return dump_json(destination, payload)
