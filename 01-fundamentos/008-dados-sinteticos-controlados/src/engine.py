"""Motor do projeto 008 — Dados sintéticos controlados."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

def dump_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload

def run(source: Path, destination: Path) -> dict[str, Any]:
    if source.suffix == ".json":
        spec = json.loads(source.read_text(encoding="utf-8"))
    else:
        row = pd.read_csv(source).iloc[0].to_dict()
        spec = {"n": int(row.get("n", 400)), "seed": int(row.get("seed", 8)), "nulos": float(row.get("nulos", 0.05))}
    rng = np.random.default_rng(int(spec.get("seed", 8)))
    n = int(spec.get("n", 400))
    renda = rng.normal(4500, 1200, n).clip(800, 20000)
    score = 0.4 * ((renda - 4500) / 1200) + rng.normal(0, 0.7, n)
    alvo = (score > 0).astype(int)
    frame = pd.DataFrame({"renda": renda.round(2), "score_latente": score.round(4), "aprovado": alvo})
    mask = rng.random(n) < float(spec.get("nulos", 0.05))
    frame.loc[mask, "renda"] = np.nan
    csv_path = destination.with_name("sintetico.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(csv_path, index=False)
    payload = {
        "n": n,
        "seed": int(spec.get("seed", 8)),
        "taxa_nulos": float(frame["renda"].isna().mean()),
        "correlacao_renda_alvo": float(pd.Series(frame["renda"]).corr(frame["aprovado"])),
        "arquivo": str(csv_path),
    }
    return dump_json(destination, payload)
