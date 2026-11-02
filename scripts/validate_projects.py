#!/usr/bin/env python3
"""Valida a estrutura dos 100 projetos educacionais.

Execute a partir de qualquer diretório:

    python scripts/validate_projects.py

A raiz considerada é a pasta que contém este script (o repositório
100-projetos-ciencia-de-dados). O código de saída é 0 somente se
todas as verificações passarem. Caso contrário, as falhas são listadas
e o processo termina com código 1.

Enquanto outros lotes ainda criam os diretórios dos projetos, é
esperado que este script falhe. Ele deve terminar com uma lista clara,
sem traceback, mesmo quando nenhum projeto existe.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = (
    "README.md",
    "requirements.txt",
    ".env.example",
    "src/main.py",
)

README_SECTIONS = (
    "Descrição",
    "Problema",
    "Objetivos de aprendizagem",
    "Conceitos de Ciência de Dados",
    "Tecnologias",
    "Arquitetura",
    "Estrutura de diretórios",
    "Pré-requisitos",
    "Instalação e configuração",
    "Como executar",
    "Como validar",
    "Exemplos de entrada e saída",
    "Decisões técnicas",
    "Limitações",
    "Melhorias sugeridas",
    "Aplicação empresarial",
    "Competências para o portfólio",
)

CATALOG_KEYS = (
    "numero",
    "slug",
    "titulo",
    "nivel",
    "categoria",
    "caminho",
    "problema",
    "objetivo_aprendizagem",
    "tecnologias",
    "conceitos",
    "tipo_entrega",
    "aplicacao_empresarial",
    "dependencias_externas",
    "projeto_anterior",
    "status",
)

NIVEIS = {"basico", "intermediario", "avancado"}
STATUS = {"planejado", "em desenvolvimento", "implementado", "validado", "bloqueado"}
SKIP_DIRS = {
    ".git",
    ".venv",
    ".venvs",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "spark-warehouse",
    "metastore_db",
    ".minio",
}
PROJECT_DIR_RE = re.compile(r"^(\d{3})-")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def find_project_dirs() -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, _filenames in os_walk_pruned(ROOT):
        for name in dirnames:
            if PROJECT_DIR_RE.match(name):
                found.append(dirpath / name)
    return found


def os_walk_pruned(root: Path):
    import os

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS and not name.startswith(".")]
        yield Path(dirpath), dirnames, filenames


def load_catalog(failures: list[str]) -> list[dict]:
    catalog_path = ROOT / "catalog" / "projects.json"
    if not catalog_path.is_file():
        failures.append("arquivo ausente: catalog/projects.json")
        return []
    try:
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"catalog/projects.json não é JSON válido: {exc}")
        return []
    if not isinstance(data, list):
        failures.append("catalog/projects.json deve ser uma lista de projetos")
        return []
    return data


def check_catalog_schema(projects: list[dict], failures: list[str]) -> None:
    if len(projects) != 100:
        failures.append(f"catálogo: esperados 100 itens, encontrados {len(projects)}")
    numeros: dict[int, int] = {}
    slugs: dict[str, int] = {}
    caminhos: dict[str, int] = {}
    for index, item in enumerate(projects, start=1):
        if not isinstance(item, dict):
            failures.append(f"catálogo: item {index} não é um objeto")
            continue
        missing = [key for key in CATALOG_KEYS if key not in item]
        if missing:
            failures.append(f"catálogo: item {index} sem campos: {', '.join(missing)}")
            continue
        numero = item["numero"]
        if not isinstance(numero, int):
            failures.append(f"catálogo: numero do item {index} não é inteiro")
            continue
        numeros[numero] = numeros.get(numero, 0) + 1
        slug = item["slug"]
        if not isinstance(slug, str) or not slug:
            failures.append(f"catálogo: slug inválido no projeto {numero}")
        else:
            slugs[slug] = slugs.get(slug, 0) + 1
        caminho = item["caminho"]
        if not isinstance(caminho, str) or "\\" in caminho:
            failures.append(f"catálogo: caminho inválido no projeto {numero}")
        else:
            caminhos[caminho] = caminhos.get(caminho, 0) + 1
            esperado = f"{item['categoria']}/{numero:03d}-{slug}"
            if caminho != esperado:
                failures.append(
                    f"catálogo: caminho do projeto {numero:03d} é '{caminho}', esperado '{esperado}'"
                )
        if item["nivel"] not in NIVEIS:
            failures.append(f"catálogo: nível inválido no projeto {numero}")
        if item["status"] not in STATUS:
            failures.append(f"catálogo: status inválido no projeto {numero}")
        if not isinstance(item["tecnologias"], list) or not item["tecnologias"]:
            failures.append(f"catálogo: tecnologias vazias no projeto {numero}")
        if not isinstance(item["conceitos"], list) or not item["conceitos"]:
            failures.append(f"catálogo: conceitos vazios no projeto {numero}")
        anterior = item["projeto_anterior"]
        if anterior is not None and (not isinstance(anterior, int) or anterior == numero):
            failures.append(f"catálogo: projeto_anterior inválido no projeto {numero}")
        caminho_dir = ROOT / str(item["caminho"])
        if not caminho_dir.is_dir():
            failures.append(f"catálogo: caminho não é diretório: {item['caminho']}")
    esperados = set(range(1, 101))
    presentes = set(numeros)
    for numero in sorted(esperados - presentes):
        failures.append(f"catálogo: número ausente: {numero:03d}")
    for numero in sorted(presentes - esperados):
        failures.append(f"catálogo: número fora de 001-100: {numero}")
    for numero, count in sorted(numeros.items()):
        if count > 1:
            failures.append(f"catálogo: número duplicado: {numero:03d} ({count})")
    for slug, count in sorted(slugs.items()):
        if count > 1:
            failures.append(f"catálogo: slug duplicado: {slug}")
    for caminho, count in sorted(caminhos.items()):
        if count > 1:
            failures.append(f"catálogo: caminho duplicado: {caminho}")
    conhecidos = {item.get("numero") for item in projects if isinstance(item, dict)}
    for item in projects:
        if not isinstance(item, dict):
            continue
        anterior = item.get("projeto_anterior")
        if isinstance(anterior, int) and anterior not in conhecidos:
            failures.append(
                f"catálogo: projeto {item.get('numero')} aponta para anterior inexistente {anterior}"
            )


def check_project_dirs(failures: list[str]) -> None:
    grouped: dict[int, list[Path]] = {}
    estranhos: list[Path] = []
    for path in find_project_dirs():
        match = PROJECT_DIR_RE.match(path.name)
        if match is None:
            continue
        numero = int(match.group(1))
        if not 1 <= numero <= 100:
            estranhos.append(path)
            continue
        grouped.setdefault(numero, []).append(path)
    for path in estranhos:
        failures.append(f"diretório com número fora de 001-100: {rel(path)}")
    if len(grouped) != 100 or any(len(paths) != 1 for paths in grouped.values()):
        failures.append(f"diretórios de projeto: esperados 100 números únicos, encontrados {len(grouped)}")
    for numero in range(1, 101):
        paths = grouped.get(numero, [])
        if not paths:
            failures.append(f"diretório ausente para o número {numero:03d}")
            continue
        if len(paths) > 1:
            lista = ", ".join(rel(path) for path in paths)
            failures.append(f"número {numero:03d} em mais de um diretório: {lista}")
            continue
        check_one_project(paths[0], failures)


def check_one_project(path: Path, failures: list[str]) -> None:
    identificador = rel(path)
    for name in REQUIRED_FILES:
        if not (path / name).is_file():
            failures.append(f"{identificador}: arquivo ausente: {name}")
    tests_dir = path / "tests"
    if not tests_dir.is_dir():
        failures.append(f"{identificador}: diretório ausente: tests/")
    else:
        testes = list(tests_dir.rglob("test_*.py")) + list(tests_dir.rglob("*_test.py"))
        if not testes:
            failures.append(f"{identificador}: tests/ sem arquivo pytest (test_*.py ou *_test.py)")
    image = path / "assets" / "architecture.png"
    if not image.is_file():
        failures.append(f"{identificador}: arquivo ausente: assets/architecture.png")
    else:
        data = image.read_bytes()
        if not data.startswith(b"\x89PNG"):
            failures.append(f"{identificador}: assets/architecture.png sem assinatura PNG")
        if len(data) <= 5000:
            failures.append(
                f"{identificador}: assets/architecture.png tem {len(data)} bytes (mínimo: maior que 5000)"
            )
    readme = path / "README.md"
    if readme.is_file():
        texto = readme.read_text(encoding="utf-8", errors="replace").lower()
        for section in README_SECTIONS:
            if section.lower() not in texto:
                failures.append(f"{identificador}: README sem a seção '{section}'")


def iter_readme_links(markdown: str) -> list[str]:
    links: list[str] = []
    for match in LINK_RE.finditer(markdown):
        raw = match.group(1).strip()
        if raw.startswith("<") and ">" in raw:
            raw = raw[1 : raw.index(">")]
        raw = raw.split()[0] if raw else raw
        links.append(raw)
    return links


def check_root_readme_links(failures: list[str]) -> None:
    readme = ROOT / "README.md"
    if not readme.is_file():
        failures.append("arquivo ausente: README.md")
        return
    texto = readme.read_text(encoding="utf-8", errors="replace")
    for target in iter_readme_links(texto):
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        sem_ancora = target.split("#", 1)[0].split("?", 1)[0]
        if sem_ancora == "":
            continue
        destino = (ROOT / sem_ancora).resolve()
        try:
            destino.relative_to(ROOT)
        except ValueError:
            failures.append(f"README.md: link sai do repositório: {target}")
            continue
        if not destino.exists():
            failures.append(f"README.md: link relativo inexistente: {target}")


def main() -> int:
    configure_stdio()
    failures: list[str] = []
    projects = load_catalog(failures)
    if projects:
        check_catalog_schema(projects, failures)
    check_project_dirs(failures)
    check_root_readme_links(failures)
    if failures:
        print(f"Falhas encontradas: {len(failures)}")
        for item in failures:
            print(f"- {item}")
        return 1
    print("Validação concluída sem falhas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
