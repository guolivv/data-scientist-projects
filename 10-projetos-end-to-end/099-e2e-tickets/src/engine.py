"""Motor do projeto 099 — Tickets de suporte ponta a ponta."""

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

from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score

POS, NEG = {"bom", "otimo", "resolveram"}, {"ruim", "atraso", "odiei", "pessimo"}

def sent(texto: str) -> str:
    toks = set(texto.lower().split())
    s = len(toks & POS) - len(toks & NEG)
    return "positivo" if s > 0 else "negativo" if s < 0 else "neutro"

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    vec = TfidfVectorizer(max_features=80)
    x = vec.fit_transform(frame["texto"].astype(str))
    nmf = NMF(n_components=3, random_state=42, max_iter=400).fit(x)
    vocab = np.array(vec.get_feature_names_out())
    topicos = [{"topico": i, "termos": vocab[row.argsort()[-5:][::-1]].tolist()} for i, row in enumerate(nmf.components_)]
    x_train, x_test, y_train, y_test = train_test_split(frame["texto"], frame["fila"], test_size=0.3, random_state=42, stratify=frame["fila"])
    pipe = Pipeline([("tfidf", TfidfVectorizer(max_features=80)), ("clf", LogisticRegression(max_iter=200))])
    pipe.fit(x_train, y_train)
    payload = {
        "topicos": topicos,
        "macro_f1_fila": float(f1_score(y_test, pipe.predict(x_test), average="macro")),
        "sentimento": frame["texto"].map(sent).value_counts().to_dict(),
    }
    return dump_json(destination, payload)
