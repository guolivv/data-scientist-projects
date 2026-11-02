# Roadmap

A trilha tem 100 projetos. Os 34 primeiros são básicos (001–034), os 33 seguintes são intermediários (035–067) e os 33 últimos são avançados (068–100). A figura dessa divisão está em [../assets/roadmap.png](../assets/roadmap.png).

O catálogo em [../catalog/projects.json](../catalog/projects.json) guarda, para cada projeto, o anterior recomendado. Esse anterior é dependência pedagógica, não uma biblioteca que precise estar instalada.

## Como a dificuldade cresce

1. **Fundamentos (001–010).** Ler CSV, tipo, nulo, outlier, data, join, KPI, dado sintético, seed e perfil.
2. **Análise exploratória (011–020).** Distribuição, correlação, bivariada, frequência, Pareto, grupos, missing, relatório, KPI de produto e figuras.
3. **SQL para ciência de dados (021–034).** SQLite, ranking, cohort, funil, RFM, janela, amostra, pivot, as-of join, métrica, feature, qualidade, view e dicionário.
4. **Estatística e experimentos (035–046).** Resumo robusto, IC, t, qui-quadrado, Simpson, A/B, poder, bootstrap, Mann-Whitney, CUPED, FDR e peeking.
5. **Feature engineering (047–056).** Encoding, scaler, binning, calendário, target encoding, pipeline, leakage, seleção, interação e imputação.
6. **Aprendizado supervisionado (057–067).** Linear, métricas, logística, threshold, árvore, floresta, boosting, CV, desbalanceamento, ROC/PR e baseline.
7. **Não supervisionado (068–076).** K-means, elbow, PCA, hierárquico, anomalia, DBSCAN, t-SNE, personas e NMF.
8. **Séries e texto (077–086).** Decomposição, naive, rolling, backtest, quebra, BoW, TF-IDF, classificador, sentimento e busca.
9. **Avaliação, ética e MLOps (087–094).** Drift, fairness educacional, permutação, model card, registro, monitoramento, custo e retreino.
10. **Projetos completos (095–100).** Churn, demanda, crédito, recomendação, tickets e um laboratório local.

Não pule o anterior se o conceito ainda não estiver claro. Pode pular um projeto isolado quando o README dele disser que a dependência é só de leitura.

## Trilhas

### Primeiros passos com pandas

- [001 — Leitura tabular com pandas](../01-fundamentos/001-leitura-tabular/)
- [002 — Tipos e conversão de colunas](../01-fundamentos/002-tipos-e-conversao/)
- [003 — Valores ausentes](../01-fundamentos/003-valores-ausentes/)
- [007 — Agrupamentos e KPIs](../01-fundamentos/007-agrupamentos-e-kpis/)
- [009 — Reprodutibilidade com seed](../01-fundamentos/009-reprodutibilidade-com-seed/)
- [010 — Perfil estatístico de dataset](../01-fundamentos/010-perfil-estatistico/)

### Análise exploratória

- [011 — Distribuições univariadas](../02-analise-exploratoria/011-distribuicoes-univariadas/)
- [012 — Correlação e heatmap](../02-analise-exploratoria/012-correlacao-e-heatmap/)
- [015 — Pareto e concentração](../02-analise-exploratoria/015-pareto-e-concentracao/)
- [018 — Relatório de EDA em Markdown](../02-analise-exploratoria/018-relatorio-eda-markdown/)
- [019 — KPIs de produto](../02-analise-exploratoria/019-kpis-de-produto/)

### SQL para ciência de dados

- [021 — Carga de CSV no SQLite](../03-sql-para-ciencia-de-dados/021-carga-csv-sqlite/)
- [023 — Cohort de retenção](../03-sql-para-ciencia-de-dados/023-cohort-de-retencao/)
- [024 — Funil de conversão](../03-sql-para-ciencia-de-dados/024-funil-de-conversao/)
- [025 — RFM em SQL](../03-sql-para-ciencia-de-dados/025-rfm-em-sql/)
- [029 — Join e vazamento temporal](../03-sql-para-ciencia-de-dados/029-join-e-vazamento-temporal/)

### Experimentos e estatística

- [036 — Intervalo de confiança](../04-estatistica-e-experimentos/036-intervalo-de-confianca/)
- [040 — Teste A/B clássico](../04-estatistica-e-experimentos/040-teste-ab/)
- [041 — Poder e tamanho amostral](../04-estatistica-e-experimentos/041-poder-e-tamanho-amostral/)
- [044 — CUPED e covariáveis](../04-estatistica-e-experimentos/044-cuped/)
- [046 — Peeking e tamanho fixo](../04-estatistica-e-experimentos/046-peeking/)

### Modelagem supervisionada

- [052 — Pipeline sklearn](../05-feature-engineering/052-pipeline-sklearn/)
- [057 — Regressão linear](../06-aprendizado-supervisionado/057-regressao-linear/)
- [059 — Regressão logística](../06-aprendizado-supervisionado/059-regressao-logistica/)
- [064 — Validação cruzada](../06-aprendizado-supervisionado/064-validacao-cruzada/)
- [067 — Baseline versus modelo](../06-aprendizado-supervisionado/067-baseline-vs-modelo/)

### Texto, série e laboratório

- [078 — Baseline naive e sazonal](../08-series-temporais-e-texto/078-baseline-naive/)
- [084 — Classificação de texto](../08-series-temporais-e-texto/084-classificacao-de-texto/)
- [087 — Data drift](../09-avaliacao-etica-e-mlops/087-data-drift/)
- [090 — Model card](../09-avaliacao-etica-e-mlops/090-model-card/)
- [095 — Churn de ponta a ponta](../10-projetos-end-to-end/095-e2e-churn/)
- [100 — Laboratório local de ciência de dados](../10-projetos-end-to-end/100-e2e-laboratorio/)
