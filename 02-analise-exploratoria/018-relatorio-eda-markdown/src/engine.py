"""Motor do projeto 018 — Relatório de EDA em Markdown."""

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
    numeric = frame.select_dtypes("number")
    md = ["# Relatório de EDA", "", f"Linhas: **{len(frame)}**. Colunas: **{frame.shape[1]}**.", "", "## Numéricas", ""]
    for col in numeric.columns:
        series = numeric[col].dropna()
        md.append(f"- `{col}`: média {series.mean():.2f}, mediana {series.median():.2f}, nulos {int(frame[col].isna().sum())}")
    md += ["", "## Riscos", "", "- Conferir nulos e assimetria antes de modelar.", "- Este relatório é gerado pelo projeto, não editado à mão.", ""]
    report = destination.with_suffix(".md")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(md), encoding="utf-8")
    payload = {"linhas": int(len(frame)), "relatorio": str(report), "n_numericas": int(numeric.shape[1])}
    return dump_json(destination, payload)
