# Glossário

Termos usados nesta trilha, no sentido em que os projetos os praticam. A definição é curta de propósito: o detalhe operacional fica no README do projeto citado.

**A/B test.** Comparação de duas variantes com métrica e teste de hipótese. Projeto 040.

**Assimetria.** Medida de cauda de uma distribuição. Entra no perfil (010) e no histograma (011).

**Baseline.** Comparável bobinho: dummy, naive ou regra de negócio, antes de celebrar o modelo. Projetos 067 e 078.

**Bootstrap.** Reamostrar com reposição para obter um intervalo quando a fórmula analítica falta. Projeto 042.

**Churn.** Evento de cancelamento. O 095 fecha um fluxo educacional de churn.

**Cohort.** Grupo que começa no mesmo período, acompanhado no tempo. Projeto 023.

**CUPED.** Ajuste por covariável pré-experimento para reduzir variância. Projeto 044.

**Data drift.** Mudança de distribuição entre treino e atual. Projeto 087 usa PSI em dado sintético.

**Encoding.** Transformar categoria em número: one-hot, ordinal ou target encoding. Projetos 047 e 051.

**Fairness / disparidade.** Comparar taxas entre grupos sintéticos. Projetos 088 e 097. Não há dado pessoal real.

**Feature.** Atributo usado pelo modelo. SQL no 031, sklearn no 047–056.

**Holdout.** Recorte de teste separado do treino. Padrão dos projetos supervisionados.

**IQR.** Amplitude interquartil, usada para outlier no 004 e resumo robusto no 035.

**Leakage.** Usar informação do futuro no treino ou no join. Projetos 029 e 053.

**MDE.** Efeito mínimo detectável no planejamento amostral. Projeto 041.

**Model card.** Documento de uso pretendido, métrica e limite. Projetos 090 e 100.

**Pareto.** Concentração: poucos itens explicam a maior parte da receita. Projeto 015.

**Peeking.** Olhar o p-valor no meio do experimento e parar. Projeto 046 simula o dano.

**Permutation importance.** Queda da métrica ao embaralhar uma coluna no holdout. Projeto 089.

**Pipeline.** Encadear pré-processamento e modelo num objeto só. Projeto 052.

**Precision-Recall.** Curva mais informativa que ROC em classe rara. Projeto 066.

**PSI.** Population Stability Index, usado no drift do 087.

**RFM.** Recência, frequência e valor. Projetos 025 e 075.

**ROC-AUC.** Área sob a curva ROC. Aparece em vários supervisionados e no 095.

**Seed.** Semente de gerador aleatório para repetir o resultado. Projeto 009.

**Silhouette.** Índice de coesão/separação para escolher k. Projeto 069.

**Target encoding.** Média do alvo por categoria, com CV para reduzir vazamento. Projeto 051.

**TF-IDF.** Peso de termo por documento e pelo corpus. Projetos 083 e 084.

**Threshold.** Corte da probabilidade. Projetos 060 e 093 alinham o corte a um custo.

**Walk-forward / rolling origin.** Validação temporal que avança o corte. Projetos 079 e 080.

**Winsorização.** Cortar caudas no limite do IQR em vez de dropar. Projeto 004.
