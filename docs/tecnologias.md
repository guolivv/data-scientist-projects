# Tecnologias

A ferramenta entra quando o problema pede. A coluna prática deste repositório é sempre uma opção local ou gratuita. Nenhuma trilha exige conta paga.

| Ferramenta | Quando faz sentido | Alternativa local ou gratuita |
|------------|--------------------|-------------------------------|
| Python 3.11+ | Quase todo projeto: ler arquivo, transformar, testar e entregar uma CLI. | A própria biblioteca padrão. Sem runtime pago. |
| pandas | Tabela, join, groupby, datas e o dataset de trabalho. | Biblioteca local. |
| numpy | Vetor, seed, simulação e conta estatística. | Biblioteca local. |
| pytest | Provar que a métrica, o split ou o artefato não quebrou. | Roda na máquina, sem serviço externo. |
| matplotlib | Histograma, heatmap, série e figura exportada. | Backend `Agg`, PNG na pasta `out/`. |
| sqlite3 | SQL analítico sem instalar servidor. | Já vem com o Python. |
| scikit-learn | Pipeline, modelo, métrica, clustering, TF-IDF e persistência. | Biblioteca local. Sem cluster e sem GPU. |

## O que fica de fora de propósito

Não há etapa obrigatória em SageMaker, Vertex, Databricks, warehouse pago nem LLM de API. Quando um conceito desses aparece (registro de modelo, drift, card), a pasta mostra o mecanismo com arquivo local e declara a distância até um ambiente de empresa.

Não há TensorFlow, PyTorch nem spaCy obrigatórios. O objetivo é o raciocínio de ciência de dados, não a stack mais pesada.

## Como escolher

- Cabe numa tabela e a pergunta é descritiva: pandas e um JSON de resumo.
- A pergunta é SQL: sqlite3 em memória ou arquivo.
- Há incerteza ou experimento: intervalo, teste e simulação em numpy.
- Há modelo: sklearn com seed, holdout ou K-fold, métrica na unidade do negócio.
- Há texto: TF-IDF local, sem embedding pago.
- Há série: baseline naive antes de qualquer modelo sofisticado.

A lista por projeto está em [../catalog/projects.json](../catalog/projects.json), no campo `tecnologias`.
