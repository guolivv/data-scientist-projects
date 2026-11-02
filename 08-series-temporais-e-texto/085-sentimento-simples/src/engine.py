"""Motor do projeto 085 — Sentimento simples."""

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
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

POS = {"bom", "otimo", "excelente", "amo", "rapido", "adorei"}
NEG = {"ruim", "lento", "odiei", "pessimo", "atraso", "horrivel"}

def lexico(texto: str) -> str:
    toks = set(texto.lower().split())
    score = len(toks & POS) - len(toks & NEG)
    if score > 0:
        return "positivo"
    if score < 0:
        return "negativo"
    return "neutro"

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    pred_lex = frame["texto"].map(lexico)
    x_train, x_test, y_train, y_test = train_test_split(frame["texto"], frame["sentimento"], test_size=0.3, random_state=42, stratify=frame["sentimento"])
    model = LogisticRegression(max_iter=200)
    from sklearn.pipeline import Pipeline
    pipe = Pipeline([("tfidf", TfidfVectorizer(max_features=80)), ("clf", model)])
    pipe.fit(x_train, y_train)
    payload = {
        "f1_lexico": float(f1_score(frame["sentimento"], pred_lex, average="macro")),
        "f1_modelo": float(f1_score(y_test, pipe.predict(x_test), average="macro")),
    }
    return dump_json(destination, payload)
