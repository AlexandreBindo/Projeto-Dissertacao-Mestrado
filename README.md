# Dissertação Mestrado
# Modelo Evolutivo Multiobjetivo para Otimização de Rotas em Logística Reversa Urbana

**Autor:** Alexandre dos Santos Bindo Cabral  
**Instituição:** Pontifícia Universidade Católica do Paraná (PUCPR)  
**Programa:** Programa de Pós-Graduação em Cidades Inteligentes e Sustentáveis (PPGCIS)  
**Nível:** Mestrado

## 1. Apresentação do Projeto

Este repositório reúne três implementações computacionais desenvolvidas no contexto de uma pesquisa de mestrado voltada à otimização de rotas em operações de logística reversa urbana, utilizando dados geográficos reais e diferentes abordagens algorítmicas.

O projeto busca explorar métodos computacionais que possam contribuir para a eficiência dos deslocamentos urbanos e apoiar a tomada de decisão em aplicações relacionadas às Cidades Inteligentes e Sustentáveis.

O desenvolvimento foi organizado em três etapas: extração de dados geográficos, otimização de rotas por Algoritmo Genético e comparação experimental entre abordagens clássica e quântica.

## 2. Programa 1 — Extração de Dados Geográficos

**Arquivo:** `projtFINAL1.py`  
**Arquivo gerado:** `condor_curitiba.csv`

O primeiro programa realiza a busca automatizada de unidades da rede de supermercados Condor localizadas em Curitiba, Paraná, utilizando dados públicos disponibilizados pelo OpenStreetMap (OSM), por meio da biblioteca Python OSMnx.

As informações obtidas incluem:

- Nome das unidades;
- Endereço;
- Latitude;
- Longitude.

Os dados coletados são organizados e exportados para o arquivo `condor_curitiba.csv`, constituindo a base geográfica utilizada na etapa seguinte do projeto.

Essa implementação permite trabalhar com coordenadas geográficas reais, aproximando os experimentos computacionais de um contexto urbano concreto.

## 3. Programa 2 — Otimização Interativa de Rotas com Algoritmo Genético

**Arquivo:** `projtFINAL2.py`  
**Arquivo de entrada:** `condor_curitiba.csv`

O segundo programa utiliza as coordenadas geográficas obtidas na etapa anterior para realizar a otimização de rotas entre as unidades da rede Condor em Curitiba.

O problema é modelado a partir do Problema do Caixeiro Viajante (Traveling Salesman Problem — TSP), utilizando um Algoritmo Genético como método de busca e otimização.

A implementação contempla operadores evolutivos, incluindo seleção, cruzamento ordenado (Ordered Crossover — OX) e mutação.

As distâncias geográficas entre os pontos são calculadas utilizando a fórmula de Haversine, que considera a curvatura terrestre para estimar a distância entre coordenadas de latitude e longitude.

Durante a execução, o programa apresenta uma visualização gráfica e interativa da evolução da melhor rota encontrada ao longo das gerações.

Ao final do processamento, são apresentados:

- A melhor sequência de unidades encontrada;
- A distância total da rota;
- A representação gráfica da solução;
- A evolução da otimização durante as gerações.

Essa etapa permite investigar a aplicação de algoritmos evolutivos na resolução de problemas combinatórios relacionados ao planejamento de rotas urbanas.

## 4. Programa 3 — Comparação entre Abordagens Clássica e Quântica

**Arquivo:** `projtFINAL3.py`  
**Arquivo de entrada:** `condor_curitiba_teste.csv`

O terceiro programa apresenta uma implementação experimental voltada à comparação entre abordagens de computação clássica e quântica aplicadas ao Problema do Caixeiro Viajante (TSP).

Para a formulação quântica, o problema é inicialmente representado por uma matriz QUBO (Quadratic Unconstrained Binary Optimization), posteriormente convertida em um Hamiltoniano de Ising.

Essa representação é utilizada pelo algoritmo QAOA (Quantum Approximate Optimization Algorithm), cujos parâmetros são ajustados por meio do método clássico de otimização COBYLA.

### Delimitação experimental

Diferentemente do Programa 2, esta implementação utiliza o arquivo `condor_curitiba_teste.csv`, contendo apenas quatro unidades da rede Condor.

A redução do número de unidades foi adotada para diminuir a complexidade do problema e o tempo de processamento computacional, viabilizando os experimentos com QAOA.

Essa configuração permite realizar uma comparação exploratória em escala reduzida, considerando:

- A rota encontrada por cada abordagem;
- A distância total percorrida;
- O desempenho computacional;
- As diferenças entre os resultados clássico e quântico.

O objetivo dessa etapa é investigar o comportamento das duas abordagens, identificando possibilidades e limitações da utilização de métodos quânticos em problemas de otimização combinatória.

Os resultados possuem caráter experimental e não pressupõem superioridade da abordagem quântica sobre a clássica.

## 5. Organização dos Arquivos

```text
Projeto-Dissertacao-Mestrado/
│
├── projtFINAL1.py
├── projtFINAL2.py
├── projtFINAL3.py
│
├── condor_curitiba.csv
├── condor_curitiba_teste.csv
│
└── README.md
```

**Descrição dos arquivos:**

| Arquivo | Finalidade |
|---|---|
| `projtFINAL1.py` | Extração de dados geográficos do OpenStreetMap |
| `projtFINAL2.py` | Otimização de rotas utilizando Algoritmo Genético |
| `projtFINAL3.py` | Comparação experimental entre métodos clássico e quântico |
| `condor_curitiba.csv` | Base geográfica utilizada pelo Programa 2 |
| `condor_curitiba_teste.csv` | Base reduzida com quatro unidades utilizada pelo Programa 3 |
| `README.md` | Documentação geral do projeto |

## 6. Fluxo Metodológico

O desenvolvimento computacional está organizado em três etapas complementares:

**Etapa 1 — Aquisição de dados**

OpenStreetMap → OSMnx → Extração de coordenadas → Arquivo CSV.

**Etapa 2 — Otimização evolutiva**

Dados geográficos → Modelagem TSP → Algoritmo Genético → Visualização e análise da rota.

**Etapa 3 — Comparação clássica e quântica**

Base experimental reduzida → Formulação QUBO → Hamiltoniano de Ising → QAOA com COBYLA → Comparação dos resultados.

As três implementações representam uma sequência de desenvolvimento metodológico, desde a obtenção de dados reais até a investigação experimental de diferentes técnicas computacionais de otimização.

## 7. Considerações Finais

Os programas apresentados constituem implementações desenvolvidas durante a evolução de uma pesquisa de mestrado sobre otimização de rotas em logística reversa urbana.

A integração entre dados geográficos reais, algoritmos evolutivos e métodos de computação quântica permite explorar diferentes possibilidades de solução para problemas de otimização combinatória.

As implementações atuais representam etapas experimentais da pesquisa e fornecem uma base para estudos posteriores envolvendo critérios adicionais de otimização, avaliação de desempenho e aplicações em cenários urbanos de logística reversa.

---

**Projeto acadêmico em desenvolvimento — Mestrado em Cidades Inteligentes e Sustentáveis — PUCPR.**