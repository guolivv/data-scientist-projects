# Como contribuir

Este repositório é material educacional. A contribuição útil é um projeto que roda, explica uma decisão e não finge estar pronto para produção.

O acompanhamento dos lotes está em [TASKS.md](TASKS.md). A fonte da verdade dos 100 projetos é [catalog/projects.json](catalog/projects.json).

## O que pode ser alterado

Cada lote mexe só nos diretórios dos seus projetos. A fundação é dona destes arquivos compartilhados:

- `README.md`, `LICENSE`, `CONTRIBUTING.md`, `TASKS.md`
- `requirements-dev.txt`, `.gitignore`
- `assets/cover.png`, `assets/roadmap.png`
- `docs/`
- `catalog/projects.json`
- `scripts/validate_projects.py`, `scripts/generate_catalog.py`

Não edite, em paralelo, o mesmo arquivo que outro lote está implementando.

## Convenções

- Documentação em português brasileiro.
- Identificadores de código em inglês. Mensagens de CLI em português.
- Sem senha, token ou dado pessoal real. O que parecer segredo fica em `.env`, copiado de `.env.example`, e não entra no Git.
- Dados de exemplo são sintéticos ou fixtures. Se uma API pública for opcional, o projeto funciona sem rede.
- Cada projeto roda sozinho, com o próprio `requirements.txt`.
- Testes com pytest.
- Cada projeto tem a própria `assets/architecture.png`, específica da solução, com assinatura PNG e mais de 5000 bytes.
- Não marque status `validado` sem ter executado o que a afirmação cobre. Se um teste não rodou, registre o motivo.

## Status

Use somente: `planejado`, `em desenvolvimento`, `implementado`, `validado`, `bloqueado`.

`implementado` significa que o código do projeto existe e o autor o executou. `validado` exige a verificação correspondente, não só a presença dos arquivos. `bloqueado` é para impedimento real: documente a falha e não simule a ferramenta.

Ao mudar o status de um projeto, atualize o item em `catalog/projects.json` e a tabela em `TASKS.md`.

## Critério mínimo de um projeto

O `README.md` do projeto contém as 17 seções listadas em `TASKS.md`. Existem `src/main.py`, `tests/` com teste pytest, `requirements.txt`, `.env.example` e `assets/architecture.png`. Não há pasta preenchida só com placeholder, TODO ou código ilustrativo apresentado como pronto.

O comando esperado, salvo quando o próprio README do projeto documentar outro, é:

```bash
python -m venv .venv
pip install -r requirements.txt
python src/main.py
pytest
```

## Antes de enviar

Na raiz desta pasta:

```bash
python -m pip install -r requirements-dev.txt
python -m py_compile scripts/validate_projects.py scripts/generate_catalog.py
python scripts/validate_projects.py
pytest
```

`validate_projects.py` termina com código 0 só quando os 100 projetos passam.

`generate_catalog.py` imprime as tabelas do catálogo na saída padrão e não reescreve o `README.md`.
