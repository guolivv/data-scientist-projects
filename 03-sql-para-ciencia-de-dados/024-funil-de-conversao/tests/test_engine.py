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
    for key in ['funil']:
        assert key in result
        assert key in saved



def test_cli_amostra_versionada(tmp_path: Path) -> None:
    saida = tmp_path / "cli.json"
    code = main(["--entrada", str(SAMPLE), "--saida", str(saida)])
    assert code == 0
    assert saida.is_file()


def test_arquivo_ausente(tmp_path: Path) -> None:
    code = main(["--entrada", str(tmp_path / "nao-existe.csv"), "--saida", str(tmp_path / "x.json")])
    assert code == 1
