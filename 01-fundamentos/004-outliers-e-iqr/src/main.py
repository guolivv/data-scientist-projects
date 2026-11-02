"""CLI do projeto 004 — Outliers e IQR."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from engine import run

logger = logging.getLogger("projeto_004")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detectar outliers pelo IQR, winsorizar e comparar médias antes e depois.")
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
            raise FileNotFoundError(f"Arquivo de entrada não encontrado: {source}")
        result = run(source, destination)
    except (OSError, ValueError, KeyError) as exc:
        logger.error("Falha: %s", exc)
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
