"""Motor do projeto 013 — Análise bivariada."""

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
    num, cat = "gasto", "segmento"
    resumo = frame.groupby(cat)[num].agg(["count", "mean", "median"]).round(2).reset_index()
    fig_dir = destination.parent / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    data = [frame.loc[frame[cat] == g, num].dropna() for g in resumo[cat]]
    ax.boxplot(data, tick_labels=list(resumo[cat].astype(str)))
    ax.set_ylabel(num)
    fig.tight_layout()
    png = fig_dir / "boxplot.png"
    fig.savefig(png, dpi=120)
    plt.close(fig)
    payload = {"resumo": resumo.to_dict(orient="records"), "figura": str(png)}
    return dump_json(destination, payload)
