# 018 — Relatório de EDA em Markdown

Material educacional de Ciência de Dados. Projeto anterior recomendado: 010. Os clientes, valores e textos deste exercício são fictícios.

## Descrição

Este projeto gerar um relatório Markdown com perfil, riscos e gráficos referenciados. O fluxo local é Dataset → Perfil → Gráficos → Markdown.

## Problema

A exploração fica presa no notebook e ninguém herda o achado.

## Objetivos de aprendizagem

- Praticar relatório, EDA reproduzível, comunicação.
- Entregar um artefato JSON (e arquivos auxiliares quando o problema pede) a partir de um CSV sintético.
- Explicar a decisão técnica e a limitação antes de copiar o desenho para um ambiente real.

## Conceitos de Ciência de Dados

Relatório, eda reproduzível, comunicação. Nível Básico. O código roda offline, com seed quando há aleatoriedade.

## Tecnologias

Python 3.11, pandas, numpy, matplotlib, pytest. Sem conta paga. Docker não é necessário.

## Arquitetura

Dataset → Perfil → Gráficos → Markdown.

![Arquitetura](assets/architecture.png)

## Estrutura de diretórios

```text
018-relatorio-eda-markdown/
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
cd 018-relatorio-eda-markdown
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

Handoff de um dataset novo para o time de modelagem.

## Competências para o portfólio

Mostre o problema, a decisão no código e a limitação. Aponte o teste e a imagem de arquitetura desta pasta.
