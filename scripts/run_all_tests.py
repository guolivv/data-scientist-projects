#!/usr/bin/env python3
"""Roda pytest em cada um dos 100 projetos e grava batches/lote-XX.md."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    catalog = json.loads((ROOT / "catalog" / "projects.json").read_text(encoding="utf-8"))
    python = sys.executable
    results: list[dict] = []
    failed = 0
    for item in catalog:
        folder = ROOT / item["caminho"]
        proc = subprocess.run(
            [python, "-m", "pytest", "-q", "--tb=line"],
            cwd=folder,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        tail = (proc.stdout or "") + (proc.stderr or "")
        summary = tail.strip().splitlines()[-1] if tail.strip() else f"exit {proc.returncode}"
        ok = proc.returncode == 0
        if not ok:
            failed += 1
            print(f"FAIL {item['numero']:03d} {item['slug']}: {summary}", flush=True)
        else:
            print(f"ok   {item['numero']:03d} {item['slug']}: {summary}", flush=True)
        results.append({"numero": item["numero"], "slug": item["slug"], "ok": ok, "summary": summary, "log": tail[-4000:]})

    batches = ROOT / "batches"
    batches.mkdir(exist_ok=True)
    for lote in range(10):
        start = lote * 10 + 1
        end = start + 9
        chunk = [r for r in results if start <= r["numero"] <= end]
        lines = [f"# Lote {lote + 1:02d} — projetos {start:03d}–{end:03d}", ""]
        passed = sum(1 for r in chunk if r["ok"])
        lines.append(f"Pytest: {passed} projetos ok, {len(chunk) - passed} com falha.")
        lines.append("")
        for r in chunk:
            mark = "ok" if r["ok"] else "FAIL"
            lines.append(f"- {r['numero']:03d} {r['slug']}: {mark} — {r['summary']}")
            if not r["ok"]:
                lines.append("```")
                lines.append(r["log"][-1500:])
                lines.append("```")
        (batches / f"lote-{lote + 1:02d}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n{len(results) - failed} ok, {failed} falhas")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
