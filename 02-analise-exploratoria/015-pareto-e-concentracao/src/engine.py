"""Motor do projeto 015 — Pareto e concentração."""

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
    ranked = frame.groupby("sku", as_index=False)["receita"].sum().sort_values("receita", ascending=False)
    ranked["pct"] = ranked["receita"] / ranked["receita"].sum()
    ranked["acumulado"] = ranked["pct"].cumsum()
    corte = ranked[ranked["acumulado"] <= 0.8]
    payload = {
        "skus": int(len(ranked)),
        "skus_80": int(max(len(corte), 1)),
        "pct_skus_80": round(max(len(corte), 1) / max(len(ranked), 1), 4),
        "top": ranked.head(5).round(4).to_dict(orient="records"),
    }
    fig_dir = destination.parent / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(len(ranked)), ranked["receita"], color="#38BDF8")
    ax2 = ax.twinx()
    ax2.plot(range(len(ranked)), ranked["acumulado"], color="#FBBF24")
    fig.tight_layout()
    fig.savefig(fig_dir / "pareto.png", dpi=120)
    plt.close(fig)
    payload["figura"] = str(fig_dir / "pareto.png")
    return dump_json(destination, payload)
