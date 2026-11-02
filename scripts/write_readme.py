#!/usr/bin/env python3
"""Escreve README.md, TASKS.md e RELATORIO-FINAL.md a partir do catálogo."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_catalog import render_catalog  # noqa: E402

NIVEL_LABEL = {"basico": "Básico", "intermediario": "Intermediário", "avancado": "Avançado"}


def main() -> int:
    catalog = json.loads((ROOT / "catalog" / "projects.json").read_text(encoding="utf-8"))
    tables = render_catalog(catalog)
    tracks = {
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
    faixas = []
    for cat, titulo in tracks.items():
        itens = [p for p in catalog if p["categoria"] == cat]
        faixas.append(f"| `{cat}` | {titulo} | {itens[0]['numero']:03d}–{itens[-1]['numero']:03d} |")
    readme = f'''# 100 Projetos de Ciência de Dados

![Capa: trilha do básico ao avançado](assets/cover.png)

Cem projetos práticos para aprender ciência de dados fazendo: pandas, EDA, SQL, experimento, feature, modelo, cluster, série, texto e um caso de ponta a ponta. Cada pasta é um problema com começo, meio e comando de execução.

Os 100 projetos estão implementados. A suíte local (pytest) e o resultado dos lotes ficam em `batches/`. O quadro de status está em [TASKS.md](TASKS.md) e o fechamento em [RELATORIO-FINAL.md](RELATORIO-FINAL.md). Cada projeto marcado `validado` passou nessa suíte local. Isso não torna o material production-ready.

## Proposta

O material serve para quem quer praticar ciência de dados, montar portfólio e ver como um problema de negócio vira análise, modelo e checagem. Não é uma lista de ideias. Cada número de 001 a 100 tem pasta, enunciado, tecnologias e um anterior recomendado.

A fonte da verdade é [catalog/projects.json](catalog/projects.json). As tabelas abaixo são a visão desse arquivo. Para gerá-las de novo:

```bash
python scripts/generate_catalog.py
```

O script imprime Markdown na saída padrão e não reescreve este README.

## O que você encontra

- 100 projetos numerados, em 10 categorias, do básico ao avançado.
- Um problema curto, um objetivo de aprendizagem e o projeto anterior, quando existe.
- Convenção única de pasta: `README.md`, `src/main.py`, `src/engine.py`, `tests/`, `requirements.txt`, `.env.example` e `assets/architecture.png`.
- Dados sintéticos. Nenhuma API paga.
- Documentação em português e um glossário dos termos usados na trilha.
- Scripts para validar a estrutura e regenerar as tabelas do catálogo.

Os diretórios 001 a 100 estão no disco, um de cada, nos caminhos de [catalog/projects.json](catalog/projects.json).

## Para quem é

- Quem está começando e quer uma ordem, em vez de um tutorial solto.
- Quem já programa e precisa praticar pandas, SQL analítico, experimento e sklearn.
- Quem vai a uma entrevista e quer explicar uma decisão com código que roda.
- Quem adapta um exercício para um protótipo interno, sabendo a distância até produção.

Não é um curso com certificado, nem um atalho para cargo. Também não substitui o critério de um ambiente real: os projetos avançados são demonstrações educacionais, como explica [docs/arquitetura.md](docs/arquitetura.md).

## Como usar

1. Escolha uma trilha em [docs/roadmap.md](docs/roadmap.md) ou um número na tabela abaixo.
2. Leia o projeto anterior indicado no catálogo, se o conceito for novo.
3. Entre na pasta do projeto e siga o README dele. A seção abaixo é o caminho padrão.
4. Ao terminar, olhe limitações e melhorias sugeridas antes de copiar o desenho para outro contexto.

Não é obrigatório fazer os 100 em sequência. É obrigatório respeitar o pré-requisito quando você ainda não viu o conceito.

## Como executar um projeto individual

Na pasta do projeto, o caminho padrão é:

```bash
python -m venv .venv
```

No Windows, PowerShell:

```powershell
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python src/main.py
pytest
```

No Linux ou macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python src/main.py
pytest
```

O ponto de entrada Python continua sendo `python src/main.py`, e o teste continua sendo pytest. Não há conta paga obrigatória.

Para trabalhar nos scripts desta raiz:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_projects.py
```

O validador sai com código 0 só quando os 100 projetos passam.

## Pré-requisitos gerais

- Python 3.11 ou superior
- Git
- pandas, numpy, scikit-learn e matplotlib nos projetos que os listam
- Nenhuma conta paga obrigatória

Detalhe em [docs/tecnologias.md](docs/tecnologias.md).

## Roadmap e organização

![Roadmap das dez categorias e dos três níveis](assets/roadmap.png)

A progressão pedagógica e as trilhas com links estão em [docs/roadmap.md](docs/roadmap.md).

| Nível | Projetos | Quantidade | Foco |
|-------|----------|------------|------|
| Básico | 001–034 | 34 | Pandas, EDA e SQL local |
| Intermediário | 035–067 | 33 | Estatística, features e modelos supervisionados |
| Avançado | 068–100 | 33 | Cluster, série, texto, MLOps local e casos completos |

| Pasta | Categoria | Projetos |
|-------|-----------|----------|
{chr(10).join(faixas)}

## Catálogo

Resumo de uma linha. O objetivo, as tecnologias, os conceitos e o projeto anterior estão em [catalog/projects.json](catalog/projects.json).

{tables}

## Tecnologias e conceitos

Python, pandas, numpy, pytest, SQLite, matplotlib e scikit-learn aparecem quando o problema pede. O guia de quando usar cada uma está em [docs/tecnologias.md](docs/tecnologias.md).

Os termos da trilha (leakage, RFM, CUPED, PSI, model card e outros) estão em [docs/glossario.md](docs/glossario.md). A organização de uma pasta e o crescimento por nível estão em [docs/arquitetura.md](docs/arquitetura.md).

## Trilhas de estudo

Cada item aponta para projetos reais do catálogo. A lista comentada está em [docs/roadmap.md](docs/roadmap.md).

- **Primeiros passos com pandas:** [001](01-fundamentos/001-leitura-tabular/), [003](01-fundamentos/003-valores-ausentes/), [007](01-fundamentos/007-agrupamentos-e-kpis/), [009](01-fundamentos/009-reprodutibilidade-com-seed/), [010](01-fundamentos/010-perfil-estatistico/).
- **EDA:** [011](02-analise-exploratoria/011-distribuicoes-univariadas/), [012](02-analise-exploratoria/012-correlacao-e-heatmap/), [015](02-analise-exploratoria/015-pareto-e-concentracao/), [018](02-analise-exploratoria/018-relatorio-eda-markdown/).
- **SQL analítico:** [021](03-sql-para-ciencia-de-dados/021-carga-csv-sqlite/), [023](03-sql-para-ciencia-de-dados/023-cohort-de-retencao/), [025](03-sql-para-ciencia-de-dados/025-rfm-em-sql/), [029](03-sql-para-ciencia-de-dados/029-join-e-vazamento-temporal/).
- **Experimentos:** [036](04-estatistica-e-experimentos/036-intervalo-de-confianca/), [040](04-estatistica-e-experimentos/040-teste-ab/), [041](04-estatistica-e-experimentos/041-poder-e-tamanho-amostral/), [046](04-estatistica-e-experimentos/046-peeking/).
- **Modelagem:** [052](05-feature-engineering/052-pipeline-sklearn/), [057](06-aprendizado-supervisionado/057-regressao-linear/), [059](06-aprendizado-supervisionado/059-regressao-logistica/), [067](06-aprendizado-supervisionado/067-baseline-vs-modelo/).
- **Projeto completo de portfólio:** [095](10-projetos-end-to-end/095-e2e-churn/), [096](10-projetos-end-to-end/096-e2e-demanda/), [097](10-projetos-end-to-end/097-e2e-credito/), [098](10-projetos-end-to-end/098-e2e-recomendacao/), [099](10-projetos-end-to-end/099-e2e-tickets/), [100](10-projetos-end-to-end/100-e2e-laboratorio/).

## Como usar em portfólio

Escolha uma trilha e dois ou três projetos em que você consiga explicar o problema, a decisão e a limitação sem ler o README na hora. Os casos 095 a 100 são os mais próximos de uma entrega completa, desde que os anteriores que eles citam tenham sido estudados.

No repositório ou no README pessoal, aponte a pasta, a imagem de arquitetura e o teste. Diga o que o projeto demonstra e o que ele não cobre.

## Como contribuir

O combinado de pastas, idioma, status e o que não marcar como validado está em [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença e aviso sobre dados

Código e documentação sob a licença MIT, em [LICENSE](LICENSE). Copyright 2026, Awesome Data Engineering BR contributors.

Os exemplos usam dados sintéticos ou fixtures. Não há dado pessoal real. Chaves de exemplo em `.env.example` são fictícias.

## Status real

Cem projetos implementados. Testes locais executados pelos lotes, com o resultado em `batches/lote-01.md` a `batches/lote-10.md`. O catálogo marca cada um como `validado` por essa suíte. A fundação permanece `implementado`.

O material é educacional.
'''
    (ROOT / "README.md").write_text(readme, encoding="utf-8")

    linhas = [
        "# Acompanhamento",
        "",
        "## Objetivo",
        "",
        "Entregar, na pasta `100-projetos-ciencia-de-dados`, um repositório educacional com 100 projetos práticos de ciência de dados, do básico ao avançado. Cada projeto precisa de código executável, documentação, dados de exemplo, instrução de execução e imagem própria.",
        "",
        "## Critérios por projeto",
        "",
        "Cada número só sai de `em desenvolvimento` quando a pasta tiver as 17 seções do README, `src/main.py`, testes pytest, dados sintéticos, `assets/architecture.png`, `requirements.txt` e `.env.example`.",
        "",
        "## Tabela dos projetos",
        "",
        "| Nº | Título | Nível | Lote | Status |",
        "|----|--------|-------|------|--------|",
    ]
    for p in catalog:
        lote = f"lote {(p['numero'] - 1) // 10 + 1:02d}"
        linhas.append(f"| {p['numero']:03d} | {p['titulo']} | {p['nivel']} | {lote} | {p['status']} |")
    linhas += [
        "",
        "## Status permitidos",
        "",
        "`planejado`, `em desenvolvimento`, `implementado`, `validado`, `bloqueado`.",
        "",
    ]
    (ROOT / "TASKS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("README.md e TASKS.md escritos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
