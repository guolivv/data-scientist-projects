#!/usr/bin/env python3
"""Gera o Markdown das tabelas do catálogo a partir de catalog/projects.json.

Uso, na raiz deste repositório ou a partir de qualquer diretório:

    python scripts/generate_catalog.py

A saída vai para stdout. Cole as tabelas na seção de catálogo do
README.md quando quiser republicar a lista. Este script não reescreve
o README: o texto editorial em volta das tabelas torna a substituição
automática frágil.

O arquivo catalog/projects.json é uma lista e permanece a fonte da
verdade. O Markdown gerado é só uma visão.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog" / "projects.json"

CATEGORY_TITLES = {
    "01-fundamentos": "Fundamentos",
    "02-analise-exploratoria": "Análise exploratória",
    "03-sql-para-ciencia-de-dados": "SQL para ciência de dados",
    "04-estatistica-e-experimentos": "Estatística e experimentos",
    "05-feature-engineering": "Feature engineering",
    "06-aprendizado-supervisionado": "Aprendizado supervisionado",
    "07-nao-supervisionado": "Não supervisionado",
    "08-series-temporais-e-texto": "Séries temporais e texto",
    "09-avaliacao-etica-e-mlops": "Avaliação, ética e MLOps",
    "10-projetos-end-to-end": "Projetos end-to-end",
}

NIVEL_LABEL = {
    "basico": "Básico",
    "intermediario": "Intermediário",
    "avancado": "Avançado",
}


def configure_stdio() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8", errors="replace")


def load_projects() -> list[dict]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("catalog/projects.json deve ser uma lista de projetos")
    return data


def escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def render_catalog(projects: list[dict]) -> str:
    grupos: dict[str, list[dict]] = defaultdict(list)
    for projeto in projects:
        grupos[str(projeto["categoria"])].append(projeto)
    blocos: list[str] = []
    for categoria in sorted(grupos):
        itens = sorted(grupos[categoria], key=lambda item: int(item["numero"]))
        titulo = CATEGORY_TITLES.get(categoria, categoria)
        prefixo = categoria.split("-", 1)[0]
        inicio = int(itens[0]["numero"])
        fim = int(itens[-1]["numero"])
        niveis = {item["nivel"] for item in itens}
        if len(niveis) == 1:
            nivel = NIVEL_LABEL.get(next(iter(niveis)), next(iter(niveis)))
            faixa = f"Projetos {inicio:03d}–{fim:03d} · {nivel}"
        else:
            faixa = f"Projetos {inicio:03d}–{fim:03d}"
        linhas = [
            f"### {prefixo} — {titulo}",
            "",
            faixa,
            "",
            "| Nº | Projeto | Nível | Resumo |",
            "|----|---------|-------|--------|",
        ]
        for item in itens:
            numero = int(item["numero"])
            href = str(item["caminho"]).strip("/") + "/"
            titulo_projeto = escape_cell(item["titulo"])
            nivel = NIVEL_LABEL.get(item["nivel"], str(item["nivel"]))
            resumo = escape_cell(item["problema"])
            linhas.append(
                f"| {numero:03d} | [{titulo_projeto}]({href}) | {nivel} | {resumo} |"
            )
        blocos.append("\n".join(linhas))
    return "\n\n".join(blocos) + "\n"


def main() -> int:
    configure_stdio()
    if not CATALOG_PATH.is_file():
        print(f"Arquivo ausente: {CATALOG_PATH}", file=sys.stderr)
        return 1
    sys.stdout.write(render_catalog(load_projects()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
