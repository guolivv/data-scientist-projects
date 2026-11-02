"""Motor do projeto 090 — Model card."""

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

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=300).fit(x_train, y_train)
    auc = float(roc_auc_score(y_test, model.predict_proba(x_test)[:, 1]))
    md = destination.with_suffix(".md")
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(
        f"# Model card\n\n- Uso pretendido: score educacional de churn.\n- Dados: sintéticos, n={len(frame)}.\n- Métrica: ROC-AUC {auc:.3f} no holdout.\n- Limites: não usar em produção nem com dado pessoal real.\n- Grupos: avaliação de fairness não inclusa neste cartão.\n",
        encoding="utf-8",
    )
    payload = {"auc": auc, "model_card": str(md), "n_treino": int(len(x_train))}
    return dump_json(destination, payload)
