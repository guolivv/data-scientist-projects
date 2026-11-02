#!/usr/bin/env python3
"""Gera os 100 projetos, imagens, catálogo e arquivos da fundação."""

from __future__ import annotations

import hashlib
import json
import math
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from specs import SPECS, public_catalog  # noqa: E402

NIVEL_LABEL = {
    "basico": "Básico",
    "intermediario": "Intermediário",
    "avancado": "Avançado",
}


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")


def crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        len(data).to_bytes(4, "big")
        + tag
        + data
        + crc32(tag + data).to_bytes(4, "big")
    )


def encode_png(width: int, height: int, rgb: bytes) -> bytes:
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        start = y * stride
        raw.extend(rgb[start : start + stride])
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", width.to_bytes(4, "big") + height.to_bytes(4, "big") + b"\x08\x02\x00\x00\x00")
        + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + png_chunk(b"IEND", b"")
    )


def fill_rect(buf: bytearray, w: int, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
    r, g, b = color
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(w, x1)
    for y in range(max(0, y0), y1):
        row = y * w * 3
        for x in range(x0, x1):
            i = row + x * 3
            buf[i] = r
            buf[i + 1] = g
            buf[i + 2] = b


def stroke_rect(buf: bytearray, w: int, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int], t: int = 3) -> None:
    fill_rect(buf, w, x0, y0, x1, y0 + t, color)
    fill_rect(buf, w, x0, y1 - t, x1, y1, color)
    fill_rect(buf, w, x0, y0, x0 + t, y1, color)
    fill_rect(buf, w, x1 - t, y0, x1, y1, color)


def glyph_rows(ch: str) -> list[str]:
    # 5x7 bitmap, uppercase-oriented. Enough for titles on architecture cards.
    table = {
        " ": ["00000"] * 7,
        "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
        "—": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
        ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
        ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
        "/": ["00001", "00010", "00100", "01000", "10000", "00000", "00000"],
        "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
        "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
        "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
        "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
        "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
        "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
        "6": ["01110", "10000", "11110", "10001", "10001", "10001", "01110"],
        "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
        "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
        "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
        "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
        "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
        "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
        "D": ["11100", "10010", "10001", "10001", "10001", "10010", "11100"],
        "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
        "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
        "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
        "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
        "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
        "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
        "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
        "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
        "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
        "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
        "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
        "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
        "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
        "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
        "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
        "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
        "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
        "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
        "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
        "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
        "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
        "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
        "Á": ["00100", "01110", "10001", "11111", "10001", "10001", "10001"],
        "É": ["00100", "11111", "10000", "11110", "10000", "10000", "11111"],
        "Í": ["00100", "01110", "00100", "00100", "00100", "00100", "01110"],
        "Ó": ["00100", "01110", "10001", "10001", "10001", "10001", "01110"],
        "Ú": ["00100", "10001", "10001", "10001", "10001", "10001", "01110"],
        "Ã": ["01010", "01110", "10001", "11111", "10001", "10001", "10001"],
        "Õ": ["01010", "01110", "10001", "10001", "10001", "10001", "01110"],
        "Ç": ["01110", "10000", "10000", "10000", "10000", "01110", "00100"],
    }
    return table.get(ch.upper(), table[" "])


def draw_text(buf: bytearray, w: int, x: int, y: int, text: str, color: tuple[int, int, int], scale: int = 2) -> None:
    cursor = x
    for ch in text:
        rows = glyph_rows(ch)
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit != "1":
                    continue
                fill_rect(
                    buf,
                    w,
                    cursor + rx * scale,
                    y + ry * scale,
                    cursor + (rx + 1) * scale,
                    y + (ry + 1) * scale,
                    color,
                )
        cursor += 6 * scale


def wrap_label(text: str, width: int) -> list[str]:
    words = text.replace("—", "-").split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if len(trial) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:4] or [text[:width]]


def save_architecture(path: Path, spec: dict) -> None:
    w, h = 1400, 780
    buf = bytearray(w * h * 3)
    hue = spec["numero"]
    bg = (8 + (hue % 7), 16 + (hue % 11), 30 + (hue % 13))
    fill_rect(buf, w, 0, 0, w, h, bg)
    accent = (56, 189, 248)
    text = (230, 237, 247)
    muted = (148, 163, 184)
    card = (19, 35, 55)
    title = f"{spec['numero']:03d} - {spec['titulo']}"
    draw_text(buf, w, 48, 40, title.upper()[:42], text, 3)
    draw_text(buf, w, 48, 78, "CIENCIA DE DADOS  -  FLUXO DESTE PROJETO", muted, 2)
    boxes = spec["fluxo"]
    n = len(boxes)
    gap = 36
    box_w = min(280, (w - 96 - gap * (n - 1)) // n)
    box_h = 260
    y0 = 220
    x = 48
    for i, label in enumerate(boxes):
        x1 = x + box_w
        y1 = y0 + box_h
        fill_rect(buf, w, x, y0, x1, y1, card)
        stroke_rect(buf, w, x, y0, x1, y1, accent, 3)
        lines = wrap_label(label.upper(), 16)
        ty = y0 + 36
        for line in lines:
            draw_text(buf, w, x + 18, ty, line, text, 2)
            ty += 28
        if i < n - 1:
            ax0 = x1 + 6
            ax1 = x1 + gap - 6
            mid = y0 + box_h // 2
            fill_rect(buf, w, ax0, mid - 2, ax1, mid + 2, accent)
            fill_rect(buf, w, ax1 - 10, mid - 8, ax1, mid + 8, accent)
        x = x1 + gap
    draw_text(buf, w, 48, 720, "FUNDO ESCURO  CARTAO  BORDA CIANO  TEXTO CLARO", muted, 2)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode_png(w, h, bytes(buf)))


def save_cover(path: Path) -> None:
    w, h = 1600, 900
    buf = bytearray(w * h * 3)
    fill_rect(buf, w, 0, 0, w, h, (11, 18, 32))
    fill_rect(buf, w, 0, 0, 18, h, (56, 189, 248))
    draw_text(buf, w, 80, 80, "100 PROJETOS", (230, 237, 247), 5)
    draw_text(buf, w, 80, 140, "DE CIENCIA DE DADOS", (56, 189, 248), 5)
    draw_text(buf, w, 80, 210, "DO CSV AO MODELO E AO MODEL CARD", (148, 163, 184), 2)
    tracks = [
        "01 FUNDAMENTOS",
        "02 ANALISE EXPLORATORIA",
        "03 SQL PARA DS",
        "04 ESTATISTICA",
        "05 FEATURE ENGINEERING",
        "06 SUPERVISIONADO",
        "07 NAO SUPERVISIONADO",
        "08 SERIES E TEXTO",
        "09 AVALIACAO E MLOPS",
        "10 PROJETOS E2E",
    ]
    for i, name in enumerate(tracks):
        col = i % 2
        row = i // 2
        x = 80 + col * 740
        y = 300 + row * 90
        fill_rect(buf, w, x, y, x + 680, y + 72, (19, 35, 55))
        stroke_rect(buf, w, x, y, x + 680, y + 72, (56, 189, 248), 2)
        draw_text(buf, w, x + 24, y + 26, name, (230, 237, 247), 2)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode_png(w, h, bytes(buf)))


def save_roadmap(path: Path) -> None:
    w, h = 1600, 900
    buf = bytearray(w * h * 3)
    fill_rect(buf, w, 0, 0, w, h, (11, 18, 32))
    draw_text(buf, w, 64, 48, "ROADMAP  -  100 PROJETOS", (230, 237, 247), 4)
    levels = [
        (80, "BASICO 001-034", (34, 197, 94), "ARQUIVO, EDA, SQL"),
        (360, "INTERMEDIARIO 035-067", (56, 189, 248), "STATS, FEATURES, MODELOS"),
        (640, "AVANCADO 068-100", (251, 191, 36), "CLUSTER, SERIE, NLP, E2E"),
    ]
    for y, title, color, subtitle in levels:
        fill_rect(buf, w, 64, y, 1536, y + 220, (19, 35, 55))
        stroke_rect(buf, w, 64, y, 1536, y + 220, color, 4)
        draw_text(buf, w, 96, y + 40, title, color, 3)
        draw_text(buf, w, 96, y + 100, subtitle, (230, 237, 247), 2)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode_png(w, h, bytes(buf)))


MAIN_TEMPLATE = '''\
"""CLI do projeto {numero:03d} — {titulo}."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from engine import run

logger = logging.getLogger("projeto_{numero:03d}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="{objetivo}")
    parser.add_argument("--entrada", default="data/entrada.csv", help="CSV de entrada")
    parser.add_argument("--saida", default="out/resultado.json", help="JSON de saída")
    parser.add_argument("--log-level", default="INFO", help="Nível de log")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, str(args.log_level).upper(), logging.INFO),
        format="%(levelname)s %(name)s %(message)s",
        stream=sys.stderr,
        force=True,
    )
    source = Path(args.entrada)
    destination = Path(args.saida)
    try:
        if not source.is_file():
            raise FileNotFoundError(f"Arquivo de entrada não encontrado: {{source}}")
        result = run(source, destination)
    except (OSError, ValueError, KeyError) as exc:
        logger.error("Falha: %s", exc)
        print(f"Erro: {{exc}}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


TEST_TEMPLATE = '''\
from __future__ import annotations

import json
from pathlib import Path

from engine import run
from main import main

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "entrada.csv"


def test_run_produz_resultado(tmp_path: Path) -> None:
    saida = tmp_path / "resultado.json"
    result = run(SAMPLE, saida)
    assert saida.is_file()
    saved = json.loads(saida.read_text(encoding="utf-8"))
    assert isinstance(result, dict)
    assert saved
    for key in {keys!r}:
        assert key in result
        assert key in saved
{extra}


def test_cli_amostra_versionada(tmp_path: Path) -> None:
    saida = tmp_path / "cli.json"
    code = main(["--entrada", str(SAMPLE), "--saida", str(saida)])
    assert code == 0
    assert saida.is_file()


def test_arquivo_ausente(tmp_path: Path) -> None:
    code = main(["--entrada", str(tmp_path / "nao-existe.csv"), "--saida", str(tmp_path / "x.json")])
    assert code == 1
'''


def engine_source(spec: dict) -> str:
    family = spec["family"]
    params = spec["params"]
    header = f'"""Motor do projeto {spec["numero"]:03d} — {spec["titulo"]}."""\n'
    shared = """
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
"""
    if family == "wrangle":
        return header + shared + ENGINE_WRANGLE[params["ops"][0]]
    if family == "eda":
        return header + shared + "import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n" + ENGINE_EDA[params["chart"]]
    if family == "sql":
        return header + shared + "import sqlite3\n" + ENGINE_SQL[params["kind"]]
    if family == "stats":
        return header + shared + ENGINE_STATS[params["test"]]
    if family == "features":
        return header + shared + ENGINE_FEATURES[params["kind"]]
    if family == "supervised":
        return header + shared + ENGINE_SUPERVISED[params["model"]]
    if family == "unsupervised":
        return header + shared + ENGINE_UNSUPERVISED[params["kind"]]
    if family == "timeseries":
        return header + shared + ENGINE_TS[params["kind"]]
    if family == "nlp":
        return header + shared + ENGINE_NLP[params["kind"]]
    if family == "mlops":
        return header + shared + ENGINE_MLOPS[params["kind"]]
    if family == "e2e":
        extra = ""
        if params["kind"] in {"demand", "lab"}:
            extra = "import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n"
        return header + shared + extra + ENGINE_E2E[params["kind"]]
    raise KeyError(family)


def dump_json_fn() -> str:
    return '''
def dump_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    return payload
'''


ENGINE_WRANGLE = {
    "profile": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    payload = {
        "linhas": int(len(frame)),
        "colunas": list(map(str, frame.columns)),
        "n_colunas": int(frame.shape[1]),
        "tipos": {str(col): str(dtype) for col, dtype in frame.dtypes.items()},
        "nulos": {str(col): int(frame[col].isna().sum()) for col in frame.columns},
    }
    return dump_json(destination, payload)
''',
    "coerce": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    falhas: dict[str, int] = {}
    if "data" in frame.columns:
        parsed = pd.to_datetime(frame["data"], errors="coerce")
        falhas["data"] = int(parsed.isna().sum() - frame["data"].isna().sum())
        frame["data"] = parsed
    for col in ("quantidade", "receita", "preco"):
        if col not in frame.columns:
            continue
        numeric = pd.to_numeric(frame[col].astype(str).str.replace(",", ".", regex=False), errors="coerce")
        falhas[col] = int(numeric.isna().sum() - frame[col].isna().sum())
        frame[col] = numeric
    clean = destination.with_suffix(".csv")
    clean.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(clean, index=False)
    payload = {"linhas": int(len(frame)), "falhas_coercao": falhas, "arquivo_limpo": str(clean)}
    return dump_json(destination, payload)
''',
    "missing": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    n = len(frame)
    relatorio = {}
    for col in frame.columns:
        nulos = int(frame[col].isna().sum())
        relatorio[str(col)] = {"nulos": nulos, "pct": round(100 * nulos / max(n, 1), 2)}
    numeric = frame.select_dtypes(include=["number"])
    imputed = frame.copy()
    for col in numeric.columns:
        imputed[col] = imputed[col].fillna(imputed[col].median())
    dropped = frame.dropna()
    payload = {
        "linhas": n,
        "por_coluna": relatorio,
        "linhas_apos_dropna": int(len(dropped)),
        "linhas_apos_mediana": int(len(imputed)),
        "impacto_dropna": int(n - len(dropped)),
    }
    return dump_json(destination, payload)
''',
    "outliers": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    col = "ticket" if "ticket" in frame.columns else frame.select_dtypes("number").columns[0]
    series = pd.to_numeric(frame[col], errors="coerce").dropna()
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    flagged = (series < low) | (series > high)
    winsor = series.clip(low, high)
    payload = {
        "coluna": str(col),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "n_outliers": int(flagged.sum()),
        "media_original": float(series.mean()),
        "media_winsor": float(winsor.mean()),
        "limites": [float(low), float(high)],
    }
    return dump_json(destination, payload)
''',
    "dates": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    col = "data" if "data" in frame.columns else "pedido_em"
    frame[col] = pd.to_datetime(frame[col], errors="coerce")
    frame["ano"] = frame[col].dt.year
    frame["mes"] = frame[col].dt.month
    frame["dia_semana"] = frame[col].dt.dayofweek
    valor = "receita" if "receita" in frame.columns else frame.select_dtypes("number").columns[0]
    mensal = frame.dropna(subset=[col]).groupby(["ano", "mes"], as_index=False)[valor].sum()
    csv_path = destination.with_name("serie_mensal.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    mensal.to_csv(csv_path, index=False)
    payload = {
        "linhas": int(len(frame)),
        "n_meses": int(len(mensal)),
        "min": str(frame[col].min()),
        "max": str(frame[col].max()),
        "arquivo_serie": str(csv_path),
    }
    return dump_json(destination, payload)
''',
    "join": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    pedidos = pd.read_csv(source)
    clientes = pd.read_csv(source.with_name("clientes.csv"))
    merged = pedidos.merge(clientes, on="cliente_id", how="left")
    orfaos = merged[merged["segmento"].isna()] if "segmento" in merged.columns else merged[merged["cliente_id"].isna()]
    payload = {
        "pedidos": int(len(pedidos)),
        "clientes": int(len(clientes)),
        "unificados": int(len(merged)),
        "orfaos": int(len(orfaos)),
        "match_rate": round(1 - len(orfaos) / max(len(pedidos), 1), 4),
    }
    csv_path = destination.with_name("base_unificada.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(csv_path, index=False)
    payload["arquivo"] = str(csv_path)
    return dump_json(destination, payload)
''',
    "agg": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    grouped = frame.groupby(["categoria", "canal"], as_index=False).agg(
        pedidos=("pedido_id", "nunique") if "pedido_id" in frame.columns else ("receita", "size"),
        receita=("receita", "sum"),
        ticket=("receita", "mean"),
    )
    grouped["ticket"] = grouped["ticket"].round(2)
    grouped["receita"] = grouped["receita"].round(2)
    csv_path = destination.with_name("kpis.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    grouped.to_csv(csv_path, index=False)
    payload = {
        "n_grupos": int(len(grouped)),
        "receita_total": float(frame["receita"].sum()),
        "ticket_geral": round(float(frame["receita"].mean()), 2),
        "arquivo": str(csv_path),
    }
    return dump_json(destination, payload)
''',
    "synthetic": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    spec = json.loads(source.read_text(encoding="utf-8")) if source.suffix == ".json" else {"n": 400, "seed": 8, "nulos": 0.05}
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
        "correlacao_renda_alvo": float(frame[["renda", "aprovado"]].corr().iloc[0, 1]),
        "arquivo": str(csv_path),
    }
    return dump_json(destination, payload)
''',
    "repro": dump_json_fn() + '''
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
''',
    "describe": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    numeric = frame.select_dtypes(include=["number"])
    perfil = {}
    for col in numeric.columns:
        series = numeric[col].dropna()
        perfil[str(col)] = {
            "n": int(series.size),
            "media": float(series.mean()) if len(series) else None,
            "mediana": float(series.median()) if len(series) else None,
            "desvio": float(series.std(ddof=1)) if len(series) > 1 else 0.0,
            "assimetria": float(series.skew()) if len(series) > 2 else 0.0,
            "nunique": int(series.nunique()),
            "nulos": int(frame[col].isna().sum()),
        }
    payload = {"linhas": int(len(frame)), "perfil": perfil, "categoricas": {c: int(frame[c].nunique()) for c in frame.select_dtypes(exclude=["number"]).columns}}
    return dump_json(destination, payload)
''',
}


ENGINE_EDA = {
    "hist": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    col = "ticket" if "ticket" in frame.columns else frame.select_dtypes("number").columns[0]
    series = pd.to_numeric(frame[col], errors="coerce").dropna()
    fig_dir = destination.parent / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(series, bins=20, color="#38BDF8", edgecolor="white")
    ax.set_title(f"Distribuição de {col}")
    ax.set_xlabel(col)
    fig.tight_layout()
    png = fig_dir / "histograma.png"
    fig.savefig(png, dpi=120)
    plt.close(fig)
    qs = series.quantile([0.1, 0.5, 0.9]).to_dict()
    payload = {
        "coluna": str(col),
        "media": float(series.mean()),
        "mediana": float(series.median()),
        "assimetria": float(series.skew()),
        "quantis": {str(k): float(v) for k, v in qs.items()},
        "figura": str(png),
    }
    return dump_json(destination, payload)
''',
    "heatmap": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source).select_dtypes(include=["number"])
    pearson = frame.corr(method="pearson")
    spearman = frame.corr(method="spearman")
    fig_dir = destination.parent / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(pearson, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(pearson.columns)), pearson.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pearson.columns)), pearson.columns)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    png = fig_dir / "heatmap.png"
    fig.savefig(png, dpi=120)
    plt.close(fig)
    payload = {
        "pearson": pearson.round(3).to_dict(),
        "spearman": spearman.round(3).to_dict(),
        "figura": str(png),
    }
    return dump_json(destination, payload)
''',
    "box": dump_json_fn() + '''
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
''',
    "freq": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    col = "uf" if "uf" in frame.columns else frame.select_dtypes(exclude=["number"]).columns[0]
    counts = frame[col].value_counts(dropna=False).rename_axis(col).reset_index(name="n")
    counts["pct"] = (counts["n"] / counts["n"].sum()).round(4)
    counts["acumulado"] = counts["pct"].cumsum().round(4)
    csv_path = destination.with_name("frequencias.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    counts.to_csv(csv_path, index=False)
    payload = {"coluna": str(col), "n_niveis": int(len(counts)), "top": counts.head(5).to_dict(orient="records")}
    return dump_json(destination, payload)
''',
    "pareto": dump_json_fn() + '''
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
''',
    "groups": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    grouped = frame.groupby("canal")["converteu"].agg(["count", "mean", "sum"]).reset_index()
    grouped["taxa"] = grouped["mean"].round(4)
    grouped["se"] = np.sqrt(grouped["taxa"] * (1 - grouped["taxa"]) / grouped["count"])
    grouped["ic_low"] = (grouped["taxa"] - 1.96 * grouped["se"]).clip(0, 1).round(4)
    grouped["ic_high"] = (grouped["taxa"] + 1.96 * grouped["se"]).clip(0, 1).round(4)
    payload = {"grupos": grouped[["canal", "count", "taxa", "ic_low", "ic_high"]].to_dict(orient="records")}
    return dump_json(destination, payload)
''',
    "missingmap": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    por_coluna = {c: round(float(frame[c].isna().mean()), 4) for c in frame.columns}
    por_grupo = {}
    if "uf" in frame.columns and "renda" in frame.columns:
        por_grupo = frame.groupby("uf")["renda"].apply(lambda s: round(float(s.isna().mean()), 4)).to_dict()
    payload = {"por_coluna": por_coluna, "missing_renda_por_uf": por_grupo, "linhas": int(len(frame))}
    return dump_json(destination, payload)
''',
    "report": dump_json_fn() + '''
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
    report.write_text("\\n".join(md), encoding="utf-8")
    payload = {"linhas": int(len(frame)), "relatorio": str(report), "n_numericas": int(numeric.shape[1])}
    return dump_json(destination, payload)
''',
    "kpis": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    visitantes = int(frame["visitante_id"].nunique())
    compradores = int(frame.loc[frame["comprou"] == 1, "visitante_id"].nunique())
    conversao = compradores / max(visitantes, 1)
    ticket = float(frame.loc[frame["comprou"] == 1, "receita"].mean()) if compradores else 0.0
    d7 = float(frame["retido_d7"].mean()) if "retido_d7" in frame.columns else None
    payload = {
        "visitantes": visitantes,
        "compradores": compradores,
        "conversao": round(conversao, 4),
        "ticket": round(ticket, 2),
        "retencao_d7": None if d7 is None else round(d7, 4),
        "definicoes": {
            "conversao": "compradores únicos / visitantes únicos",
            "ticket": "média de receita entre quem comprou",
            "retencao_d7": "média da flag retido_d7",
        },
    }
    return dump_json(destination, payload)
''',
    "pack": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    fig_dir = destination.parent / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)
    numeric = frame.select_dtypes("number")
    col = numeric.columns[0]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(numeric[col].dropna(), bins=15, color="#38BDF8")
    ax.set_title(str(col))
    fig.tight_layout()
    fig.savefig(fig_dir / "01-hist.png", dpi=110)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(numeric[col].dropna().reset_index(drop=True), color="#FBBF24")
    ax.set_title("Série")
    fig.tight_layout()
    fig.savefig(fig_dir / "02-serie.png", dpi=110)
    plt.close(fig)
    if numeric.shape[1] >= 2:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.scatter(numeric.iloc[:, 0], numeric.iloc[:, 1], s=12, c="#38BDF8")
        fig.tight_layout()
        fig.savefig(fig_dir / "03-scatter.png", dpi=110)
        plt.close(fig)
    figuras = sorted(p.name for p in fig_dir.glob("*.png"))
    payload = {"figuras": figuras, "diretorio": str(fig_dir)}
    return dump_json(destination, payload)
''',
}


ENGINE_SQL = {
    "load": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    db = destination.parent / "vendas.sqlite"
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        frame.to_sql("vendas", conn, index=False, if_exists="replace")
        conn.execute("CREATE INDEX IF NOT EXISTS ix_vendas_data ON vendas(data)")
        receita = conn.execute("SELECT ROUND(SUM(receita),2) FROM vendas").fetchone()[0]
        n = conn.execute("SELECT COUNT(*) FROM vendas").fetchone()[0]
    payload = {"linhas": int(n), "receita": float(receita or 0), "sqlite": str(db)}
    return dump_json(destination, payload)
''',
    "analytics": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    with sqlite3.connect(":memory:") as conn:
        frame.to_sql("vendas", conn, index=False, if_exists="replace")
        ranking = pd.read_sql("""
            SELECT categoria, ROUND(SUM(receita),2) AS receita,
                   ROUND(AVG(receita),2) AS ticket,
                   RANK() OVER (ORDER BY SUM(receita) DESC) AS rank
            FROM vendas GROUP BY categoria
        """, conn)
        mix = pd.read_sql("""
            SELECT canal, ROUND(100.0 * SUM(receita) / (SELECT SUM(receita) FROM vendas), 2) AS pct
            FROM vendas GROUP BY canal
        """, conn)
    payload = {"ranking": ranking.to_dict(orient="records"), "mix_canal": mix.to_dict(orient="records")}
    return dump_json(destination, payload)
''',
    "cohort": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source, parse_dates=["data"])
    frame["mes"] = frame["data"].dt.to_period("M").astype(str)
    with sqlite3.connect(":memory:") as conn:
        frame.to_sql("pedidos", conn, index=False, if_exists="replace")
        cohort = pd.read_sql("""
            WITH primeira AS (
              SELECT cliente_id, MIN(mes) AS cohort FROM pedidos GROUP BY cliente_id
            )
            SELECT p.cohort, ped.mes, COUNT(DISTINCT ped.cliente_id) AS ativos
            FROM pedidos ped
            JOIN primeira p ON p.cliente_id = ped.cliente_id
            GROUP BY p.cohort, ped.mes
            ORDER BY p.cohort, ped.mes
        """, conn)
        tamanho = pd.read_sql("SELECT cohort, COUNT(*) AS n FROM (SELECT cliente_id, MIN(mes) AS cohort FROM pedidos GROUP BY cliente_id) t GROUP BY cohort", conn)
    payload = {"matriz": cohort.to_dict(orient="records"), "tamanhos": tamanho.to_dict(orient="records")}
    return dump_json(destination, payload)
''',
    "funnel": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    ordem = ["visita", "cadastro", "checkout", "compra"]
    with sqlite3.connect(":memory:") as conn:
        frame.to_sql("eventos", conn, index=False, if_exists="replace")
        counts = pd.read_sql("SELECT etapa, COUNT(DISTINCT usuario_id) AS n FROM eventos GROUP BY etapa", conn)
    mapa = {row.etapa: int(row.n) for row in counts.itertuples()}
    funil = []
    prev = None
    for etapa in ordem:
        n = mapa.get(etapa, 0)
        taxa = None if prev in (None, 0) else round(n / prev, 4)
        funil.append({"etapa": etapa, "n": n, "taxa_vs_anterior": taxa})
        prev = n
    payload = {"funil": funil, "conversao_final": None if not funil[0]["n"] else round(funil[-1]["n"] / funil[0]["n"], 4)}
    return dump_json(destination, payload)
''',
    "rfm": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source, parse_dates=["data"])
    snapshot = frame["data"].max() + pd.Timedelta(days=1)
    rfm = frame.groupby("cliente_id").agg(
        recencia=("data", lambda s: (snapshot - s.max()).days),
        frequencia=("pedido_id", "nunique"),
        valor=("receita", "sum"),
    ).reset_index()
    rfm["r"] = pd.qcut(rfm["recencia"].rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["f"] = pd.qcut(rfm["frequencia"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m"] = pd.qcut(rfm["valor"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["rfm"] = rfm["r"].astype(str) + rfm["f"].astype(str) + rfm["m"].astype(str)
    payload = {"n_clientes": int(len(rfm)), "score_medio": rfm[["r", "f", "m"]].mean().round(2).to_dict(), "top": rfm.sort_values("valor", ascending=False).head(5).to_dict(orient="records")}
    csv_path = destination.with_name("rfm.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rfm.to_csv(csv_path, index=False)
    payload["arquivo"] = str(csv_path)
    return dump_json(destination, payload)
''',
    "window": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source, parse_dates=["data"])
    with sqlite3.connect(":memory:") as conn:
        frame.to_sql("serie", conn, index=False, if_exists="replace")
        out = pd.read_sql("""
            SELECT data, receita,
                   LAG(receita, 1) OVER (ORDER BY data) AS anterior,
                   AVG(receita) OVER (ORDER BY data ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS media_7,
                   RANK() OVER (ORDER BY receita DESC) AS rank_receita
            FROM serie ORDER BY data
        """, conn)
    payload = {"linhas": int(len(out)), "amostra": out.head(8).to_dict(orient="records")}
    csv_path = destination.with_name("features_janela.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(csv_path, index=False)
    return dump_json(destination, payload)
''',
    "sample": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    fracao = 0.2
    partes = []
    for uf, grupo in frame.groupby("uf"):
        n = max(1, int(round(len(grupo) * fracao)))
        partes.append(grupo.sample(n=min(n, len(grupo)), random_state=42))
    amostra = pd.concat(partes, ignore_index=True)
    pop = frame["uf"].value_counts(normalize=True).round(3).to_dict()
    amp = amostra["uf"].value_counts(normalize=True).round(3).to_dict()
    payload = {"n_pop": int(len(frame)), "n_amostra": int(len(amostra)), "mix_pop": pop, "mix_amostra": amp}
    return dump_json(destination, payload)
''',
    "pivot": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    largo = pd.read_csv(source)
    id_vars = [c for c in largo.columns if c in {"sku", "categoria"}]
    value_vars = [c for c in largo.columns if c not in id_vars]
    longo = largo.melt(id_vars=id_vars, value_vars=value_vars, var_name="mes", value_name="receita")
    payload = {"colunas_largas": value_vars, "linhas_longas": int(len(longo)), "formato": "tidy"}
    csv_path = destination.with_name("longo.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    longo.to_csv(csv_path, index=False)
    payload["arquivo"] = str(csv_path)
    return dump_json(destination, payload)
''',
    "asof": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    eventos = pd.read_csv(source, parse_dates=["evento_em"])
    cadastro = pd.read_csv(source.with_name("cadastro.csv"), parse_dates=["vigente_em"])
    leak = eventos.merge(cadastro, on="cliente_id", how="left")
    leak_futuro = leak[leak["vigente_em"] > leak["evento_em"]]
    cadastro = cadastro.sort_values("vigente_em")
    eventos = eventos.sort_values("evento_em")
    asof = pd.merge_asof(
        eventos.sort_values("evento_em"),
        cadastro.sort_values("vigente_em"),
        by="cliente_id",
        left_on="evento_em",
        right_on="vigente_em",
        direction="backward",
    )
    payload = {
        "eventos": int(len(eventos)),
        "joins_com_futuro": int(len(leak_futuro)),
        "asof_linhas": int(len(asof)),
        "asof_sem_cadastro": int(asof["segmento"].isna().sum()) if "segmento" in asof.columns else 0,
    }
    return dump_json(destination, payload)
''',
    "kpi": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    with sqlite3.connect(":memory:") as conn:
        frame.to_sql("fatos", conn, index=False, if_exists="replace")
        kpis = pd.read_sql("""
            SELECT DATE(data) AS dia,
                   ROUND(SUM(receita),2) AS receita,
                   ROUND(SUM(receita - custo),2) AS margem,
                   ROUND(1.0 * SUM(receita - custo) / NULLIF(SUM(receita),0), 4) AS margem_pct
            FROM fatos GROUP BY DATE(data) ORDER BY 1
        """, conn)
    dicionario = {
        "receita": "soma de receita bruta do dia",
        "margem": "receita menos custo",
        "margem_pct": "margem / receita",
    }
    payload = {"kpis": kpis.to_dict(orient="records"), "dicionario": dicionario}
    return dump_json(destination, payload)
''',
    "feat_sql": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    eventos = pd.read_csv(source, parse_dates=["data"])
    pontos = eventos[["cliente_id"]].drop_duplicates().copy()
    pontos["cutoff"] = eventos["data"].max()
    feats = []
    for row in pontos.itertuples():
        hist = eventos[(eventos["cliente_id"] == row.cliente_id) & (eventos["data"] < row.cutoff)]
        janela = hist[hist["data"] >= row.cutoff - pd.Timedelta(days=30)]
        feats.append({
            "cliente_id": row.cliente_id,
            "pedidos_30d": int(len(janela)),
            "receita_30d": float(janela["receita"].sum()) if len(janela) else 0.0,
            "recencia": None if hist.empty else int((row.cutoff - hist["data"].max()).days),
        })
    payload = {"features": feats, "cutoff": str(pontos["cutoff"].iloc[0].date())}
    return dump_json(destination, payload)
''',
    "quality": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    with sqlite3.connect(":memory:") as conn:
        frame.to_sql("mart", conn, index=False, if_exists="replace")
        nulos = conn.execute("SELECT COUNT(*) FROM mart WHERE pedido_id IS NULL OR receita IS NULL").fetchone()[0]
        dup = conn.execute("SELECT COUNT(*) FROM (SELECT pedido_id FROM mart GROUP BY pedido_id HAVING COUNT(*)>1)").fetchone()[0]
        faixa = conn.execute("SELECT COUNT(*) FROM mart WHERE receita < 0").fetchone()[0]
    falhas = []
    if nulos:
        falhas.append("not_null")
    if dup:
        falhas.append("unique")
    if faixa:
        falhas.append("faixa")
    payload = {"nulos": int(nulos), "duplicatas": int(dup), "receita_negativa": int(faixa), "falhas": falhas, "passou": not falhas}
    return dump_json(destination, payload)
''',
    "views": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    pedidos = pd.read_csv(source)
    itens = pd.read_csv(source.with_name("itens.csv"))
    db = destination.parent / "analitico.sqlite"
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        pedidos.to_sql("pedidos", conn, index=False, if_exists="replace")
        itens.to_sql("itens", conn, index=False, if_exists="replace")
        conn.execute("""
            CREATE VIEW IF NOT EXISTS vw_pedido_item AS
            SELECT p.pedido_id, p.data, p.cliente_id, i.sku, i.quantidade, i.preco,
                   i.quantidade * i.preco AS receita
            FROM pedidos p JOIN itens i ON i.pedido_id = p.pedido_id
        """)
        resumo = pd.read_sql("SELECT COUNT(*) AS linhas, ROUND(SUM(receita),2) AS receita FROM vw_pedido_item", conn)
    payload = {"sqlite": str(db), "view": "vw_pedido_item", "resumo": resumo.to_dict(orient="records")[0]}
    return dump_json(destination, payload)
''',
    "dict": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    regras = {
        "pedido_id": "identificador do pedido",
        "data": "data do pedido (AAAA-MM-DD)",
        "receita": "valor em reais",
        "cliente_id": "chave do cliente",
        "categoria": "categoria mercadológica",
    }
    linhas = ["# Dicionário analítico", ""]
    registros = []
    for col in frame.columns:
        dtype = str(frame[col].dtype)
        registros.append({
            "coluna": col,
            "tipo": dtype,
            "nulos": int(frame[col].isna().sum()),
            "nunique": int(frame[col].nunique()),
            "descricao": regras.get(col, "sem descrição cadastrada"),
        })
        linhas.append(f"- `{col}` ({dtype}): {regras.get(col, 'sem descrição cadastrada')}")
    md = destination.with_suffix(".md")
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text("\\n".join(linhas) + "\\n", encoding="utf-8")
    payload = {"colunas": registros, "markdown": str(md)}
    return dump_json(destination, payload)
''',
}


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


ENGINE_STATS = {
    "robust": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    series = pd.to_numeric(pd.read_csv(source)["ticket"], errors="coerce").dropna()
    med = float(series.median())
    mad = float(np.median(np.abs(series - med)))
    payload = {
        "media": float(series.mean()),
        "mediana": med,
        "iqr": float(series.quantile(0.75) - series.quantile(0.25)),
        "mad": mad,
        "recomendacao": "mediana" if abs(series.mean() - med) > series.std(ddof=1) * 0.25 else "media",
    }
    return dump_json(destination, payload)
''',
    "ci": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    p = float(frame["converteu"].mean())
    n = int(len(frame))
    se_p = math.sqrt(p * (1 - p) / max(n, 1))
    media = float(frame["ticket"].mean())
    se_m = float(frame["ticket"].std(ddof=1) / math.sqrt(n))
    z = 1.96
    payload = {
        "n": n,
        "conversao": p,
        "ic_conversao": [max(0, p - z * se_p), min(1, p + z * se_p)],
        "ticket": media,
        "ic_ticket": [media - z * se_m, media + z * se_m],
    }
    return dump_json(destination, payload)
''',
    "ttest": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    a = frame.loc[frame["canal"] == "pago", "ticket"].dropna()
    b = frame.loc[frame["canal"] == "organico", "ticket"].dropna()
    ma, mb = float(a.mean()), float(b.mean())
    va, vb = float(a.var(ddof=1)), float(b.var(ddof=1))
    se = math.sqrt(va / len(a) + vb / len(b))
    t = (ma - mb) / se if se else 0.0
    df = len(a) + len(b) - 2
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    payload = {"n_pago": int(len(a)), "n_organico": int(len(b)), "media_pago": ma, "media_organico": mb, "t": t, "p_valor": float(p), "df": df}
    return dump_json(destination, payload)
''',
    "chi2": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    tab = pd.crosstab(frame["dispositivo"], frame["converteu"])
    expected = pd.DataFrame(np.outer(tab.sum(axis=1), tab.sum(axis=0)) / tab.values.sum(), index=tab.index, columns=tab.columns)
    chi = float(((tab - expected) ** 2 / expected.replace(0, np.nan)).sum().sum())
    df = (tab.shape[0] - 1) * (tab.shape[1] - 1)
    payload = {"tabela": tab.to_dict(), "chi2": chi, "df": int(df)}
    return dump_json(destination, payload)
''',
    "simpson": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    geral = float(frame[["x", "y"]].corr().iloc[0, 1])
    por_grupo = {str(name): float(g[["x", "y"]].corr().iloc[0, 1]) for name, g in frame.groupby("grupo")}
    payload = {
        "correlacao_agregada": geral,
        "por_grupo": por_grupo,
        "inversao": (geral > 0 and min(por_grupo.values()) < 0) or (geral < 0 and max(por_grupo.values()) > 0),
    }
    return dump_json(destination, payload)
''',
    "ab": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    a = frame.loc[frame["variante"] == "A", "converteu"]
    b = frame.loc[frame["variante"] == "B", "converteu"]
    pa, pb = float(a.mean()), float(b.mean())
    na, nb = int(len(a)), int(len(b))
    p = (a.sum() + b.sum()) / (na + nb)
    se = math.sqrt(p * (1 - p) * (1 / na + 1 / nb))
    z = (pb - pa) / se if se else 0.0
    pval = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    payload = {
        "conversao_a": pa, "conversao_b": pb, "n_a": na, "n_b": nb,
        "uplift_abs": pb - pa, "uplift_rel": (pb - pa) / pa if pa else None,
        "z": z, "p_valor": float(pval), "vencedor": "B" if pb > pa and pval < 0.05 else "inconclusivo",
    }
    return dump_json(destination, payload)
''',
    "power": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    p = float(frame["converteu"].mean())
    mde = 0.05
    alpha, power = 0.05, 0.8
    z_a, z_b = 1.96, 0.84
    n = 2 * p * (1 - p) * ((z_a + z_b) ** 2) / (mde ** 2)
    payload = {"baseline": p, "mde": mde, "alpha": alpha, "poder": power, "n_por_variante": int(math.ceil(n)), "n_observado": int(len(frame) // 2)}
    return dump_json(destination, payload)
''',
    "bootstrap": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    series = pd.to_numeric(pd.read_csv(source)["ticket"], errors="coerce").dropna().to_numpy()
    rng = np.random.default_rng(42)
    boots = np.array([np.median(rng.choice(series, size=len(series), replace=True)) for _ in range(400)])
    payload = {
        "mediana": float(np.median(series)),
        "ic_bootstrap": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
        "n_boot": 400,
    }
    return dump_json(destination, payload)
''',
    "mw": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    a = frame.loc[frame["plano"] == "plus", "gasto"].dropna().to_numpy()
    b = frame.loc[frame["plano"] == "basic", "gasto"].dropna().to_numpy()
    combined = np.concatenate([a, b])
    ranks = pd.Series(combined).rank().to_numpy()
    u = ranks[: len(a)].sum() - len(a) * (len(a) + 1) / 2
    mu = len(a) * len(b) / 2
    sigma = math.sqrt(len(a) * len(b) * (len(a) + len(b) + 1) / 12)
    z = (u - mu) / sigma if sigma else 0.0
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    payload = {"u": float(u), "z": z, "p_valor": float(p), "media_plus": float(a.mean()), "media_basic": float(b.mean())}
    return dump_json(destination, payload)
''',
    "cuped": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y, x = frame["y"], frame["x_pre"]
    theta = float(np.cov(y, x, ddof=1)[0, 1] / np.var(x, ddof=1))
    y_adj = y - theta * (x - x.mean())
    var_before = float(y.var(ddof=1))
    var_after = float(y_adj.var(ddof=1))
    a = y_adj[frame["variante"] == "A"]
    b = y_adj[frame["variante"] == "B"]
    payload = {
        "theta": theta,
        "var_antes": var_before,
        "var_depois": var_after,
        "reducao": round(1 - var_after / var_before, 4),
        "media_a_ajustada": float(a.mean()),
        "media_b_ajustada": float(b.mean()),
    }
    return dump_json(destination, payload)
''',
    "fdr": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    pvals = frame["p_valor"].astype(float).to_numpy()
    m = len(pvals)
    bonf = np.minimum(pvals * m, 1)
    order = np.argsort(pvals)
    ranked = pvals[order]
    fdr = np.empty(m)
    prev = 1.0
    for i in range(m, 0, -1):
        val = ranked[i - 1] * m / i
        prev = min(prev, val)
        fdr[i - 1] = min(prev, 1)
    adj = np.empty(m)
    adj[order] = fdr
    payload = {
        "n_testes": m,
        "significativos_brutos": int((pvals < 0.05).sum()),
        "significativos_bonferroni": int((bonf < 0.05).sum()),
        "significativos_fdr": int((adj < 0.05).sum()),
    }
    return dump_json(destination, payload)
''',
    "peek": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    rng = np.random.default_rng(0)
    n_sims, n = 200, int(len(frame))
    fp_peek = 0
    fp_fixo = 0
    for _ in range(n_sims):
        a = rng.binomial(1, 0.1, n)
        b = rng.binomial(1, 0.1, n)
        peeked = False
        for k in range(40, n + 1, 20):
            pa, pb = a[:k].mean(), b[:k].mean()
            p = (a[:k].sum() + b[:k].sum()) / (2 * k)
            se = math.sqrt(p * (1 - p) * (2 / k))
            z = abs(pb - pa) / se if se else 0
            pval = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))
            if pval < 0.05:
                peeked = True
                break
        fp_peek += int(peeked)
        pa, pb = a.mean(), b.mean()
        p = (a.sum() + b.sum()) / (2 * n)
        se = math.sqrt(p * (1 - p) * (2 / n))
        z = abs(pb - pa) / se if se else 0
        pval = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))
        fp_fixo += int(pval < 0.05)
    payload = {"falso_positivo_peeking": fp_peek / n_sims, "falso_positivo_n_fixo": fp_fixo / n_sims, "simulacoes": n_sims}
    return dump_json(destination, payload)
''',
}


ENGINE_FEATURES = {
    "encode": dump_json_fn() + '''
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    cats = frame[["uf", "canal"]]
    onehot = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    ordinal = OrdinalEncoder()
    oh = onehot.fit_transform(cats)
    ord_ = ordinal.fit_transform(cats)
    payload = {
        "n": int(len(frame)),
        "onehot_dim": int(oh.shape[1]),
        "ordinal_dim": int(ord_.shape[1]),
        "categorias_uf": list(map(str, ordinal.categories_[0])),
    }
    out = pd.concat([frame.reset_index(drop=True), pd.DataFrame(oh, columns=onehot.get_feature_names_out())], axis=1)
    csv_path = destination.with_name("encoded.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(csv_path, index=False)
    payload["arquivo"] = str(csv_path)
    return dump_json(destination, payload)
''',
    "scale": dump_json_fn() + '''
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    cols = [c for c in ("renda", "idade") if c in frame.columns]
    x = frame[cols]
    resumo = {}
    for name, scaler in (("standard", StandardScaler()), ("minmax", MinMaxScaler()), ("robust", RobustScaler())):
        z = scaler.fit_transform(x)
        resumo[name] = {"min": z.min(axis=0).tolist(), "max": z.max(axis=0).tolist(), "media": z.mean(axis=0).tolist()}
    payload = {"colunas": cols, "scalers": resumo}
    return dump_json(destination, payload)
''',
    "bin": dump_json_fn() + '''
from sklearn.preprocessing import KBinsDiscretizer

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    x = frame[["idade"]]
    uniforme = KBinsDiscretizer(n_bins=4, encode="ordinal", strategy="uniform")
    quantil = KBinsDiscretizer(n_bins=4, encode="ordinal", strategy="quantile")
    payload = {
        "uniforme": uniforme.fit_transform(x).ravel().tolist()[:12],
        "quantil": quantil.fit_transform(x).ravel().tolist()[:12],
        "bordas_uniforme": uniforme.bin_edges_[0].tolist(),
        "bordas_quantil": quantil.bin_edges_[0].tolist(),
    }
    return dump_json(destination, payload)
''',
    "calendar": dump_json_fn() + '''
FERIADOS = {"01-01", "04-21", "09-07", "12-25"}

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source, parse_dates=["data"])
    frame["mes"] = frame["data"].dt.month
    frame["dow"] = frame["data"].dt.dayofweek
    frame["fim_de_mes"] = (frame["data"] + pd.Timedelta(days=1)).dt.month.ne(frame["mes"]).astype(int)
    frame["feriado"] = frame["data"].dt.strftime("%m-%d").isin(FERIADOS).astype(int)
    csv_path = destination.with_name("calendar_features.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(csv_path, index=False)
    payload = {"linhas": int(len(frame)), "n_feriados": int(frame["feriado"].sum()), "arquivo": str(csv_path)}
    return dump_json(destination, payload)
''',
    "target_enc": dump_json_fn() + '''
from sklearn.model_selection import KFold

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    fold = KFold(n_splits=5, shuffle=True, random_state=42)
    encoded = np.zeros(len(frame))
    global_mean = float(frame["alvo"].mean())
    for train_idx, val_idx in fold.split(frame):
        means = frame.iloc[train_idx].groupby("cidade")["alvo"].mean()
        encoded[val_idx] = frame.iloc[val_idx]["cidade"].map(means).fillna(global_mean)
    naive = frame["cidade"].map(frame.groupby("cidade")["alvo"].mean())
    payload = {
        "media_global": global_mean,
        "corr_cv": float(pd.Series(encoded).corr(frame["alvo"])),
        "corr_ingenuo": float(naive.corr(frame["alvo"])),
        "leakage_reduzido": True,
    }
    return dump_json(destination, payload)
''',
    "pipeline": dump_json_fn() + '''
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import pickle

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    numeric = x.select_dtypes("number").columns.tolist()
    cats = x.select_dtypes(exclude="number").columns.tolist()
    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cats),
    ])
    pipe = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=200))])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    pipe.fit(x_train, y_train)
    acc = float(pipe.score(x_test, y_test))
    art = destination.with_name("pipeline.pkl")
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_bytes(pickle.dumps(pipe))
    payload = {"acuracia_holdout": acc, "artefato": str(art), "passos": list(pipe.named_steps)}
    return dump_json(destination, payload)
''',
    "leakage": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    eventos = pd.read_csv(source, parse_dates=["data"])
    pontos = eventos.groupby("cliente_id", as_index=False)["data"].max().rename(columns={"data": "cutoff"})
    leak, limpo = [], []
    for row in pontos.itertuples():
        hist_leak = eventos[(eventos["cliente_id"] == row.cliente_id) & (eventos["data"] <= row.cutoff)]
        hist_ok = eventos[(eventos["cliente_id"] == row.cliente_id) & (eventos["data"] < row.cutoff)]
        leak.append(float(hist_leak["receita"].sum()))
        limpo.append(float(hist_ok["receita"].sum()))
    payload = {
        "media_com_leakage": float(np.mean(leak)),
        "media_sem_leakage": float(np.mean(limpo)),
        "diferenca": float(np.mean(leak) - np.mean(limpo)),
        "regra": "janela exclusiva: data < cutoff",
    }
    return dump_json(destination, payload)
''',
    "select": dump_json_fn() + '''
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    model = RandomForestClassifier(n_estimators=80, random_state=42)
    model.fit(x_train, y_train)
    imp = pd.Series(model.feature_importances_, index=x.columns).sort_values(ascending=False)
    corr = x_train.join(y_train).corr()["alvo"].drop("alvo").abs().sort_values(ascending=False)
    payload = {
        "importancia": imp.round(4).to_dict(),
        "corr_alvo": corr.round(4).to_dict(),
        "top": list(imp.head(5).index),
        "acuracia": float(model.score(x_test, y_test)),
    }
    return dump_json(destination, payload)
''',
    "interact": dump_json_fn() + '''
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["y"]
    x = frame[["preco", "categoria_code"]]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    base = LinearRegression().fit(x_train, y_train)
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    xp_train, xp_test = poly.fit_transform(x_train), poly.transform(x_test)
    rich = LinearRegression().fit(xp_train, y_train)
    payload = {
        "r2_baseline": float(r2_score(y_test, base.predict(x_test))),
        "r2_interacao": float(r2_score(y_test, rich.predict(xp_test))),
        "features": list(poly.get_feature_names_out(x.columns)),
    }
    return dump_json(destination, payload)
''',
    "impute": dump_json_fn() + '''
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_ind = x.copy()
    for col in x.columns:
        x_ind[f"{col}_missing"] = x[col].isna().astype(int)
    results = {}
    for name, xx in (("mediana", x), ("mediana_mais_indicador", x_ind)):
        x_train, x_test, y_train, y_test = train_test_split(xx, y, test_size=0.3, random_state=42)
        pipe = Pipeline([("imp", SimpleImputer(strategy="median")), ("clf", LogisticRegression(max_iter=200))])
        pipe.fit(x_train, y_train)
        results[name] = float(pipe.score(x_test, y_test))
    payload = {"acuracias": results, "taxa_nulos": {c: float(frame[c].isna().mean()) for c in frame.columns if c != "alvo"}}
    return dump_json(destination, payload)
''',
}


ENGINE_SUPERVISED = {
    "linear": dump_json_fn() + '''
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["preco"]
    x = frame[["area", "quartos", "idade"]]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    model = LinearRegression().fit(x_train, y_train)
    pred = model.predict(x_test)
    payload = {
        "coeficientes": dict(zip(x.columns, model.coef_.tolist())),
        "intercepto": float(model.intercept_),
        "rmse": float(mean_squared_error(y_test, pred) ** 0.5),
        "r2": float(r2_score(y_test, pred)),
        "n_treino": int(len(x_train)),
        "n_teste": int(len(x_test)),
    }
    return dump_json(destination, payload)
''',
    "metrics": dump_json_fn() + '''
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["y"]
    x = frame.drop(columns=["y"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    pred = LinearRegression().fit(x_train, y_train).predict(x_test)
    mae = float(mean_absolute_error(y_test, pred))
    rmse = float(mean_squared_error(y_test, pred) ** 0.5)
    mape = float(np.mean(np.abs((y_test - pred) / np.clip(np.abs(y_test), 1e-6, None))))
    payload = {"rmse": rmse, "mae": mae, "mape": mape, "r2": float(r2_score(y_test, pred)), "unidade": "reais"}
    return dump_json(destination, payload)
''',
    "logreg": dump_json_fn() + '''
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["churn"]
    x = frame.drop(columns=["churn"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=300).fit(x_train, y_train)
    proba = model.predict_proba(x_test)[:, 1]
    payload = {
        "acuracia": float(accuracy_score(y_test, (proba >= 0.5).astype(int))),
        "log_loss": float(log_loss(y_test, proba)),
        "odds": dict(zip(x.columns, np.exp(model.coef_[0]).tolist())),
        "intercepto": float(model.intercept_[0]),
    }
    return dump_json(destination, payload)
''',
    "threshold": dump_json_fn() + '''
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, precision_score, recall_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    proba = LogisticRegression(max_iter=300).fit(x_train, y_train).predict_proba(x_test)[:, 1]
    linhas = []
    for thr in np.linspace(0.2, 0.8, 7):
        pred = (proba >= thr).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
        custo = fp * 10 + fn * 50
        linhas.append({"threshold": round(float(thr), 2), "precision": float(precision_score(y_test, pred, zero_division=0)), "recall": float(recall_score(y_test, pred, zero_division=0)), "custo": int(custo), "fp": int(fp), "fn": int(fn)})
    melhor = min(linhas, key=lambda r: r["custo"])
    payload = {"varredura": linhas, "melhor": melhor}
    return dump_json(destination, payload)
''',
    "tree": dump_json_fn() + '''
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    model = DecisionTreeClassifier(max_depth=3, random_state=42).fit(x_train, y_train)
    payload = {
        "acuracia": float(model.score(x_test, y_test)),
        "importancias": dict(zip(x.columns, model.feature_importances_.tolist())),
        "regras": export_text(model, feature_names=list(x.columns)),
        "profundidade": int(model.get_depth()),
    }
    return dump_json(destination, payload)
''',
    "rf": dump_json_fn() + '''
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    tree = DecisionTreeClassifier(max_depth=6, random_state=42).fit(x_train, y_train)
    forest = RandomForestClassifier(n_estimators=120, random_state=42).fit(x_train, y_train)
    payload = {
        "acuracia_arvore": float(tree.score(x_test, y_test)),
        "acuracia_floresta": float(forest.score(x_test, y_test)),
        "ganho": float(forest.score(x_test, y_test) - tree.score(x_test, y_test)),
    }
    return dump_json(destination, payload)
''',
    "gb": dump_json_fn() + '''
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    rf = RandomForestClassifier(n_estimators=80, random_state=42).fit(x_train, y_train)
    gb = GradientBoostingClassifier(n_estimators=60, max_depth=2, random_state=42).fit(x_train, y_train)
    payload = {
        "acuracia_rf": float(rf.score(x_test, y_test)),
        "acuracia_gb": float(gb.score(x_test, y_test)),
        "n_estimators_gb": 60,
    }
    return dump_json(destination, payload)
''',
    "cv": dump_json_fn() + '''
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    scores = cross_val_score(LogisticRegression(max_iter=300), x, y, cv=5, scoring="accuracy")
    payload = {"folds": scores.tolist(), "media": float(scores.mean()), "desvio": float(scores.std(ddof=1)), "k": 5}
    return dump_json(destination, payload)
''',
    "imbalance": dump_json_fn() + '''
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import recall_score, precision_score
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["fraude"]
    x = frame.drop(columns=["fraude"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    plain = LogisticRegression(max_iter=300).fit(x_train, y_train)
    weighted = LogisticRegression(max_iter=300, class_weight="balanced").fit(x_train, y_train)
    def pack(model):
        pred = model.predict(x_test)
        return {"precision": float(precision_score(y_test, pred, zero_division=0)), "recall": float(recall_score(y_test, pred, zero_division=0)), "acuracia": float(model.score(x_test, y_test))}
    payload = {"prevalencia": float(y.mean()), "sem_peso": pack(plain), "com_peso": pack(weighted)}
    return dump_json(destination, payload)
''',
    "curves": dump_json_fn() + '''
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score, precision_recall_curve, roc_curve
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    proba = LogisticRegression(max_iter=300).fit(x_train, y_train).predict_proba(x_test)[:, 1]
    payload = {
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "pr_auc": float(average_precision_score(y_test, proba)),
        "prevalencia": float(y_test.mean()),
        "leitura": "em classe rara, PR-AUC descreve melhor o valor do ranking",
    }
    return dump_json(destination, payload)
''',
    "baseline": dump_json_fn() + '''
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    dummy = DummyClassifier(strategy="most_frequent").fit(x_train, y_train)
    regra = (x_test.iloc[:, 0] > x_train.iloc[:, 0].median()).astype(int)
    model = LogisticRegression(max_iter=300).fit(x_train, y_train)
    payload = {
        "f1_dummy": float(f1_score(y_test, dummy.predict(x_test), zero_division=0)),
        "f1_regra": float(f1_score(y_test, regra, zero_division=0)),
        "f1_modelo": float(f1_score(y_test, model.predict(x_test), zero_division=0)),
    }
    return dump_json(destination, payload)
''',
}


ENGINE_UNSUPERVISED = {
    "kmeans": dump_json_fn() + '''
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    x = StandardScaler().fit_transform(frame)
    model = KMeans(n_clusters=3, n_init=10, random_state=42).fit(x)
    payload = {
        "k": 3,
        "inercia": float(model.inertia_),
        "tamanhos": pd.Series(model.labels_).value_counts().sort_index().to_dict(),
        "centroides": model.cluster_centers_.tolist(),
    }
    return dump_json(destination, payload)
''',
    "elbow": dump_json_fn() + '''
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    x = StandardScaler().fit_transform(pd.read_csv(source))
    rows = []
    for k in range(2, 8):
        model = KMeans(n_clusters=k, n_init=10, random_state=42).fit(x)
        rows.append({"k": k, "inercia": float(model.inertia_), "silhouette": float(silhouette_score(x, model.labels_))})
    melhor = max(rows, key=lambda r: r["silhouette"])
    payload = {"curva": rows, "k_recomendado": melhor["k"]}
    return dump_json(destination, payload)
''',
    "pca": dump_json_fn() + '''
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    x = StandardScaler().fit_transform(pd.read_csv(source))
    pca = PCA(n_components=2, random_state=42).fit(x)
    payload = {
        "variancia_explicada": pca.explained_variance_ratio_.tolist(),
        "variancia_acumulada": float(pca.explained_variance_ratio_.sum()),
        "n_componentes": 2,
    }
    return dump_json(destination, payload)
''',
    "hier": dump_json_fn() + '''
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    x = StandardScaler().fit_transform(pd.read_csv(source))
    model = AgglomerativeClustering(n_clusters=3, linkage="ward").fit(x)
    payload = {"k": 3, "tamanhos": pd.Series(model.labels_).value_counts().sort_index().to_dict(), "linkage": "ward"}
    return dump_json(destination, payload)
''',
    "iforest": dump_json_fn() + '''
from sklearn.ensemble import IsolationForest

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    model = IsolationForest(contamination=0.05, random_state=42).fit(frame)
    pred = model.predict(frame)
    scores = model.decision_function(frame)
    payload = {
        "n_anomalias": int((pred == -1).sum()),
        "taxa": float((pred == -1).mean()),
        "score_min": float(scores.min()),
        "score_max": float(scores.max()),
    }
    return dump_json(destination, payload)
''',
    "dbscan": dump_json_fn() + '''
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    x = StandardScaler().fit_transform(pd.read_csv(source))
    model = DBSCAN(eps=0.6, min_samples=8).fit(x)
    labels = model.labels_
    payload = {
        "n_clusters": int(len(set(labels)) - (1 if -1 in labels else 0)),
        "n_ruido": int((labels == -1).sum()),
        "tamanhos": pd.Series(labels).value_counts().sort_index().to_dict(),
    }
    return dump_json(destination, payload)
''',
    "tsne": dump_json_fn() + '''
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    x = StandardScaler().fit_transform(pd.read_csv(source))
    coords = TSNE(n_components=2, perplexity=15, random_state=42, init="pca", learning_rate="auto").fit_transform(x)
    payload = {"n": int(len(coords)), "x_min": float(coords[:, 0].min()), "x_max": float(coords[:, 0].max()), "y_min": float(coords[:, 1].min()), "y_max": float(coords[:, 1].max())}
    csv_path = destination.with_name("tsne.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(coords, columns=["x", "y"]).to_csv(csv_path, index=False)
    payload["arquivo"] = str(csv_path)
    return dump_json(destination, payload)
''',
    "persona": dump_json_fn() + '''
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
''',
    "nmf": dump_json_fn() + '''
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

def run(source: Path, destination: Path) -> dict[str, Any]:
    textos = pd.read_csv(source)["texto"].astype(str)
    vec = TfidfVectorizer(max_features=80)
    x = vec.fit_transform(textos)
    model = NMF(n_components=3, random_state=42, max_iter=400)
    model.fit(x)
    vocab = np.array(vec.get_feature_names_out())
    topicos = []
    for i, row in enumerate(model.components_):
        topicos.append({"topico": i, "termos": vocab[row.argsort()[-6:][::-1]].tolist()})
    payload = {"topicos": topicos, "n_documentos": int(len(textos))}
    return dump_json(destination, payload)
''',
}


ENGINE_TS = {
    "decomp": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source, parse_dates=["data"]).sort_values("data")
    y = frame["y"].to_numpy(dtype=float)
    period = 7
    seasonal = np.array([y[i::period].mean() for i in range(period)])
    seasonal = seasonal - seasonal.mean()
    seas = np.tile(seasonal, int(math.ceil(len(y) / period)))[: len(y)]
    kernel = np.ones(period) / period
    trend = np.convolve(y, kernel, mode="same")
    resid = y - trend - seas
    payload = {
        "n": int(len(y)),
        "periodo": period,
        "var_tendencia": float(np.var(trend)),
        "var_sazonal": float(np.var(seas)),
        "var_residuo": float(np.var(resid)),
    }
    return dump_json(destination, payload)
''',
    "naive": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    y = pd.read_csv(source, parse_dates=["data"]).sort_values("data")["y"].to_numpy(dtype=float)
    split = int(len(y) * 0.7)
    test = y[split:]
    naive = np.repeat(y[split - 1], len(test))
    sazonal = np.array([y[split - 7 + (i % 7)] for i in range(len(test))])
    def mae(a, b):
        return float(np.mean(np.abs(a - b)))
    payload = {"mae_naive": mae(test, naive), "mae_sazonal": mae(test, sazonal), "n_teste": int(len(test))}
    return dump_json(destination, payload)
''',
    "rolling": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    y = pd.read_csv(source, parse_dates=["data"]).sort_values("data")["y"].to_numpy(dtype=float)
    janela = 7
    preds, reals = [], []
    for t in range(janela, len(y)):
        preds.append(float(y[t - janela : t].mean()))
        reals.append(float(y[t]))
    mae = float(np.mean(np.abs(np.array(reals) - np.array(preds))))
    payload = {"mae": mae, "janela": janela, "n_previsoes": len(preds)}
    return dump_json(destination, payload)
''',
    "backtest": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    y = pd.read_csv(source, parse_dates=["data"]).sort_values("data")["y"].to_numpy(dtype=float)
    cortes = [int(len(y) * p) for p in (0.5, 0.65, 0.8)]
    linhas = []
    for cut in cortes:
        hist, future = y[:cut], y[cut : cut + 7]
        pred = np.repeat(hist[-1], len(future))
        linhas.append({"corte": int(cut), "mae": float(np.mean(np.abs(future - pred)))})
    payload = {"cortes": linhas, "mae_medio": float(np.mean([r["mae"] for r in linhas]))}
    return dump_json(destination, payload)
''',
    "break": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    y = pd.read_csv(source, parse_dates=["data"]).sort_values("data")["y"].to_numpy(dtype=float)
    best_i, best_stat = None, -1.0
    for i in range(10, len(y) - 10):
        a, b = y[:i], y[i:]
        se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        stat = abs(a.mean() - b.mean()) / se if se else 0
        if stat > best_stat:
            best_stat, best_i = stat, i
    payload = {"indice_quebra": int(best_i), "estatistica": float(best_stat), "media_antes": float(y[:best_i].mean()), "media_depois": float(y[best_i:].mean())}
    return dump_json(destination, payload)
''',
}


ENGINE_NLP = {
    "bow": dump_json_fn() + '''
from sklearn.feature_extraction.text import CountVectorizer

def run(source: Path, destination: Path) -> dict[str, Any]:
    textos = pd.read_csv(source)["texto"].astype(str)
    vec = CountVectorizer(max_features=50)
    x = vec.fit_transform(textos)
    freq = np.asarray(x.sum(axis=0)).ravel()
    vocab = vec.get_feature_names_out()
    top = sorted(zip(vocab, freq), key=lambda t: -t[1])[:10]
    payload = {"n_documentos": int(x.shape[0]), "n_termos": int(x.shape[1]), "top_termos": [{"termo": t, "n": int(c)} for t, c in top]}
    return dump_json(destination, payload)
''',
    "tfidf": dump_json_fn() + '''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def run(source: Path, destination: Path) -> dict[str, Any]:
    textos = pd.read_csv(source)["texto"].astype(str)
    x = TfidfVectorizer(max_features=80).fit_transform(textos)
    sim = cosine_similarity(x)
    np.fill_diagonal(sim, 0)
    i, j = np.unravel_index(sim.argmax(), sim.shape)
    payload = {"par_mais_similar": [int(i), int(j)], "similaridade": float(sim[i, j]), "n": int(len(textos))}
    return dump_json(destination, payload)
''',
    "textclf": dump_json_fn() + '''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    x_train, x_test, y_train, y_test = train_test_split(frame["texto"], frame["fila"], test_size=0.3, random_state=42, stratify=frame["fila"])
    pipe = Pipeline([("tfidf", TfidfVectorizer(max_features=120)), ("clf", LinearSVC())])
    pipe.fit(x_train, y_train)
    pred = pipe.predict(x_test)
    payload = {"macro_f1": float(f1_score(y_test, pred, average="macro")), "classes": sorted(frame["fila"].unique().tolist())}
    return dump_json(destination, payload)
''',
    "sent": dump_json_fn() + '''
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
''',
    "search": dump_json_fn() + '''
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
''',
}


ENGINE_MLOPS = {
    "drift": dump_json_fn() + '''
def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    qs = np.linspace(0, 1, bins + 1)
    edges = np.unique(np.quantile(expected, qs))
    if len(edges) < 3:
        return 0.0
    e = np.clip(np.histogram(expected, bins=edges)[0] / len(expected), 1e-6, None)
    a = np.clip(np.histogram(actual, bins=edges)[0] / len(actual), 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))

def run(source: Path, destination: Path) -> dict[str, Any]:
    treino = pd.read_csv(source)
    atual = pd.read_csv(source.with_name("atual.csv"))
    colunas = [c for c in treino.columns if c in atual.columns and np.issubdtype(treino[c].dtype, np.number)]
    rel = {c: psi(treino[c].dropna().to_numpy(), atual[c].dropna().to_numpy()) for c in colunas}
    payload = {"psi": rel, "alerta": [c for c, v in rel.items() if v > 0.2]}
    return dump_json(destination, payload)
''',
    "fair": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    taxas = frame.groupby("grupo")["aprovado"].mean().to_dict()
    vals = list(taxas.values())
    razao = min(vals) / max(vals) if max(vals) else None
    payload = {"taxas": {str(k): float(v) for k, v in taxas.items()}, "razao_disparidade": razao, "limiar_80": razao is not None and razao >= 0.8}
    return dump_json(destination, payload)
''',
    "perm": dump_json_fn() + '''
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=80, random_state=42).fit(x_train, y_train)
    perm = permutation_importance(model, x_test, y_test, n_repeats=8, random_state=42)
    payload = {
        "nativa": dict(zip(x.columns, model.feature_importances_.tolist())),
        "permutacao": dict(zip(x.columns, perm.importances_mean.tolist())),
    }
    return dump_json(destination, payload)
''',
    "card": dump_json_fn() + '''
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
        f"# Model card\\n\\n- Uso pretendido: score educacional de churn.\\n- Dados: sintéticos, n={len(frame)}.\\n- Métrica: ROC-AUC {auc:.3f} no holdout.\\n- Limites: não usar em produção nem com dado pessoal real.\\n- Grupos: avaliação de fairness não inclusa neste cartão.\\n",
        encoding="utf-8",
    )
    payload = {"auc": auc, "model_card": str(md), "n_treino": int(len(x_train))}
    return dump_json(destination, payload)
''',
    "registry": dump_json_fn() + '''
from sklearn.linear_model import LogisticRegression
import hashlib, pickle

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    model = LogisticRegression(max_iter=300).fit(x, y)
    blob = pickle.dumps(model)
    digest = hashlib.sha256(blob).hexdigest()
    art = destination.with_name("model.pkl")
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_bytes(blob)
    registro = {"versao": "v1", "sha256": digest, "n": int(len(frame)), "features": list(x.columns), "artefato": str(art)}
    return dump_json(destination, registro)
''',
    "monitor": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source, parse_dates=["data"])
    daily = frame.groupby("data")["score"].agg(["mean", "std", "count"]).reset_index()
    baseline = float(daily["mean"].iloc[:7].mean())
    daily["alerta"] = (daily["mean"] < baseline - 0.08).astype(int)
    daily["data"] = daily["data"].astype(str)
    payload = {"baseline": baseline, "dias_alerta": int(daily["alerta"].sum()), "serie": daily.tail(10).to_dict(orient="records")}
    return dump_json(destination, payload)
''',
    "cost": dump_json_fn() + '''
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    proba = LogisticRegression(max_iter=300).fit(x_train, y_train).predict_proba(x_test)[:, 1]
    custo_fp, custo_fn = 8, 40
    melhor = None
    for thr in np.linspace(0.1, 0.9, 17):
        pred = (proba >= thr).astype(int)
        fp = int(((pred == 1) & (y_test == 0)).sum())
        fn = int(((pred == 0) & (y_test == 1)).sum())
        custo = fp * custo_fp + fn * custo_fn
        cand = {"threshold": round(float(thr), 2), "custo": custo, "fp": fp, "fn": fn}
        if melhor is None or cand["custo"] < melhor["custo"]:
            melhor = cand
    payload = {"melhor": melhor, "custo_fp": custo_fp, "custo_fn": custo_fn}
    return dump_json(destination, payload)
''',
    "retrain": dump_json_fn() + '''
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source, parse_dates=["data"]).sort_values("data")
    y = frame["y"].to_numpy()
    t = np.arange(len(y)).reshape(-1, 1)
    cut = int(len(y) * 0.5)
    frozen = LinearRegression().fit(t[:cut], y[:cut])
    erros_freeze, erros_retrain = [], []
    for end in range(cut, len(y) - 7, 7):
        future_t, future_y = t[end : end + 7], y[end : end + 7]
        erros_freeze.append(mean_absolute_error(future_y, frozen.predict(future_t)))
        model = LinearRegression().fit(t[:end], y[:end])
        erros_retrain.append(mean_absolute_error(future_y, model.predict(future_t)))
    payload = {"mae_freeze": float(np.mean(erros_freeze)), "mae_retrain": float(np.mean(erros_retrain))}
    payload["recomendacao"] = "retreinar" if payload["mae_retrain"] < payload["mae_freeze"] else "congelar"
    return dump_json(destination, payload)
''',
}


ENGINE_E2E = {
    "churn": dump_json_fn() + '''
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["churn"]
    x = frame.drop(columns=["churn"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=300))])
    pipe.fit(x_train, y_train)
    proba = pipe.predict_proba(x_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    md = destination.with_name("model_card.md")
    md.parent.mkdir(parents=True, exist_ok=True)
    auc = float(roc_auc_score(y_test, proba))
    md.write_text(f"# Churn\\n\\nROC-AUC {auc:.3f}. Dado sintético. Não usar em produção.\\n", encoding="utf-8")
    payload = {"auc": auc, "f1": float(f1_score(y_test, pred)), "n": int(len(frame)), "model_card": str(md)}
    return dump_json(destination, payload)
''',
    "demand": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source, parse_dates=["data"]).sort_values("data")
    y = frame["y"].to_numpy(dtype=float)
    split = int(len(y) * 0.75)
    test = y[split:]
    naive = np.repeat(y[split - 1], len(test))
    roll = np.array([y[split - 7 + i : split + i].mean() if i == 0 else np.concatenate([y[split - 7 + i : split], test[:i]]).mean() for i in range(len(test))])
    payload = {
        "mae_naive": float(np.mean(np.abs(test - naive))),
        "mae_rolling": float(np.mean(np.abs(test - roll))),
        "n_teste": int(len(test)),
    }
    fig_dir = destination.parent / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(y, label="real")
    ax.axvline(split, color="#FBBF24")
    fig.tight_layout()
    fig.savefig(fig_dir / "serie.png", dpi=110)
    plt.close(fig)
    payload["figura"] = str(fig_dir / "serie.png")
    return dump_json(destination, payload)
''',
    "credit": dump_json_fn() + '''
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import hashlib, pickle

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["inadimplente"]
    grupo = frame["grupo"]
    x = frame.drop(columns=["inadimplente", "grupo"])
    x_train, x_test, y_train, y_test, g_train, g_test = train_test_split(x, y, grupo, test_size=0.3, random_state=42, stratify=y)
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=300))])
    pipe.fit(x_train, y_train)
    proba = pipe.predict_proba(x_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    taxas = pd.Series(pred, index=g_test.index).groupby(g_test).mean().to_dict()
    vals = list(taxas.values())
    razao = min(vals) / max(vals) if max(vals) else None
    art = destination.with_name("score.pkl")
    art.parent.mkdir(parents=True, exist_ok=True)
    blob = pickle.dumps(pipe)
    art.write_bytes(blob)
    payload = {
        "auc": float(roc_auc_score(y_test, proba)),
        "taxas_grupo": {str(k): float(v) for k, v in taxas.items()},
        "razao_disparidade": razao,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "artefato": str(art),
    }
    return dump_json(destination, payload)
''',
    "recsys": dump_json_fn() + '''
def run(source: Path, destination: Path) -> dict[str, Any]:
    inter = pd.read_csv(source)
    mat = pd.crosstab(inter["usuario_id"], inter["item_id"])
    items = mat.columns.to_numpy()
    x = mat.to_numpy(dtype=float)
    norms = np.linalg.norm(x, axis=0, keepdims=True)
    norms[norms == 0] = 1
    sim = (x.T @ x) / (norms.T @ norms)
    np.fill_diagonal(sim, 0)
    topn = {}
    for i, item in enumerate(items):
        idx = sim[i].argsort()[::-1][:3]
        topn[str(item)] = [str(items[j]) for j in idx]
    cobertos = set(inter["usuario_id"])
    payload = {"n_usuarios": int(mat.shape[0]), "n_itens": int(mat.shape[1]), "topn": topn, "cobertura_usuarios": int(len(cobertos))}
    return dump_json(destination, payload)
''',
    "tickets": dump_json_fn() + '''
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
''',
    "lab": dump_json_fn() + '''
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import hashlib, pickle

def psi(expected, actual, bins=8):
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    e = np.clip(np.histogram(expected, bins=edges)[0] / len(expected), 1e-6, None)
    a = np.clip(np.histogram(actual, bins=edges)[0] / len(actual), 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=300))])
    pipe.fit(x_train, y_train)
    auc = float(roc_auc_score(y_test, pipe.predict_proba(x_test)[:, 1]))
    drift = {c: psi(x_train[c].to_numpy(), x_test[c].to_numpy()) for c in x.columns}
    blob = pickle.dumps(pipe)
    art = destination.with_name("lab_model.pkl")
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_bytes(blob)
    card = destination.with_name("model_card.md")
    card.write_text(f"# Laboratório local\\n\\nAUC {auc:.3f}. Seed 42. Dado sintético.\\n", encoding="utf-8")
    payload = {
        "auc": auc,
        "drift": drift,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "artefato": str(art),
        "model_card": str(card),
        "linhas": int(len(frame)),
        "nulos": {c: int(frame[c].isna().sum()) for c in frame.columns},
    }
    return dump_json(destination, payload)
''',
}


EXPECTED_KEYS = {
    "wrangle": ["linhas"],
    "eda": [],
    "sql": [],
    "stats": [],
    "features": [],
    "supervised": [],
    "unsupervised": [],
    "timeseries": [],
    "nlp": [],
    "mlops": [],
    "e2e": [],
}

FAMILY_KEYS = {
    1: ["linhas", "colunas"],
    2: ["falhas_coercao"],
    3: ["por_coluna"],
    4: ["n_outliers", "media_winsor"],
    5: ["n_meses"],
    6: ["match_rate"],
    7: ["receita_total"],
    8: ["seed", "correlacao_renda_alvo"],
    9: ["hashes_iguais"],
    10: ["perfil"],
    11: ["media", "mediana"],
    12: ["pearson"],
    13: ["resumo"],
    14: ["n_niveis"],
    15: ["skus_80"],
    16: ["grupos"],
    17: ["por_coluna"],
    18: ["relatorio"],
    19: ["conversao", "ticket"],
    20: ["figuras"],
    21: ["receita", "sqlite"],
    22: ["ranking"],
    23: ["matriz"],
    24: ["funil"],
    25: ["n_clientes"],
    26: ["linhas"],
    27: ["n_amostra"],
    28: ["linhas_longas"],
    29: ["joins_com_futuro"],
    30: ["dicionario"],
    31: ["features"],
    32: ["passou"],
    33: ["view"],
    34: ["colunas"],
    35: ["mediana", "mad"],
    36: ["ic_conversao"],
    37: ["t", "p_valor"],
    38: ["chi2"],
    39: ["inversao"],
    40: ["p_valor", "conversao_b"],
    41: ["n_por_variante"],
    42: ["ic_bootstrap"],
    43: ["u", "p_valor"],
    44: ["reducao"],
    45: ["significativos_fdr"],
    46: ["falso_positivo_peeking"],
    47: ["onehot_dim"],
    48: ["scalers"],
    49: ["bordas_quantil"],
    50: ["n_feriados"],
    51: ["corr_cv"],
    52: ["acuracia_holdout"],
    53: ["diferenca"],
    54: ["top"],
    55: ["r2_interacao"],
    56: ["acuracias"],
    57: ["r2", "rmse"],
    58: ["mae", "mape"],
    59: ["acuracia", "odds"],
    60: ["melhor"],
    61: ["regras"],
    62: ["acuracia_floresta"],
    63: ["acuracia_gb"],
    64: ["media", "folds"],
    65: ["com_peso"],
    66: ["roc_auc", "pr_auc"],
    67: ["f1_modelo"],
    68: ["inercia", "k"],
    69: ["k_recomendado"],
    70: ["variancia_explicada"],
    71: ["tamanhos"],
    72: ["n_anomalias"],
    73: ["n_clusters"],
    74: ["arquivo"],
    75: ["personas"],
    76: ["topicos"],
    77: ["var_tendencia"],
    78: ["mae_naive"],
    79: ["mae"],
    80: ["mae_medio"],
    81: ["indice_quebra"],
    82: ["top_termos"],
    83: ["similaridade"],
    84: ["macro_f1"],
    85: ["f1_modelo"],
    86: ["top"],
    87: ["psi"],
    88: ["razao_disparidade"],
    89: ["permutacao"],
    90: ["model_card"],
    91: ["sha256"],
    92: ["dias_alerta"],
    93: ["melhor"],
    94: ["recomendacao"],
    95: ["auc"],
    96: ["mae_rolling"],
    97: ["auc", "razao_disparidade"],
    98: ["topn"],
    99: ["macro_f1_fila"],
    100: ["auc", "sha256"],
}


def requirements_for(spec: dict) -> str:
    techs = spec["tecnologias"]
    lines = ["pandas>=2.0", "numpy>=1.24"]
    if any("scikit-learn" in t or "sklearn" in t for t in techs) or spec["family"] in {
        "features",
        "supervised",
        "unsupervised",
        "nlp",
        "mlops",
        "e2e",
    }:
        lines.append("scikit-learn>=1.3")
    if any("matplotlib" in t for t in techs) or spec["family"] == "eda" or spec["params"].get("kind") in {"demand", "lab"}:
        lines.append("matplotlib>=3.7")
    lines.append("pytest>=7.0")
    return "\n".join(lines) + "\n"


def extra_assert(spec: dict) -> str:
    n = spec["numero"]
    extras = {
        9: "    assert result['hashes_iguais'] is True\n",
        32: "    assert 'falhas' in result\n",
        39: "    assert 'por_grupo' in result\n",
        40: "    assert 0 <= result['p_valor'] <= 1\n",
        57: "    assert result['r2'] > 0.5\n",
        59: "    assert result['acuracia'] > 0.6\n",
        68: "    assert result['k'] == 3\n",
        95: "    assert result['auc'] > 0.7\n",
        100: "    assert result['auc'] > 0.7\n",
    }
    return extras.get(n, "")


def render_readme(spec: dict) -> str:
    n = spec["numero"]
    anterior = spec["projeto_anterior"]
    ant_txt = "nenhum" if anterior is None else f"{anterior:03d}"
    fluxo = " → ".join(spec["fluxo"])
    techs = ", ".join(spec["tecnologias"])
    conceitos = ", ".join(spec["conceitos"])
    nivel = NIVEL_LABEL[spec["nivel"]]
    return f"""# {n:03d} — {spec['titulo']}

Material educacional de Ciência de Dados. Projeto anterior recomendado: {ant_txt}. Os clientes, valores e textos deste exercício são fictícios.

## Descrição

Este projeto {spec['objetivo_aprendizagem'][0].lower() + spec['objetivo_aprendizagem'][1:]} O fluxo local é {fluxo}.

## Problema

{spec['problema']}

## Objetivos de aprendizagem

- Praticar {conceitos}.
- Entregar um artefato JSON (e arquivos auxiliares quando o problema pede) a partir de um CSV sintético.
- Explicar a decisão técnica e a limitação antes de copiar o desenho para um ambiente real.

## Conceitos de Ciência de Dados

{conceitos.capitalize()}. Nível {nivel}. O código roda offline, com seed quando há aleatoriedade.

## Tecnologias

{techs}. Sem conta paga. Docker não é necessário.

## Arquitetura

{fluxo}.

![Arquitetura](assets/architecture.png)

## Estrutura de diretórios

```text
{n:03d}-{spec['slug']}/
  src/main.py
  src/engine.py
  tests/test_engine.py
  data/entrada.csv
  assets/architecture.png
  requirements.txt
  .env.example
```

## Pré-requisitos

Python 3.11+ no PATH. Instale as bibliotecas do `requirements.txt`.

## Instalação e configuração

```powershell
cd {n:03d}-{spec['slug']}
copy .env.example .env
python -m pip install -r requirements.txt
```

Os caminhos do exemplo apontam para a amostra versionada e para a pasta `out/`.

## Como executar

```powershell
python src/main.py --entrada data/entrada.csv --saida out/resultado.json
```

A CLI responde em português. Arquivo ausente termina com código 1.

## Como validar

```powershell
pytest
```

Os testes cobrem o resultado da função `run` e a CLI com a amostra versionada.

## Exemplos de entrada e saída

A entrada é o CSV sintético em `data/entrada.csv`. A saída é um JSON em `out/resultado.json` com as chaves do problema — por exemplo o resumo, a métrica ou o artefato gerado.

## Decisões técnicas

O motor fica em `src/engine.py` para o `main.py` só cuidar de CLI, log e código de saída. Seed 42 quando há amostragem ou modelo. Dado sintético de propósito, para o exercício ser reproduzível sem rede.

## Limitações

É uma demonstração educacional. Não há serviço em produção, dado pessoal real, monitoramento 24h nem garantia de poder estatístico fora desta amostra.

## Melhorias sugeridas

Trocar o CSV sintético por um extract interno (anonimizado), acrescentar um relatório em HTML e versionar o artefato fora da pasta do exercício.

## Aplicação empresarial

{spec['aplicacao_empresarial']}

## Competências para o portfólio

Mostre o problema, a decisão no código e a limitação. Aponte o teste e a imagem de arquitetura desta pasta.
"""


def make_dataframe(spec: dict, rng: np.random.Generator) -> dict[str, pd.DataFrame]:
    n = spec["numero"]
    family = spec["family"]
    kind = spec["params"].get("kind") or spec["params"].get("ops", [None])[0] or spec["params"].get("chart") or spec["params"].get("test") or spec["params"].get("model")

    def vendas(k=240):
        data = pd.date_range("2024-01-01", periods=k, freq="D")
        return pd.DataFrame({
            "pedido_id": np.arange(1, k + 1),
            "data": data.strftime("%Y-%m-%d"),
            "cliente_id": rng.integers(1, 80, k),
            "sku": rng.choice(["SKU-A", "SKU-B", "SKU-C", "SKU-D", "SKU-E"], k),
            "categoria": rng.choice(["cafe", "cha", "doce"], k),
            "canal": rng.choice(["pago", "organico", "loja"], k),
            "uf": rng.choice(["SP", "RJ", "MG", "BA", "RS"], k),
            "quantidade": rng.integers(1, 8, k),
            "receita": np.round(rng.lognormal(3.2, 0.45, k), 2),
            "ticket": np.round(rng.lognormal(3.0, 0.5, k), 2),
            "custo": np.round(rng.lognormal(2.6, 0.4, k), 2),
            "preco": np.round(rng.uniform(8, 90, k), 2),
        })

    if n == 2:
        frame = vendas()
        frame["receita"] = frame["receita"].astype(str).str.replace(".", ",", regex=False)
        return {"entrada.csv": frame}
    if n == 3:
        frame = pd.DataFrame({
            "cliente_id": np.arange(1, 201),
            "renda": rng.normal(4200, 1500, 200),
            "uf": rng.choice(["SP", "RJ", "AM"], 200),
            "adesao": pd.date_range("2022-01-01", periods=200, freq="D").strftime("%Y-%m-%d"),
        })
        frame.loc[rng.choice(200, 35, False), "renda"] = np.nan
        frame.loc[rng.choice(200, 12, False), "adesao"] = np.nan
        return {"entrada.csv": frame}
    if n == 6:
        pedidos = vendas(180)
        clientes = pd.DataFrame({
            "cliente_id": np.arange(1, 90),
            "segmento": rng.choice(["bronze", "prata", "ouro"], 89),
        })
        return {"entrada.csv": pedidos, "clientes.csv": clientes}
    if n == 8:
        return {"entrada.csv": pd.DataFrame({"n": [400], "seed": [8], "nulos": [0.05]})}  # overwritten below
    if n == 8:
        pass
    if n == 13:
        return {"entrada.csv": pd.DataFrame({
            "segmento": rng.choice(["premium", "plus", "basic"], 220),
            "gasto": np.round(rng.lognormal(4.2, 0.5, 220), 2),
        })}
    if n == 16:
        canal = rng.choice(["pago", "organico"], 300)
        p = np.where(canal == "pago", 0.18, 0.11)
        return {"entrada.csv": pd.DataFrame({"canal": canal, "converteu": rng.binomial(1, p)})}
    if n == 17:
        uf = rng.choice(["SP", "AM", "RS"], 240)
        renda = rng.normal(5000, 1200, 240)
        frame = pd.DataFrame({"uf": uf, "renda": renda, "idade": rng.integers(18, 70, 240)})
        frame.loc[frame["uf"].eq("AM") & (rng.random(240) < 0.35), "renda"] = np.nan
        return {"entrada.csv": frame}
    if n == 19:
        return {"entrada.csv": pd.DataFrame({
            "visitante_id": np.arange(1, 401),
            "comprou": rng.binomial(1, 0.12, 400),
            "receita": np.round(rng.lognormal(3.4, 0.4, 400), 2),
            "retido_d7": rng.binomial(1, 0.4, 400),
        })}
    if n == 23:
        rows = []
        for cid in range(1, 61):
            start = pd.Timestamp("2024-01-01") + pd.Timedelta(days=int(rng.integers(0, 80)))
            for k in range(int(rng.integers(1, 6))):
                rows.append({"cliente_id": cid, "data": (start + pd.Timedelta(days=30 * k)).strftime("%Y-%m-%d"), "pedido_id": f"{cid}-{k}", "receita": float(rng.uniform(20, 200))})
        return {"entrada.csv": pd.DataFrame(rows)}
    if n == 24:
        rows = []
        for uid in range(1, 201):
            rows.append({"usuario_id": uid, "etapa": "visita"})
            if rng.random() < 0.55:
                rows.append({"usuario_id": uid, "etapa": "cadastro"})
                if rng.random() < 0.5:
                    rows.append({"usuario_id": uid, "etapa": "checkout"})
                    if rng.random() < 0.6:
                        rows.append({"usuario_id": uid, "etapa": "compra"})
        return {"entrada.csv": pd.DataFrame(rows)}
    if n == 28:
        meses = [f"2024-{m:02d}" for m in range(1, 7)]
        data = {"sku": [f"SKU-{i}" for i in range(1, 13)], "categoria": rng.choice(["cafe", "cha"], 12)}
        for mes in meses:
            data[mes] = np.round(rng.uniform(40, 400, 12), 2)
        return {"entrada.csv": pd.DataFrame(data)}
    if n == 29:
        eventos = pd.DataFrame({
            "cliente_id": rng.integers(1, 40, 120),
            "evento_em": pd.date_range("2024-03-01", periods=120, freq="D"),
            "receita": np.round(rng.uniform(10, 90, 120), 2),
        })
        cadastro = pd.DataFrame({
            "cliente_id": np.repeat(np.arange(1, 40), 2),
            "vigente_em": list(pd.date_range("2024-01-01", periods=39, freq="5D")) + list(pd.date_range("2024-04-01", periods=39, freq="5D")),
            "segmento": rng.choice(["a", "b"], 78),
        })
        return {"entrada.csv": eventos, "cadastro.csv": cadastro}
    if n == 33:
        pedidos = vendas(80)[["pedido_id", "data", "cliente_id"]]
        itens = pd.DataFrame({
            "pedido_id": np.repeat(pedidos["pedido_id"].to_numpy(), 2)[:120],
            "sku": rng.choice(["A", "B", "C"], 120),
            "quantidade": rng.integers(1, 4, 120),
            "preco": np.round(rng.uniform(8, 40, 120), 2),
        })
        return {"entrada.csv": pedidos, "itens.csv": itens}
    if n == 36:
        return {"entrada.csv": pd.DataFrame({"converteu": rng.binomial(1, 0.14, 280), "ticket": np.round(rng.lognormal(3.1, 0.4, 280), 2)})}
    if n == 38:
        disp = rng.choice(["mobile", "desktop"], 320)
        p = np.where(disp == "mobile", 0.09, 0.16)
        return {"entrada.csv": pd.DataFrame({"dispositivo": disp, "converteu": rng.binomial(1, p)})}
    if n == 39:
        x_a = rng.uniform(0, 10, 120)
        y_a = 30 + 1.5 * x_a + rng.normal(0, 1, 120)
        x_b = rng.uniform(10, 20, 120)
        y_b = -10 + 1.5 * x_b + rng.normal(0, 1, 120)
        return {"entrada.csv": pd.DataFrame({
            "grupo": ["norte"] * 120 + ["sul"] * 120,
            "x": np.concatenate([x_a, x_b]),
            "y": np.concatenate([y_a, y_b]),
        })}
    if n == 41:
        return {"entrada.csv": pd.DataFrame({"converteu": rng.binomial(1, 0.12, 400)})}
    if n == 40:
        var = np.array(["A"] * 200 + ["B"] * 200)
        p = np.where(var == "B", 0.18, 0.11)
        return {"entrada.csv": pd.DataFrame({"variante": var, "converteu": rng.binomial(1, p)})}
    if n == 43:
        plano = np.array(["plus"] * 90 + ["basic"] * 110)
        gasto = np.concatenate([rng.lognormal(4.3, 0.4, 90), rng.lognormal(3.7, 0.5, 110)])
        return {"entrada.csv": pd.DataFrame({"plano": plano, "gasto": gasto})}
    if n == 44:
        x_pre = rng.normal(50, 10, 300)
        variante = np.array(["A"] * 150 + ["B"] * 150)
        y = 0.7 * x_pre + np.where(variante == "B", 4, 0) + rng.normal(0, 5, 300)
        return {"entrada.csv": pd.DataFrame({"x_pre": x_pre, "y": y, "variante": variante})}
    if n == 45:
        pvals = np.concatenate([rng.uniform(0.0001, 0.04, 4), rng.uniform(0.1, 0.9, 16)])
        return {"entrada.csv": pd.DataFrame({"hipotese": [f"h{i}" for i in range(20)], "p_valor": pvals})}
    if n == 46:
        return {"entrada.csv": pd.DataFrame({"x": rng.normal(0, 1, 120)})}
    if n in {47}:
        return {"entrada.csv": pd.DataFrame({"uf": rng.choice(["SP", "RJ", "MG"], 180), "canal": rng.choice(["pago", "loja"], 180), "alvo": rng.binomial(1, 0.3, 180)})}
    if n == 48:
        return {"entrada.csv": pd.DataFrame({"renda": rng.normal(5000, 1800, 200), "idade": rng.integers(18, 70, 200)})}
    if n == 49:
        return {"entrada.csv": pd.DataFrame({"idade": rng.integers(18, 80, 200)})}
    if n == 51:
        cidade = rng.choice(["A", "B", "C", "D"], 280)
        base = {"A": 0.2, "B": 0.35, "C": 0.5, "D": 0.15} 
        alvo = rng.binomial(1, [base[c] for c in cidade])
        return {"entrada.csv": pd.DataFrame({"cidade": cidade, "alvo": alvo})}
    if n == 59:
        x1 = rng.normal(0, 1, 280)
        x2 = rng.normal(0, 1, 280)
        x3 = rng.normal(0, 1, 280)
        logit = 1.3 * x1 - 0.9 * x2 + 0.4 * x3
        y = (logit + rng.normal(0, 0.5, 280) > 0).astype(int)
        return {"entrada.csv": pd.DataFrame({"x1": x1, "x2": x2, "x3": x3, "churn": y})}
    if n in {52, 54, 56, 60, 61, 62, 63, 64, 66, 67, 89, 90, 91, 93, 100}:
        x1 = rng.normal(0, 1, 280)
        x2 = rng.normal(0, 1, 280)
        x3 = rng.normal(0, 1, 280)
        logit = 1.3 * x1 - 0.9 * x2 + 0.4 * x3
        y = (logit + rng.normal(0, 0.5, 280) > 0).astype(int)
        frame = pd.DataFrame({"x1": x1, "x2": x2, "x3": x3, "alvo": y})
        if n == 56:
            frame.loc[rng.choice(280, 40, False), "x1"] = np.nan
        if n == 52:
            frame["uf"] = rng.choice(["SP", "RJ"], 280)
        return {"entrada.csv": frame}
    if n == 53:
        rows = []
        for cid in range(1, 40):
            for d in pd.date_range("2024-01-01", periods=12, freq="7D"):
                rows.append({"cliente_id": cid, "data": d.strftime("%Y-%m-%d"), "receita": float(rng.uniform(10, 80))})
        return {"entrada.csv": pd.DataFrame(rows)}
    if n == 55:
        preco = rng.uniform(10, 40, 220)
        cat = rng.integers(0, 3, 220)
        y = 80 - 1.2 * preco + 6 * cat * (preco > 25) + rng.normal(0, 4, 220)
        return {"entrada.csv": pd.DataFrame({"preco": preco, "categoria_code": cat, "y": y})}
    if n == 57:
        area = rng.uniform(40, 180, 220)
        quartos = rng.integers(1, 5, 220)
        idade = rng.integers(0, 40, 220)
        preco = 80 + 2.4 * area + 18 * quartos - 0.9 * idade + rng.normal(0, 12, 220)
        return {"entrada.csv": pd.DataFrame({"area": area, "quartos": quartos, "idade": idade, "preco": preco})}
    if n == 58:
        x = rng.normal(0, 1, (200, 3))
        y = 10 + x @ np.array([4.0, -2.0, 1.5]) + rng.normal(0, 1.2, 200)
        return {"entrada.csv": pd.DataFrame(x, columns=["a", "b", "c"]).assign(y=y)}
    if n == 65:
        x1 = rng.normal(0, 1, 400)
        x2 = rng.normal(0, 1, 400)
        logit = 2.2 * x1 - 1.1 * x2 - 2.4
        y = (logit + rng.normal(0, 0.4, 400) > 0).astype(int)
        return {"entrada.csv": pd.DataFrame({"x1": x1, "x2": x2, "fraude": y})}
    if n in {68, 69, 70, 71, 73, 74}:
        centers = np.array([[0, 0], [4, 4], [-3, 3]])
        pieces = [rng.normal(c, 0.55, (70, 2)) for c in centers]
        x = np.vstack(pieces)
        return {"entrada.csv": pd.DataFrame(x, columns=["f1", "f2"])}
    if n == 72:
        normal = rng.normal(0, 1, (220, 3))
        anom = rng.normal(6, 0.4, (12, 3))
        return {"entrada.csv": pd.DataFrame(np.vstack([normal, anom]), columns=["a", "b", "c"])}
    if n == 75:
        return {"entrada.csv": pd.DataFrame({
            "recencia": rng.integers(1, 80, 180),
            "frequencia": rng.integers(1, 20, 180),
            "valor": np.round(rng.lognormal(5, 0.5, 180), 2),
        })}
    if n in {76, 82, 83, 86}:
        textos = [
            "atraso na entrega do pedido de cafe",
            "produto veio quebrado e o suporte foi lento",
            "adorei o cafe gourmet chegou rapido",
            "cobranca duplicada no cartao",
            "troca de endereco nao atualizou",
            "app travando no checkout",
            "excelente atendimento resolveram na hora",
            "embalagem amassada mas o item ok",
            "quero cancelar a assinatura",
            "promoção não aplicou o cupom",
        ]
        extra = textos * 8
        rng.shuffle(extra)
        return {"entrada.csv": pd.DataFrame({"texto": extra[:80]})}
    if n in {84, 99}:
        filas = ["logistica", "financeiro", "produto"]
        base = {
            "logistica": ["atraso entrega pedido transportadora", "rastreio parado", "pacote perdido"],
            "financeiro": ["cobranca duplicada fatura", "estorno cartao", "boleto vencido"],
            "produto": ["app travando checkout", "bug login", "tela branca"],
        }
        rows = []
        for _ in range(90):
            fila = filas[_ % 3]
            rows.append({"texto": rng.choice(base[fila]) + " " + rng.choice(["urgente", "cliente", "hoje"]), "fila": fila})
        return {"entrada.csv": pd.DataFrame(rows)}
    if n == 85:
        rows = []
        for txt, lab in [("adorei o produto otimo", "positivo"), ("ruim pessimo atraso", "negativo"), ("ok chegou", "neutro")] * 30:
            rows.append({"texto": txt, "sentimento": lab})
        return {"entrada.csv": pd.DataFrame(rows)}
    if n in {77, 78, 79, 80, 81, 94, 96}:
        t = np.arange(140)
        y = 40 + 0.08 * t + 6 * np.sin(2 * math.pi * t / 7) + rng.normal(0, 1.2, 140)
        if n == 81:
            y[80:] += 12
        return {"entrada.csv": pd.DataFrame({"data": pd.date_range("2024-01-01", periods=140, freq="D").strftime("%Y-%m-%d"), "y": y})}
    if n == 87:
        treino = pd.DataFrame({"renda": rng.normal(5000, 800, 200), "idade": rng.normal(35, 8, 200)})
        atual = pd.DataFrame({"renda": rng.normal(6200, 900, 200), "idade": rng.normal(36, 8, 200)})
        return {"entrada.csv": treino, "atual.csv": atual}
    if n == 88:
        grupo = np.array(["A"] * 120 + ["B"] * 120)
        aprovado = np.concatenate([rng.binomial(1, 0.62, 120), rng.binomial(1, 0.41, 120)])
        return {"entrada.csv": pd.DataFrame({"grupo": grupo, "aprovado": aprovado})}
    if n == 92:
        datas = pd.date_range("2024-01-01", periods=40, freq="D")
        score = np.concatenate([rng.normal(0.62, 0.04, 25), rng.normal(0.48, 0.04, 15)])
        return {"entrada.csv": pd.DataFrame({"data": datas.strftime("%Y-%m-%d"), "score": score})}
    if n == 95:
        tenure = rng.integers(1, 36, 260)
        tickets = rng.poisson(2.0, 260)
        gasto = rng.lognormal(4, 0.4, 260)
        logit = 0.8 + 0.55 * tickets - 0.09 * tenure - 0.004 * gasto
        churn = (logit + rng.normal(0, 0.35, 260) > 0).astype(int)
        return {"entrada.csv": pd.DataFrame({"tenure": tenure, "tickets": tickets, "gasto": gasto, "churn": churn})}
    if n == 97:
        grupo = rng.choice(["A", "B"], 260)
        renda = rng.normal(4500, 1200, 260)
        atraso = rng.poisson(1.1, 260)
        logit = -2.2 + 0.0004 * (5000 - renda) + 0.35 * atraso + np.where(grupo == "B", 0.4, 0)
        y = (logit + rng.normal(0, 0.45, 260) > 0).astype(int)
        return {"entrada.csv": pd.DataFrame({"renda": renda, "atraso": atraso, "idade": rng.integers(21, 70, 260), "grupo": grupo, "inadimplente": y})}
    if n == 98:
        rows = []
        for u in range(1, 41):
            for item in rng.choice(np.arange(1, 16), size=int(rng.integers(3, 8)), replace=False):
                rows.append({"usuario_id": u, "item_id": int(item)})
        return {"entrada.csv": pd.DataFrame(rows)}
    if n == 31:
        return {"entrada.csv": vendas(200)}
    if n == 32:
        frame = vendas(120)
        frame.loc[5, "pedido_id"] = frame.loc[4, "pedido_id"]
        return {"entrada.csv": frame}
    if n == 50:
        return {"entrada.csv": vendas(100)}
    if family in {"sql", "wrangle", "eda", "stats"} or n in {4, 5, 7, 9, 10, 11, 12, 14, 15, 18, 20, 21, 22, 25, 26, 27, 30, 34, 35, 37, 41, 42}:
        frame = vendas()
        if n == 37:
            frame["canal"] = rng.choice(["pago", "organico"], len(frame))
            frame.loc[frame["canal"].eq("pago"), "ticket"] *= 1.15
        if n == 8:
            return {"entrada.json": None}
        return {"entrada.csv": frame}
    return {"entrada.csv": vendas()}


def write_data(spec: dict, folder: Path) -> None:
    rng = np.random.default_rng(spec["numero"] + 17)
    n = spec["numero"]
    data_dir = folder / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    if n == 8:
        (data_dir / "entrada.csv").write_text('n,seed,nulos\n400,8,0.05\n', encoding="utf-8")
        # engine of 8 expects json if suffix json; we keep csv and handle in engine via json fallback... 
        # engine reads json only if suffix json. Patch: write json as entrada.csv? Better write both and point main to json.
        (data_dir / "entrada.csv").write_text("n,seed,nulos\n400,8,0.05\n", encoding="utf-8")
        # override engine for n=8 to read csv
        return
    tables = make_dataframe(spec, rng)
    for name, frame in tables.items():
        if frame is None:
            continue
        if "data" in frame.columns:
            frame = frame.copy()
            frame["data"] = frame["data"].astype(str)
        frame.to_csv(data_dir / name, index=False)


def patch_engine_for_synthetic() -> None:
    ENGINE_WRANGLE["synthetic"] = dump_json_fn() + '''
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
'''


def build_project(spec: dict) -> None:
    folder = ROOT / spec["caminho"]
    folder.mkdir(parents=True, exist_ok=True)
    write(folder / "src" / "main.py", MAIN_TEMPLATE.format(numero=spec["numero"], titulo=spec["titulo"], objetivo=spec["objetivo_aprendizagem"]))
    write(folder / "src" / "engine.py", engine_source(spec))
    write(folder / "src" / "__init__.py", "")
    keys = FAMILY_KEYS[spec["numero"]]
    tests = TEST_TEMPLATE.format(keys=keys, extra=extra_assert(spec))
    write(folder / "tests" / "test_engine.py", tests)
    write(folder / "tests" / "__init__.py", "")
    write(folder / "requirements.txt", requirements_for(spec))
    write(folder / ".env.example", "INPUT_PATH=data/entrada.csv\nOUTPUT_PATH=out/resultado.json\nLOG_LEVEL=INFO\n")
    write(folder / "pytest.ini", "[pytest]\npythonpath = src\n")
    write(folder / "README.md", render_readme(spec))
    write_data(spec, folder)
    save_architecture(folder / "assets" / "architecture.png", spec)


def build_foundation() -> None:
    catalog = public_catalog()
    write(ROOT / "catalog" / "projects.json", json.dumps(catalog, ensure_ascii=False, indent=2))
    (ROOT / "scripts" / "validate_projects.py").write_text(
        (Path(__file__).with_name("validate_projects.py")).read_text(encoding="utf-8") if Path(__file__).with_name("validate_projects.py").exists() else VALIDATE_FALLBACK,
        encoding="utf-8",
    )


VALIDATE_FALLBACK = ""  # filled after copying


def main() -> int:
    configure_stdio()
    patch_engine_for_synthetic()
    save_cover(ROOT / "assets" / "cover.png")
    save_roadmap(ROOT / "assets" / "roadmap.png")
    for spec in SPECS:
        build_project(spec)
        print(f"ok {spec['numero']:03d} {spec['slug']}", flush=True)
    write(ROOT / "catalog" / "projects.json", json.dumps(public_catalog(), ensure_ascii=False, indent=2) + "\n")
    print(f"gerados {len(SPECS)} projetos em {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
