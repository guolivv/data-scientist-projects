# Arquitetura

Há duas escalas neste repositório: a pasta de um projeto e a trilha inteira. A trilha não é uma plataforma única. São 100 exercícios que compartilham convenção, catálogo e uma progressão.

## Um projeto

A pasta é autocontida. O número e o slug vêm de [../catalog/projects.json](../catalog/projects.json).

```text
categoria/NNN-slug/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py
│   └── engine.py
├── tests/
├── data/                      # sintético ou fixture
└── assets/
    └── architecture.png
```

`src/main.py` é o ponto de entrada da CLI, em português nas mensagens. O teste padrão continua sendo pytest.

`.env.example` lista variáveis sem valor real. Segredo não entra no código.

`assets/architecture.png` explica aquele projeto: origem, etapas e destino. Não é figura genérica reaproveitada.

O README do projeto tem 17 seções, listadas em [../TASKS.md](../TASKS.md). Entre elas estão decisões, limitações e o que a pessoa pode mostrar no portfólio.

## Como a complexidade cresce

**Básico (001–034).** Pandas, EDA e SQL local. Sem Docker e sem serviço obrigatório. A arquitetura cabe num fluxo curto: ler, descrever, transformar, gravar.

**Intermediário (035–067).** Entram teste de hipótese, A/B, feature engineering e modelos supervisionados com holdout. sklearn roda na máquina. Não há cluster.

**Avançado (068–100).** Clustering, séries, texto, drift, fairness educacional, model card e casos de ponta a ponta. O código continua executável numa máquina só. Conta paga e operação 24 horas não fazem parte do contrato.

A imagem de arquitetura deve acompanhar esse crescimento. No básico, um fluxo linear honesto. No avançado, as fronteiras entre dado, modelo, avaliação e documentação, sem caixa decorativa de ferramenta que o código não usa.

## Demonstração educacional

Os projetos avançados são demonstrações educacionais. Não são produção. Passar em pytest local, em sklearn ou em um model card gerado não substitui monitoramento operado, dado real, governança de modelo nem aprovação jurídica.

Nenhuma pasta deve dizer que está pronta para produção só porque treina um classificador ou calcula um PSI.

Casos em que a honestidade é parte do desenho:

- **039.** Simpson mostra que correlação agregada engana; não é um motor causal.
- **046.** Peeking é uma simulação didática da inflação de falso positivo.
- **088 e 097.** Fairness usa grupo sintético. Não há dado pessoal real.
- **090 e 100.** O model card documenta limite e uso pretendido educacional.
- **076, 082–086, 099.** Texto é fixture em português, não um corpus de clientes.

## O que a fundação não faz

`scripts/validate_projects.py` confere estrutura, imagem, seções do README, catálogo e links do README da raiz. Ele não substitui o pytest de cada projeto e não promove status para `validado`.

`scripts/generate_catalog.py` só imprime as tabelas. O texto do README da raiz continua editorial.
