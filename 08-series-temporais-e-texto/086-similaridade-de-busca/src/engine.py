"""Motor do projeto 086 — Busca por similaridade."""

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

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    vec = TfidfVectorizer(max_features=100)
    x = vec.fit_transform(frame["texto"].astype(str))
    query = "atraso na entrega do pedido"
    q = vec.transform([query])
    scores = cosine_similarity(q, x).ravel()
    top = scores.argsort()[::-1][:5]
    payload = {
        "query": query,
        "top": [{"indice": int(i), "score": float(scores[i]), "texto": str(frame.iloc[i]["texto"])} for i in top],
    }
    return dump_json(destination, payload)
