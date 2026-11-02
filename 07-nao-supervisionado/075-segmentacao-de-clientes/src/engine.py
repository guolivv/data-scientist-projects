"""Motor do projeto 075 — Segmentação de clientes."""

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

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    x = StandardScaler().fit_transform(frame[["recencia", "frequencia", "valor"]])
    labels = KMeans(n_clusters=3, n_init=10, random_state=42).fit_predict(x)
    frame["segmento"] = labels
    perfis = frame.groupby("segmento")[["recencia", "frequencia", "valor"]].mean().round(2)
    nomes = []
    for idx, row in perfis.iterrows():
        if row["valor"] == perfis["valor"].max():
            nome = "alto valor"
        elif row["recencia"] == perfis["recencia"].max():
            nome = "em risco"
        else:
            nome = "frequente"
        nomes.append({"segmento": int(idx), "persona": nome, **row.to_dict()})
    payload = {"personas": nomes, "n": int(len(frame))}
    return dump_json(destination, payload)
