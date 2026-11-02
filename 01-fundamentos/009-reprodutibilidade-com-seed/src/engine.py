"""Motor do projeto 009 — Reprodutibilidade com seed."""

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

def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

import hashlib

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    rng = np.random.default_rng(42)
    amostra = frame.sample(frac=0.5, random_state=42)
    digest = hashlib.sha256(amostra.to_csv(index=False).encode("utf-8")).hexdigest()
    payload = {"seed": 42, "linhas_amostra": int(len(amostra)), "sha256": digest, "reproduzivel": True}
    second = hashlib.sha256(frame.sample(frac=0.5, random_state=42).to_csv(index=False).encode("utf-8")).hexdigest()
    payload["hashes_iguais"] = digest == second
    return dump_json(destination, payload)
