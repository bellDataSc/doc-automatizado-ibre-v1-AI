# Relatório DNIT II.01.1 — Tomo 1 Materiais SICRO (2º RR nº 15-08/2026, Ref. Jul/2026)

Documentação estrutural do **relatório-produto** — o documento que a aplicação
deve automatizar. Gerada por extração e leitura integral do PDF
(`pypdf`, 165 páginas, 5.278 linhas de texto).

- **Arquivo:** `DNIT_II.01.1_2ºRR_15-08.2026_Tomo-1_Materiais-SICRO-compactado.pdf`
- **Tamanho:** ~6,87 MB · **165 páginas no PDF** (a ficha catalográfica declara `162 p.`)
- **Entradas que o alimentam:** `DNIT_II.08.0_…Resultado-Final…xlsx` (preços) e
  `DNIT_II.09.0_…Origem-Precos…xlsx` (origem metodológica). Ver docs próprias.

---

## 1. Identificação

| Campo | Valor literal |
|---|---|
| Órgão | `DEPARTAMENTO NACIONAL DE INFRAESTRUTURA DE TRANSPORTES – DNIT` |
| Documento | `2º RELATÓRIO DE RESULTADOS Nº 15-08/2026` |
| Tomo | `TOMO 1 – MATERIAIS SICRO` |
| Referência | `REFERÊNCIA JULHO/2026` |
| Objetivo | `OBJETIVO II – PESQUISA NACIONAL DE PREÇOS DE INSUMOS` |
| Contrato | `Contrato nº 647/2024` (SEI nº 19092578, celebrado em 30/09/2024) |
| Protocolo FGV | `FGV IBRE VDRI/821/2026` |
| Data | `Setembro de 2026` · local `São Paulo` |
| Executor | Fundação Getulio Vargas – FGV / Instituto Brasileiro de Economia – IBRE |

**Resumo (p. 4, verbatim):** "2º Relatório de Resultados referente à Pesquisa de
Preços, Referência Julho de 2026, Objetivo II – Pesquisa Nacional de Preços de
Insumos: Tomo 1 – Materiais SICRO, pertencente ao contrato n° 647/2024 (SEI n°
19092578), celebrado em 30 de setembro de 2024, entre a Fundação Getulio Vargas
– FGV, por intermédio do seu Instituto Brasileiro de Economia – IBRE, e o
Departamento Nacional de Infraestrutura de Transportes – DNIT."

**Escopo:** o Tomo 1 trata **apenas dos insumos de prefixo `M` (materiais)** —
1.704 itens no arquivo de preços. Equipamentos (`A`/`E`) e Mão de Obra (`P`) são
objeto de outros tomos. Isso confirma a separação em três frentes da aplicação.

---

## 2. Anatomia do documento

### 2.1 Blocos fixos (front matter)

| Páginas PDF | Conteúdo |
|---|---|
| 1 | Capa |
| 2 | Folha de rosto |
| 3 | Ficha catalográfica (`162 p.` · palavras-chave: Contrato FGV/DNIT nº 647/2024, Desenvolvimento do Programa DNIT, Metodologias, Pesquisa de preço, SICRO) |
| 4 | `RESUMO` |
| 5–7 | `LISTA DE GRÁFICOS` (63 entradas) |
| 8–9 | `LISTA DE TABELAS` (36 entradas) |
| 10–11 | `SUMÁRIO` |
| 12 → 163 | Corpo (seções 1 a 7) |
| 164 | `APÊNDICE A` |
| 165 | Página final sem texto |

### 2.2 Cabeçalho repetido em todas as páginas do corpo

Quatro linhas fixas — descartar no parsing:

```
Programa DNIT – Objetivo II
2º Relatório de Resultados – Pesquisa Nacional de Preços de Insumos
Tomo 1 – Materiais SICRO
Nº 15-08/2026 FGV IBRE VDRI/821/2026
```

Variam entre entregas apenas `Nº 15-08/2026` e `VDRI/821/2026`.

### 2.3 Convenções de layout observadas

| Convenção | Detalhe |
|---|---|
| **Numeração** | página impressa = página PDF − 2 (offset constante) |
| **Posição do número** | normalmente após o cabeçalho; **antes** dele nas páginas em paisagem com tabelas de 27 UFs (ex. PDF 89, 108, 115) |
| **Gráficos por página** | `nº de gráficos = imagens − 2` (2 imagens fixas de marca). `imagens=2` → só texto/tabela; `=3` → 1 gráfico; `=4` → 2 gráficos |
| **Bloco de gráfico** | `Gráfico {N} - {Título}` → imagem → `Fonte: FGV IBRE` → parágrafo de análise (frequentemente na página seguinte) |
| **Tabela contínua** | título repetido com sufixo `(2/6)`, `(3/6)`… A **primeira parte nunca traz `(1/N)`** |
| **`Fonte: FGV IBRE`** | uma vez, na **última** parte da tabela. Exceções: nas tabelas largas em paisagem (T15, T24) a extração o coloca **antes** do cabeçalho |
| **Separadores** | hífen `-` e travessão `–` usados de forma inconsistente em títulos e códigos (`Tabela 24 -` vs `Tabela 25 –`) |

### 2.4 Estrutura de seções (sumário)

```
1. INTRODUÇÃO ......................................................... 10
   1.1. Aprimoramentos metodológicos da referência
2. MATERIAIS DE AMPLA COMERCIALIZAÇÃO (PARTE 1) ...................... 10
   2.1. Diagnósticos de dados pesquisados
        2.1.1. Materiais com preços zerados
        2.1.2. Materiais precificados por metodologia de agregados
               2.1.2.1. Comparação das distâncias médias de transporte dos agregados
        2.1.3. Materiais precificados por metodologia do cimento
        2.1.4. Materiais precificados por metodologia da cal hidratada
   2.2. Variações de preços de materiais de ampla comercialização
        2.2.1. Materiais relevantes em obras de infraestrutura
               2.2.1.1. Distribuição das variações
               2.2.1.2. Variação de preços dos materiais relevantes em orçamentos
               2.2.1.3. Evolução de preços dos materiais representativos
        2.2.2. Materiais relacionados como líderes e liderados
               2.2.2.1. Distribuição de variações de materiais líderes
               2.2.2.2. Distribuição de variações de materiais liderados
        2.2.3. Materiais de ampla comercialização relevantes em CCUs acima de |5%|
        2.2.4. Ocorrências de variação acima de |20%|
   2.3. Amplitudes de preços de materiais de ampla comercialização
        2.3.1. Distribuição de amplitudes de materiais
        2.3.2. Análises de amplitudes acima de 100%
   2.4. Ordenamento de preços de materiais de ampla comercialização
        2.4.1. Ordenamento de materiais relevantes em obras de infraestrutura
3. MATERIAIS DE COMERCIALIZAÇÃO RESTRITA (PARTE 2) .................. 102
   3.1. Diagnósticos de dados pesquisados
        3.1.1. Itens com preço pesquisado com tratamento e aplicação do frete metodológico
        3.1.2. Itens com preço pesquisado e atualizado por índice
        3.1.3. Itens com preço extrapolado ou interpolado
        3.1.4. Itens com preço estimado
        3.1.5. Itens com preço pesquisado e imputado nas demais UFs
   3.2. Variações de preços de Materiais de comercialização restrita
        3.2.1. Materiais de comercialização restrita relevantes em orçamentos
               3.2.1.1. Evolução de preços dos materiais representativos
        3.2.2. Relevantes em composições valoradas acima de |5%|
        3.2.3. Ocorrências de variação acima de |20%|
   3.3. Amplitudes de preços de materiais de comercialização restrita
        3.3.1. Análises de amplitudes acima de 100%
   3.4. Ordenamento de preços de materiais de comercialização restrita
        3.4.1. Principais gráficos de ordenamentos
        3.4.2. Ocorrências em ordenamentos de preços de materiais com DMT
4. PREÇOS COLETADOS NO VAREJO ....................................... 126
   4.1. Cobertura da pesquisa varejo
   4.2. Proposta de substituição de insumos na pesquisa do varejo
5. COTAÇÕES ENCAMINHADAS PELO DNIT .................................. 132
   5.1. Caracterização dos dados recebidos
   5.2. Tratamento dos dados recebidos
   5.3. Balizamento preços cotações x SICRO
        5.3.1. Ocorrências de diferença acima de |25%|
        5.3.2. Desdobramentos das análises
   5.4. Conclusão acerca das análises das cotações
6. ESFORÇO DE PESQUISA .............................................. 159
7. MANIFESTAÇÃO SOBRE PARECERES ANTERIORES ......................... 160
APÊNDICE A – SÍTIO PARA CONSULTA DO PAINEL DE PREÇOS REFERENCIAIS .. 162
```

**Simetria Parte 1 / Parte 2:** as seções 2 e 3 são espelhadas
(diagnósticos → variações → amplitudes → ordenamento). Vários parágrafos são o
mesmo template com 2-3 slots trocados. Vale implementar **uma** função por
bloco, parametrizada por universo (`ampla` | `restrita`).

---

## 3. Inventário completo das 36 tabelas

Páginas = página impressa (conforme `LISTA DE TABELAS`).

| # | Título | Pág. | Colunas | Linha = | Nº linhas |
|---|---|---|---|---|---|
| 1 | UF direcionadora dos insumos líderes das famílias das areias e britas | 11 | Código · Descrição e unidade · UF Tratada · UF Direcionadora preço · Distância média de transporte estudo (km) | item × UF tratada | 26 |
| 2 | Parcelas de frete sobre preços de areia | 12 | Código · Descrição · **27 UFs** | parâmetro de frete ou insumo | 3 param. + 6 insumos |
| 3 | Parcelas de frete sobre preços de brita | 12 | Código · Descrição · **27 UFs** | idem | 3 param. + 8 insumos |
| 4 | Comparativo das distâncias de transporte para agregados | 13–14 | Material · UF · Distância média estudo (km) · Custo frete (R$/m³) · Distância média amostra (km) · Custo frete (R$/m³) | material × UF | 54 (Britas 27 + Areias 27) |
| 5 | UF direcionadora dos insumos líderes da família do cimento | 15 | Código · Descrição e unidade · UF Tratada · UF Direcionadora preço · UF Considerada p/ transporte · Distância média (km) | item × UF tratada | 16 |
| 6 | Parcelas de frete sobre preços de cimento a granel | 16 | Código · Descrição · **AC · RR · PI** | 3 parâmetros + 1 insumo (M1954) | 4 |
| 7 | UF direcionadora dos insumos líderes da família da cal | 16–17 | idem T5 | item × UF tratada (M0345) | 17 |
| 8 | Parcelas de frete sobre preços de cal | 17 | Código · Descrição · **AC · RR · AP** | 3 parâmetros + 1 insumo (M0345) | 4 |
| 9 | Materiais de ampla comercialização relevantes em obras de infraestrutura | 17–18 | Código · Descrição | insumo relevante | **41** |
| 10 | Distribuição das variações de materiais relevantes | 19 | Faixas de Variações de Preços · Ocorrências Totais (27 UFs) · Percentual | faixa | 12 + 2 totais |
| 11 | Variações dos materiais relevantes em orçamentos | 20 | Código · Descrição e Unidade · **27 UFs** | insumo | 41 |
| 12 | Análise de variações … com variações acima de \|10%\| | 21 (6 partes) | Código · Descrição e Unidade · Máx. · Mín. · Justificativa | insumo | 30 |
| 13 | Distribuição de variações de materiais líderes | 85 | Faixas · Ocorrências Totais (27 UFs) · Proporção Total | faixa | 12 + 2 (3.024 / 27 = 112) |
| 14 | Distribuição de variações de materiais liderados | 85 (2 partes) | idem | faixa | 12 + 2 (7.965 / 27 = 295) |
| 15 | Materiais de ampla comercialização com variação acima de \|20%\| | 87 | Código · Descrição e unidade · **27 UFs** | insumo | 4 |
| 16 | Justificativas para os materiais … acima de \|20%\| | 88 | Código · Descrição e Unidade · Relação de liderança · UFs com variação acima de \|20%\| · Justificativa | insumo | 4 |
| 17 | Distribuição de amplitudes de materiais de ampla comercialização | 89 | Faixas de Amplitudes de Preços · Itens Totais · Proporção Total | faixa | 4 + 3 totais |
| 18 | Análises de amplitudes acima de 100% | 90 (3 partes) | Código · Descrição · Amplitude (Abril/26, Julho/26) · Análise | insumo | **35** |
| 19 | Quantitativos de preços pesquisados p/ materiais de comercialização restrita | 102 | Descrição · Quantidade | métrica | 2 (+nota) |
| 20 | Materiais com aplicação de frete metodológico | 103 | Lista de materiais com DMT · Quantidade | metodologia | 5 + total |
| 21 | Distribuição de variações de materiais de comercialização restrita | 105 | Faixa de variações · Quantidade · % | faixa | 7 + total |
| 22 | Materiais de comercialização restrita relevantes em obras | 105 | Código · Descrição | insumo | 3 |
| 23 | Variação dos materiais de comercialização restrita relevantes | 106 | Código · Descrição e Unidade · **27 UFs** | insumo | 3 |
| 24 | Materiais de comercialização restrita com variação acima de \|20%\| | 113 | Código · Descrição e unidade · **27 UFs** | insumo | 13 |
| 25 | Justificativas de materiais de comercialização restrita … \|20%\| | 114 (3 partes) | idem T16 | insumo | 13 |
| 26 | Distribuição de amplitudes de materiais de comercialização restrita | 117 | Amplitude de preços (%) · métrica · **julho/25 · outubro/25 · janeiro/26 · abril/26 · julho/26** | faixa × (Quantidade, Proporção) | 3 faixas × 2 + total |
| 27 | Comparativo preço varejo convertido em atacado x atacado SICRO – SP | 128 | Código · Descrição e unidade · Modalidade varejo · Margem PAC (%) · Preço varejo convertido (R$) · Preço atacado (R$) · Diferença (%) | insumo × UF | 1 |
| 28 | Quantidade de cotações recebidas por obra, trecho e período | 133 (3 partes) | Obra · Data · UF · Contagem | obra × mês × UF | 76 (Σ = 1.368) |
| 29 | Variáveis disponíveis constantes nas cotações | 135 | Item · Descrição | variável do registro | 23 |
| 30 | Itens SICRO disponíveis nas cotações | 136 (2 partes) | Código SICRO · Descrição · Unidade | insumo | 50 |
| 31 | Resumo de cotações aproveitadas e descartadas | 138 | Descrição · Quantidade · Percentual | métrica | 3 |
| 32 | Classificação dos descartes realizados | 138 | Tipo de descarte · Quantidade · Percentual | motivo | 4 + total |
| 33 | Resultados do tratamento estatístico e comparação com a referência | 140 (6 partes) | 12 colunas (ver §6.5) | insumo × UF | **103** |
| 34 | Faixas de diferença … metodologia do STJ e SICRO | 146 | Faixas de diferença de preços · Quantidade de ocorrências · Percentual | faixa | 3 + total |
| 35 | Faixas de diferença … coeficiente de variação e SICRO | 146 | idem | faixa | 3 + total |
| 36 | Análises para itens com diferença acima de \|25%\| | 147 (10 partes) | Código · Descrição e unidade · UF · Análise FGV IBRE | insumo × UF | **39** |

### 3.1 Tabelas "largas" de 27 UFs

`T2`, `T3`, `T11`, `T15`, `T23`, `T24` usam as 27 colunas de UF **na mesma ordem
regional** do arquivo de preços:

```
AC AM AP PA RO RR TO | AL BA CE MA PB PE PI RN SE | ES MG RJ SP | PR RS SC | DF GO MS MT
```

Três variações de rótulo/precisão a respeitar: `Descrição e unidade` (T15, T24,
2 decimais), `Descrição e Unidade` (T11, T23 — T23 com 1 decimal).

---

## 4. Inventário completo dos 63 gráficos

Cinco tipos, todos com `Fonte: FGV IBRE`.

| Faixa | Tipo | Título-padrão | Eixos |
|---|---|---|---|
| **G1–G41** | Evolução de preços (ampla) | `Gráfico {N} - Evolução dos preços do Item {CÓDIGO} {DESCRIÇÃO}` | X = 10 referências (trimestrais); Y = preço na unidade do item; séries **por região** |
| **G42–G47** | Ordenamento por família (ampla) | `Gráfico {N} - Ordenamento da família {NOME}` | categorias = itens da família; valor = preço |
| **G48–G50** | Evolução de preços (restrita) | `Gráfico {N} - Evolução dos preços do Item {CÓDIGO} {DESCRIÇÃO}` | idem G1–G41 (declarado: "em período de dez referências, por região") |
| **G51–G55** | Preços e amplitude | `Gráfico {N} - Preços e amplitude Item {CÓDIGO} {DESCRIÇÃO}` | categorias = 27 UFs agrupadas por região; valor = preço; amplitude destacada; UFF = menor preço |
| **G56–G62** | Ordenamento na UFF (restrita) | `Gráfico {N} - Ordenamento da família {NOME}` / `… da família de componentes tipo {NOME}` / `… na UFF, para as famílias de: {NOME}` | preços na UFF; categorias = itens da família |
| **G63** | Comparação varejo × atacado | `Gráfico 63 - Comparação atacado x varejo SICRO para o "M0004 – Aço CA 50 – kg" em julho/2026` | X = 27 UFs por região; 2 séries (varejo, atacado) |

> Os rótulos de eixo **não existem no texto extraído** (são imagens). As
> descrições acima vêm dos parágrafos que os introduzem.

### 4.1 G1–G41 — mapeamento 1:1 com a Tabela 9

**Regra confirmada:** `Gráfico N` = N-ésima linha da Tabela 9 (ordem temática,
não alfabética nem por código).

| G | Código | Título | G | Código | Título |
|---|---|---|---|---|---|
| 1 | M0003 | Aço CA 25 | 22 | M1790 | Gás liquefeito de petróleo (GLP) |
| 2 | M0004 | Aço CA 50 | 23 | M0237 | Energia Elétrica |
| 3 | M0014 | Aço CA 60 | 24 | M0446 | Compensado resinado - E = 10 mm |
| 4 | M0424 | Cimento Portland CP II - 32 - saco | 25 | M0447 | Compensado resinado - E = 12 mm |
| 5 | M1954 | Cimento Portland CP II - 32 - a granel | 26 | M0448 | Compensado resinado - E = 14 mm |
| 6 | M0080 | Areia Fina | 27 | M0442 | Compensado plastificado - E = 10 mm |
| 7 | M1383 | Areia Fina Lavada | 28 | M0443 | Compensado plastificado - E = 12 mm |
| 8 | M0028 | Areia Média | 29 | M0459 | Compensado plastificado - E = 14 mm |
| 9 | M0082 | Areia Média Lavada | 30 | M0286 | Tábua - E = 2,5 cm e L = 30 cm |
| 10 | M0081 | Areia Grossa | 31 | M0289 | Tábua - E = 2,5 cm e L = 15 cm |
| 11 | M1382 | Areia Grossa Lavada | 32 | M0290 | Tábua - E = 2,5 cm e L = 10 cm |
| 12 | M1098 | Brita 0 (pedrisco) | 33 | M1429 | Tábua de pinho de terceira - E = 2,5 cm |
| 13 | M0191 | Brita 1 | 34 | M0285 | Pontalete para escoramento - D = 15 cm |
| 14 | M0192 | Brita 2 | 35 | M0301 | Pontalete para escoramento - D = 10 cm |
| 15 | M0193 | Brita 3 | 36 | M1638 | Mourão de madeira - H = 2,10 m e D = 0,10 m |
| 16 | M0808 | Brita 4 | 37 | M1639 | Mourão de madeira - H = 2,20 m e D = 0,15 m |
| 17 | M2356 | Brita para lastro ferroviário | 38 | M2014 | Mourão de madeira - H = 2,20 m e D = 0,10 m |
| 18 | M1135 | Pó de Pedra | 39 | M2119 | Mourão de madeira - H = 2,80 m e D = 0,15 m |
| 19 | M1097 | Pedra de mão ou rachão | 40 | M1812 | Estronca de madeira – D = 20 cm |
| 20 | M0039 | Gasolina comum | 41 | M2281 | Dormente de madeira bitola larga - C = 280 cm, L = 24 cm e H = 17 cm |
| 21 | M0043 | Óleo Diesel | | | |

**Cuidado com capitalização:** o título do gráfico usa Title Case
(`Areia Fina`, `Óleo Diesel`, `Pó de Pedra`) enquanto a Tabela 9 usa sentence
case (`Areia fina`). O G17 perde a palavra "padrão" (`Brita para lastro
ferroviário` vs `Brita padrão para lastro ferroviário`).

### 4.2 Famílias dos gráficos de ordenamento

- **Ampla (G42–47):** Aço CA · Cimento · da Areia · da Areia Lavada · brita · Combustível
- **Restrita (G56–62):** Amortecedor · Ancoragem Estais Fixas · Ancoragem Estais
  Reguláveis · Aparelho de Apoio Metálico Elástico Unidirecional · componentes
  tipo Roller Bit · componentes tipo Roller Bit TCI · Pórtico Metálico
- **Itens dos G51–55:** M0427 · M3276 · M1446 · M1968 · M2027

---

## 5. Insumos líderes de família (parametrização)

| Família | Líder | Onde citado |
|---|---|---|
| Aços | **M0004** (Aço CA 50) | análise G1 |
| Cimento | **M0424** (CP II-32 saco) | §2.1.3, G5 |
| Cal | **M0345** (Cal hidratada saco) | T7, T8 |
| Areias | **M0082** (Areia média lavada) | T12, G8, G10 |
| Britas / agregados | **M0191** (Brita 1) | T12, G12–G19 |
| Compensados (resinados **e** plastificados) | **M0446** (resinado E=10 mm) | T12, G25–G29 |

`M2356` (brita para lastro) é composto: "o preço do item é formado a partir dos
preços das britas 2, 3 e 4".
`M1098` resulta da consolidação dos descontinuados `M0005` (Brita 0) e `M1103`
(Pedrisco).

---

## 6. Regras de negócio, limiares e fórmulas

### 6.1 Limiares

| Limiar | Efeito | Onde |
|---|---|---|
| **\|10%\|** | dispara justificativa textual (T12) e comentário nos gráficos de evolução; destaque de formatação nas T15/T24; sinal de alerta varejo×atacado | §2.2.1.2, §2.2.1.3, §3.2.1, §4 |
| **\|20%\|** (≥ 20,00%) | dispara análise individualizada: matriz por UF (T15/T24) + justificativas (T16/T25). Base: **Parecer nº 94/2026/CCR/CGCIT/DPP/DNIT SEDE** | §2.2.4, §3.2.3 |
| **\|5%\|** (duplo critério) | peso > \|5%\| na valoração da CCU **E** variação > \|5%\| → lista remetida ao arquivo externo `DNIT_II.01.4_…Variacao-CCUs-SICRO` | §2.2.3, §3.2.2 |
| **100%** de amplitude | dispara justificativa (T18 na ampla; bloco em prosa por item na restrita) | §2.3, §3.3.1 |
| **\|25%\|** | dispara análise item-a-item das cotações do DNIT (T36) | §5.3.1 |
| **75% / 125%** | metodologia STJ: < 75% da média = inexequível; > 125% = excessivamente elevado. **Excluir os elevados antes dos inexequíveis** | §5.3 |
| **CV ≤ 25%** | usa **média**; `CV > 25%` usa **mediana** (sem descarte de extremos) | §5.3 |
| **faixa A da curva ABC** | critério de "relevante em obras de infraestrutura" | §3.2.1 |

### 6.2 Fórmula de amplitude (idêntica nas duas partes)

```
Amplitude = (maior preço das 27 UFs − menor preço das 27 UFs) / menor preço das 27 UFs
```

Pré-requisito: **só itens com preço nas 27 UFs**. Na referência: 475 itens
totais → 407 com preço + 68 sem preço (os mesmos 68 zerados do arquivo `II.08.0`).

### 6.3 Grades de faixas (bins) — quatro grades distintas

| Uso | Faixas |
|---|---|
| Variações, ampla (T10, T13, T14) | −100/−50 · −50/−20 · −20/−10 · −10/−5 · −5/0 · **=0** · 0/5 · 5/10 · 10/20 · 20/50 · 50/100 · >100 |
| Variações, restrita (T21) | < −20 · −20/−10 · −10/0 · **=0** · 0/10 · 10/20 · > 20 |
| Amplitudes, ampla (T17) | 0/30 · 30/50 · 50/100 · >100 |
| Amplitudes, restrita (T26) | 0/25 · 25/50 · >50 (×5 referências) |

### 6.4 Conversões e invariantes verificados

| Invariante | Valor |
|---|---|
| `Insumos = Ocorrências ÷ 27` | T10: 1.107/27 = 41 · T13: 3.024/27 = 112 · T14: 7.965/27 = 295 |
| `Máx./Mín.` da T12 | extremos da linha correspondente na T11, entre as 27 UFs |
| Inclusão na T12 | `max(|Máx.|,|Mín.|) > 10%` → 41 − 11 = 30 linhas |
| Linhas da T18 | = faixa `>100%` da T17 = **35** |
| T19 | 916 × 27 = 24.732 · 1.229 − 916 = 313 |
| T20 | 916+129+156+13+15 = **1.229** (= total T21 e T26/julho-26) |
| T28 | Σ Contagem = **1.368** = total da T31 |
| T31/T32 | 428 + 940 = 1.368 · 559+293+66+22 = 940 |
| T33 | 103 linhas = total das T34 e T35 |
| T34 `>25%` = 36; T35 `>25%` = 34 | contagem direta sobre a T33 |
| T36 | **39** linhas = união dos dois critérios (`|dif_STJ|>25 OR |dif_CV|>25`) — **regra não enunciada no texto** |
| Diferença % (T33) | `(Resultado SICRO ÷ Resultado cotações) − 1` |

### 6.5 Colunas da Tabela 33 (12)

`Código` · `Descrição e unidade` · `UF` · `Quantidade de cotações` ·
`Cotações utilizadas - metodologia STJ` ·
`Resultado cotações DNIT - metodologia STJ (R$)` · `CV Total Cotações DNIT` ·
`Resultado cotações DNIT - metodologia CV (R$)` · `Resultado SICRO Jul/26 (R$)` ·
`Origem de preço Jul/26` · `Diferença % STJ - SICRO` · `Diferença % CV - SICRO`

Comportamentos: `Quantidade = 1` → `CV = "-"` e as duas metodologias coincidem;
`CV ≤ 25%` e nenhum descarte → resultados iguais; `CV > 25%` → coluna CV traz a
mediana. A coluna `Origem de preço Jul/26` usa as **mesmas siglas** do arquivo
`II.09.0` (observadas: PC, PCT, PCI, PMP, PMT, PRI, PFM).

### 6.6 Frete metodológico

- Fórmula: preço de aquisição na **UFF** (capital da UF do fabricante/fornecedor)
  **+** custo de frete até a capital de cada UF.
- Agregados (areia/brita): frete = custo do frete × **média das distâncias** da
  pedreira/areal até a capital da UF.
- Cimento e cal: distância da **capital da UF de imputação** até a **capital da
  UF de destino**.
- Tabelas de parâmetros (T2/T3/T6/T8) têm sempre a estrutura:
  `Distância/DMT (km)` → `Valor do frete (R$/km/m³ ou R$/kg)` →
  `Frete médio / Valor total` → `% de frete por insumo`.
- Percentuais desta referência: cimento a granel AC 28% · RR 41% · PI 32%;
  cal ensacada AC 14% · RR 23% · AP 21%.
- Distâncias: 514,5 km (AC) · 864,5 km (RR) · 438,8 km (PI) · 735,5 km (AP).

### 6.7 Conceitos-chave (definições literais do relatório)

- **Família:** "conjunto dos insumos cujas especificações guardam correspondência
  entre si e que tendem a se diferenciar apenas por seus tamanhos, medidas,
  capacidades ou outras características particulares. A esse conjunto o FGV IBRE
  chama de famílias" (§3.4). Serve para acompanhar a **lei de formação de preços**.
- **Ampla comercialização:** alta capilaridade nacional; preço por pesquisa nas
  27 UFs.
- **Comercialização restrita:** "itens não disponíveis na maioria das UFs, sendo
  comercializados diretamente pelos fabricantes ou fornecedores"; preço = UFF +
  frete metodológico; variação medida **na UFF**.
- **Líder / liderado:** o liderado tem preço obtido por **parametrização** a
  partir do líder. Coluna `Relação de liderança` ∈ {`LÍDER`, `LIDERADO`}.
- **UFF (UF fabricante):** origem do frete; tipicamente o **menor preço** do item.
- **Tratamento:** ajuste do preço coletado antes da publicação, por dois motivos
  canônicos — manter o ordenamento da família, ou absorver variações abruptas.
- **Suavização / abrandamento:** incorporação **parcial** da variação até
  confirmação do novo nível de preço.
- **Balizamento:** validação contra fonte externa — SINAPI, Portal da
  Transparência, PNCP, compras públicas, ANP, cotações do DNIT, varejo convertido.
- **Interpolação/extrapolação:** obrigatoriamente **dentro da mesma família**,
  em função de peso, volume, diâmetro, classe de resistência.

### 6.8 Quantitativos da referência (todos os números publicados)

| Métrica | Valor |
|---|---|
| Insumos zerados (todas as UFs) | **68** (sigla `PRZ`) |
| Materiais relevantes em infraestrutura (ampla) | **41** |
| Ocorrências de variação (relevantes) | 1.107 = 41 × 27 |
| Materiais líderes | **112** (3.024 ocorrências) |
| Materiais liderados | **295** (7.965 ocorrências) |
| Itens com variação ≥ \|20%\| — ampla | **4** (M0167, M0168, M1397, M0237) |
| Itens com amplitude > 100% — ampla | **35** |
| Universo de amplitude — ampla | 475 = 407 com preço + 68 sem |
| Materiais de comercialização restrita | **1.229** (916 frete metodológico + 129 estimados + 156 índice + 13 extra/interpolados + 15 imputados) |
| Preços restrita estabelecidos | 24.732 = 916 × 27 |
| Itens com tratamento + frete (PCT/PFM) | 119 |
| Itens com variação ≥ \|20%\| — restrita | texto diz **10**, tabelas listam **13** |
| Itens com amplitude > 100% — restrita | **1** (M0042, 111,48%) |
| Insumos do varejo | até **15** (areia, brita, cimento, vergalhão) |
| Cobertura do varejo | 332 / 405 posições ≈ **82%** (405 = 15 × 27) |
| Margem PAC (IBGE) | **34,28%** |
| Cotações recebidas do DNIT | **1.368** (5 lotes) → 428 aproveitadas (31%), 940 descartadas (69%) |
| Balizamentos cotação × SICRO | **103** pares (insumo × UF), 35 códigos |
| Ocorrências > \|25%\| | **39** (26 de origem natural) |
| Esforço de pesquisa | 842/722 empresas (SP/RJ, liderados) · 1.184 (aço/areia/brita/cimento, 27 UFs) · 2.647 (varejo) · 4.335 (líderes) |

---

## 7. Templates de texto (base para `text_generator.py`)

O relatório é fortemente **templatizado**. Abaixo os padrões confirmados, com
partes fixas e slots. Há também **blocos copiados literalmente** entre seções —
candidatos a snippet único.

### 7.1 Abertura de análise de gráfico de evolução

```
Os preços de {MÊS} de {ANO} apresentaram variações entre {MIN} e {MAX}.
```
Variantes literais: `apresentaram variações entre` · `apresentam variações entre`
· `Os preços de referência de {MÊS} de {ANO}…` · `Os preços para referência de
{MÊS} de {ANO}…` · `As variações dos preços em {MÊS} de {ANO} oscilaram entre…` ·
`…apresentaram variações entre referências de {MIN} a {MAX}` ·
`…apresentaram variação em relação à referência de {MÊS ANTERIOR} de {ANO} entre…`

A faixa `{MIN}`/`{MAX}` = mínimo e máximo da linha do item na Tabela 11.

### 7.2 Cláusulas por UF (vocabulário fechado de causas)

| Causa | Template literal |
|---|---|
| Parametrização | `nas UFs {UFs}, a variação observada decorre da metodologia de parametrização, tendo como base o insumo líder {CÓDIGO}` |
| Preço do respondente | `na UF {UF}, da alteração dos preços informados pelos respondentes` |
| Nova coleta | `na UF {UF}, da obtenção de uma nova coleta para um insumo anteriormente parametrizado` |
| Imputação | `na UF {UF}, da metodologia de imputação de preços por meio da UF direcionadora {UF}` |
| Troca de painel | `na UF {UF}, da mudança de respondentes` |
| Índice | `na UF {UF}, da variação do índice adotado para o insumo` |
| Tratamento | `na UF {UF}, da aplicação de tratamento estatístico {detalhe}` |
| Repasse | `na UF {UF}, do aumento de preços repassado pelo respondente` |
| Estimativa balizada | `na UF {UF}, a variação observada decorre da estimativa do preço, ratificada por meio do balizamento do preço formado` |
| Madeireiro (ida) | `da mudança de preço aplicado com a metodologia específica para itens madeireiros para preço coletado com tratamento` |
| Madeireiro (volta) | `da mudança de preço coletado com tratamento para preço aplicado com a metodologia específica para itens madeireiros` |
| Coleta simples | `resulta de preços coletados por meio da pesquisa` / `…com tratamento` / `…e respaldados por balizamento` |
| Frete (restrita) | `Demais variações decorrem da aplicação do frete metodológico.` |

Fechamentos:
- `observando-se, ainda, nas UFs {UFs}, a elevação dos custos de combustível, refletida no aumento dos valores de frete.`
- `Nas UFs {UFs}, observou-se, ainda, a elevação dos custos de combustível, refletida no aumento dos valores de frete.`
- `As demais variações observadas decorreram da aplicação da metodologia de parametrização com base no insumo líder {CÓDIGO}.`
- `As demais variações acima de 10%, em módulo, tiveram origem na metodologia de parametrização com base no insumo líder {CÓDIGO}.`
- `As demais variações observadas decorreram da aplicação da metodologia específica para itens madeireiros, descrita no Volume 03: Preços Referenciais da 2ª edição Manual de Custos de Infraestrutura de Transportes.`
- `As demais UFs apresentaram cenário de estabilidade.`

**Duas formas de encadeamento** (escolher uma e ser consistente):
1. **Elíptica com `;`** — só a primeira cláusula traz o verbo:
   `…decorre da metodologia X; nas UFs {…}, da alteração dos preços…; e na UF {…}, da variação do índice…`
2. **Frases completas com `.`** — cada cláusula repete o verbo:
   `Nas UFs {…}, a variação observada decorre de… . Na UF {…}, a variação observada decorre de… .`

### 7.3 Rótulos de justificativa (T12, T16, T25)

Prefixo tipificado + `:` + narrativa. Catálogo observado:

`Variação de preços pesquisados` · `Variação de preço pesquisado` ·
`Variação de preços pesquisados e imputados` ·
`Variação de preços pesquisados, parametrizados e com incidência de frete` ·
`Variação de preços pesquisados, parametrizados, tratados, por índice e com incidência de frete` ·
`Variação de preços parametrizados, pesquisados, tratados, por índice e com incidência de frete` ·
`Variação de preços pesquisados, imputados, estimados e com incidência de frete` ·
`Variação de preços pesquisados, parametrizados, imputados, tratados e com incidência de frete` ·
`Variação de preços pesquisados, parametrizados, imputados e com incidência de frete` ·
`Variação de preços parametrizados` · `Variação de preços de fontes externas` ·
`Variação de preços pesquisados, estimados e imputados` ·
`Variação de preços pesquisados e frete` ·
`Variação de preço pesquisado e parametrizado` ·
`Variação de preço pesquisado, parametrizado e imputado` ·
`Variação por metodologia de preços de itens madeireiros` ·
`Variação de preços pesquisados e metodologia de preços de itens madeireiros` ·
`Alteração de metodologia` · `Alteração de metodologia e preços pesquisados` ·
`Alteração de metodologia, preços pesquisados e parametrizados` ·
`Alteração de metodologia, preços pesquisados e metodologia de preços de itens madeireiros` ·
`Ampliação de amostra` · `Nova coleta em confirmação`

**Regra:** o rótulo é a enumeração dos tipos de origem que produziram as
variações — montável a partir das siglas do arquivo `II.09.0`.

### 7.4 Textos-boilerplate por classificação de material (T18)

A coluna de análise da T18 é **mesclada por grupo**, um parágrafo canônico por
classificação — praticamente invariante entre referências:

| Classificação | Itens nesta referência |
|---|---|
| `Natural - Mineral e Derivados` (agregados) | 15 (M1383, M0028, M0082, M0081, M1382, M1098, M0191, M0192, M0193, M0808, M1097, M1135, M2356, M0222, M1755) |
| cimento (ausência de unidades fabris no Norte) | 2 (M0424, M1954) |
| `Minerais Industrializados` | 5 (M0083, M0084, M0344, M0345, M0140) |
| `Naturais – Orgânicos e Derivados` (madeiras) | 8 (M0284, M0285, M0286, M0289, M0290, M0301, M1358, M1429) |
| artefatos de concreto (subtipo de Natural-Mineral) | 4 (M2164, M2165, M2167, M2187) |
| individual | 1 (M0026) |

O trecho "Lembrando especialmente de situações encontradas na região Norte, onde
as rochas próprias para britagem são escassas, devido principalmente ao extenso
manto sedimentar…" é **literalmente idêntico** nos blocos de agregados e de
minerais industrializados.

### 7.5 Template de identificação no arquivo de origens (§3.1.1–3.1.5)

```
Estes itens são identificados no arquivo DNIT_II.09.0_2ºOrigem-Precos-SICRO-Ref-{Mês}.{Ano},
com a sigla "{SIGLA}" {em todas as UFs | na UF fabricante e "{SIGLA2}" nas demais UFs},
totalizando {N} insumos na referência {mês} de {ano}.
```

| § | Siglas | N |
|---|---|---|
| 3.1.1 | `PCT` na UFF + `PFM` nas demais | 119 |
| 3.1.2 | `PCI` em todas as UFs | 156 |
| 3.1.3 | `PEI` em todas as UFs | 13 |
| 3.1.4 | `PRE` em todas as UFs | 129 |
| 3.1.5 | `PC` ou `PCT` na UFF + `PRI` nas demais | 15 |

### 7.6 Template de "Preços e amplitude" (G51–G55)

```
Pode-se notar que a UFF deste item é {ESTADO POR EXTENSO} na {REGIÃO} (menor preço e,
portanto, preço na origem da UF Fabricante). Os maiores preços encontram-se na Região
Norte, onde os custos de transporte aumentam devido ao aumento da distância.
```
Variantes curtas: `A análise demonstra que o item {CÓDIGO} apresenta
comportamento homogêneo entre as unidades da federação…` ·
`Para o item {CÓDIGO}, não existem destaques de amplitudes a serem apresentados.`

### 7.7 Análise de série temporal (T26)

```
…faixa de amplitude de até {FAIXA}, que passou de {P_INICIAL} em {REF_INICIAL} para
{P_FINAL} em {REF_FINAL}, evidenciando {redução|aumento} gradual da dispersão…
```
Totalmente derivável dos dados da tabela — 3 faixas × (primeira, última referência).

### 7.8 Parágrafos condicionais de ausência (seções que desaparecem)

- `Não há nessa referência destaques em ordenamentos de preços que mereçam estar detalhadas neste relatório.` (§3.4.2)
- `Em análise dos demais itens relevantes de comercialização restrita, verificou-se que, na referência em questão, não houve variações superiores a 10% em módulo. Dessa forma, não se identificaram ocorrências que demandassem análise individualizada dos movimentos de preço, razão pela qual não é apresentada tabela específica para esse grupo de insumos.` (§3.2.1)
- `Na referência de julho de 2026, não foram identificados aprimoramentos metodológicos a serem incorporados…` (§1.1)

### 7.9 Blocos reaproveitados literalmente (fonte única de verdade)

| Bloco | Onde repete |
|---|---|
| Cadeia siderúrgica / minério de ferro / Estreito de Ormuz | análise G1 **e** G2 (idênticos, muda só a frase de ligação) |
| Óleo diesel / Estreito de Ormuz | análise G6-areias (p. 40) **e** G13-britas (p. 51) — inclui o **mesmo erro** "a alta nos preços dos reflete" |
| Nota de família mineral (`Destaca-se que, os gráficos {N1} ao {N2} tratam de insumos pertencentes à família das {FAMÍLIA}…`) | areias e britas |
| Cenário cimenteiro (coque ≈ 40% do custo, MCMV) | T12/M0424 **e** análise G4 |
| Carboneto de tungstênio / exportações da China | T25 M1895 **e** M2147 (idênticos) |
| SP integralmente incorporado + diferencial de fretes | T25 M3237 **e** M3239 (idênticos) |
| Template UFF | G51 **e** G53 |
| Parágrafo de finalidade de \|20%\| | §2.2.4 **e** §3.2.3 (3 slots de diferença) |
| Critério \|5%\| em CCU | §2.2.3 **e** §3.2.2 |
| Fórmula de amplitude | §2.3 **e** §3.3 |

### 7.10 Banco de sentenças da Tabela 36 (cotações)

Os pareceres da T36 são montados por blocos. Principais:

- **Fragilidade amostral:** `A quantidade reduzida de cotações obtidas na presente amostragem não confere a robustez estatística necessária para mitigar distorções, comprometendo a representatividade real do mercado e inviabilizando a realização de comparações consistentes e fundamentadas.`
- **Desalinhamento geográfico:** `Além da fragilidade amostral, constatou-se um desalinhamento geográfico em relação às premissas metodológicas estabelecidas pelo SICRO. Identificou-se que a cotação realizada pelo DNIT considerou uma localidade fora da região metropolitana da capital.`
- **Material natural:** `Ressalta-se que, por se tratar de material de origem natural, a formação de preço possui elevada sensibilidade à localização das jazidas, à disponibilidade regional do insumo e às condições logísticas de transporte e fornecimento.`
- **Balizamento:** `Como etapa complementar de validação, o preço referencial do SICRO foi comparado {ao SINAPI | com outra fonte balizadora da própria unidade da federação | com o SINAPI e outras fontes de balizamento, como catálogos, pesquisa de mercado, marketplaces e sítios eletrônicos de fornecedores}, observando-se convergência entre os valores.`
- **Compatibilidade:** `A compatibilidade verificada entre {os diferentes sistemas referenciais | as diferentes fontes de referência} reforça {a coerência, a consistência e a confiabilidade | a coerência, a consistência e a segurança jurídica} do preço referencial formado pelo SICRO.`
- **Compromisso:** `Por fim, o FGV IBRE permanece empenhado na ampliação da base de coletas desse insumo, considerando que o preço referencial adotado na referência de julho de 2026 foi obtido por meio de {parametrização | imputação | coleta | frete metodológico}.`
- **Canal de comercialização:** `constatou-se uma divergência estrutural entre as fontes de consulta: a cotação enviada pelo DNIT apresenta preços obtidos diretamente junto a fabricantes, refletindo condições comerciais de topo de cadeia. Já no caso referencial do SICRO os valores são atribuídos a distribuidoras.`
- **Ganho de escala:** `refere-se ao fornecimento de {QTD}` (160 m³, 189 t ≈ 283 m³, 1.296 un)
- **Licença ANM:** `A única cotação que atende aos critérios de localização não possui licença vigente junto à ANM, requisito observado pelo SICRO na formação de seus preços referenciais para insumos de origem mineral.`
- **STJ × CV** (matriz 2×2): `As cotações remanescentes da amostra, após a aplicação dos descartes conforme a metodologia estabelecida pelo STJ, demonstram convergência com o preço referencial formado. No entanto, quando as cotações remanescentes são submetidas à análise por meio do coeficiente de variação, observa-se heterogeneidade entre os dados.`

---

## 8. Seções 4 a 7 — particularidades

### 8.1 §4 Varejo

- Contrato prevê pesquisa varejista de **até 15 insumos** das famílias areia,
  brita, cimento e vergalhão de aço; frequência **trimestral**; capitais/RMs das
  27 UFs.
- Conversão varejo→atacado pela **margem PAC/IBGE = 34,28%** (provisória, até a
  série histórica permitir margem própria — prevista para outubro/2026).
- Limitação registrada: a margem PAC é **única por CNAE nacional** (CEMPRE),
  sem abertura por insumo nem por UF.
- Modalidades de coleta: `VV` (varejo comum), `VX` (varejo corporativo).
- §4.2: o DNIT **vetou** (Ofício nº 124739/2026, SEI 24577501) as propostas de
  substituir M0193/M0808 e de uniformizar preços das areias.
- Entregável: `DNIT_II.01.5_2ºRR_15-08.2026_Resultado-Varejo-SICRO`.

### 8.2 §5 Cotações do DNIT

- Base: **§4º do art. 10 da IN nº 10, de 09/10/2024**, em resposta ao
  **Acórdão nº 2178/2023-TCU-Plenário**.
- 5 lotes de ofícios (03/2025 a 12/2025), 1.368 cotações, janela jul/2022–mai/2025.
- 6 tratamentos: conversão de unidades · índice setorial por tipo de insumo ·
  descarte de frete FOB · só fornecedores com CNAE atacadista · atualização até
  a data-base · descarte de insumos zerados no SICRO.
- Descartes: varejo 559 (60%) · FOB 293 (31%) · descrição incompatível 66 (7%) ·
  CNAE não-atacado 22 (2%).
- Caso positivo (§5.3.2): revisão da família dos **gabiões**, cujos preços
  saíram da faixa > \|25%\| após incorporação das cotações.

### 8.3 §6 Esforço de pesquisa

Uma página, sem tabelas. Quatro blocos, cada um com até 3 indicadores
(empresas mapeadas · sugestões de preços da referência · preços no banco):

| Escopo | Mercado | Abrangência | Empresas | Sugestões | Banco |
|---|---|---|---|---|---|
| insumos **liderados** | produtor ou distribuidor | SP e RJ | 842 / 722 | 542 | 1.365 |
| aço, areia, brita, cimento | produtor e distribuidor | 27 UF | 1.184 | 663 | 1.050 |
| aço, areia, brita, cimento | varejo | 27 UF | 2.647 | 4.109 | — |
| insumos **líderes de família** | produtor ou distribuidor | 27 UF | 4.335 | 3.536 | 7.807 |

### 8.4 §7 Manifestação sobre pareceres

Estrutura em 4 camadas: `Considerando…` (×3) → `{Título do apontamento}:` →
citação recuada → `Manifestação do FGV IBRE:` → resposta.
Nesta referência: 1 apontamento, sobre divergência **TPC × SICRO** em 6 insumos
(`E8533`, `E8887`–`E8891`), causada por preços sem o frete metodológico até SP.

### 8.5 Apêndice A

Apenas título + URL:
`https://app-ibre.fgv.br/Entregaveis_Externo/Login.aspx`
(portal de entregáveis externos do FGV IBRE, onde fica o Painel de Preços
Referenciais em Power BI).

---

## 9. Arquivos citados pelo relatório

| Arquivo | Papel |
|---|---|
| `DNIT_II.08.0_2ºResultado-Final-SICRO-Ref-Jul.2026` | preços referenciais (valores) |
| `DNIT_II.09.0_2ºOrigem-Precos-SICRO-Ref-Jul.2026` | origem metodológica do preço (siglas) |
| `DNIT_II.01.4_2ºRR_15-08.2026_Variacao-CCUs-SICRO(.xlsx)` | variações em CCUs > \|5%\|; **fonte da formatação** das tabelas de \|20%\| |
| `DNIT_II.01.5_2ºRR_15-08.2026_Resultado-Varejo-SICRO` | resultado da pesquisa de varejo |
| `Volume 03: Preços Referenciais` da 2ª ed. do Manual de Custos de Infraestrutura de Transportes | metodologias (agregados, cimento, cal, itens madeireiros) |
| `Manual de Orientação: Pesquisa de Preços – 4ª edição` (STJ) | metodologia 75%/125% e CV |

---

## 10. Inconsistências do documento-fonte (decidir antes de automatizar)

Encontradas na leitura; a automação pode corrigi-las ou reproduzi-las, mas a
decisão precisa ser explícita.

**Numéricas / lógicas**
1. §3.2.3 diz "**10** itens" acima de \|20%\|, mas T24 e T25 têm **13** linhas.
2. §3.4.1 diz "**nove** famílias", mas publica **7** gráficos (G56–G62).
3. T36 tem **39** linhas = união dos critérios STJ **ou** CV; o texto não enuncia
   essa regra (T34 diz 36, T35 diz 34).
4. T23 arredonda para 1 decimal enquanto os comentários dos G48–G50 usam 2 —
   as duas visões não coincidem (`0,20%` vs `0,25%`).
5. T28 tem chave duplicada com contagens diferentes (`Represa 3 Fronteiras | ago-24 | CE` → 10 e 17) e UFs incoerentes (`BR-153/PR` com UF `MG`).
6. `M2426` aparece na T33 mas **não** na T30.
7. Nenhum valor da T33 é exatamente 10,00% ou 25,00% — a convenção de fronteira
   dos bins nunca é exercitada; fixe-a explicitamente (sugestão: `<10`,
   `[10,25]`, `>25`).

**Redacionais**
8. Análise do G2: template de "dois fatores" editado à mão virou
   "um fator principal, o primeiro sendo … em função do refinamento que seria os
   reajustes de preços" — frase quebrada.
9. "a alta nos preços **dos** reflete o impacto direto" — substantivo faltando,
   nas **duas** cópias do bloco do diesel.
10. `apesentam` (§2.2.1.3), `preços estimado` (§2.2.4 e §3.2.3), `capacidade’ de
    carga` (M0377, em T24 e T25), falta de pontuação antes de "Já" (análise G13).
11. Análise do G14/M0192: duas frases consecutivas com **o mesmo motivo e o mesmo
    líder** que deveriam ter sido fundidas em uma lista de UFs — indica geração
    por grupo sem merge posterior. Mesmo defeito em M1098 e M0191.
12. Rótulo da última coluna da T18 muda entre partes: `Análise` (1/3) →
    `Ocorrências` (2/3 e 3/3); e `Abril/26` vira `abril/26`.
13. Separador de milhar inconsistente (`1038`, `1073`, `7410,9054` sem ponto vs
    `1.229`, `1.165`, `1.321,2469` com ponto).
14. Título/capitalização divergente entre T9, T11, T12 e títulos de gráfico
    (Title Case × sentence case; en dash × hífen; "Brita **padrão** para lastro"
    perdendo "padrão" no G17).

**Artefatos de extração do PDF** (não são erros do relatório, mas afetam parsing)
15. Espaços espúrios dentro de palavras e números: `pesquis a`, `observando -se`,
    `20 26`, `1 3,36%`, `R$ 5, 67`, `3. 536`. Qualquer regex sobre códigos,
    percentuais ou datas precisa tolerar `\s*` interno.
16. Cabeçalhos de tabela verticalizados (um rótulo quebrado em 2–4 linhas).
17. Descrições longas quebradas em várias linhas dentro da mesma célula.
18. Formato de data misto na T28: `jul-24` (partes 1-2) vs `abr/25` (parte 3).

---

## 11. O que a aplicação precisa produzir (resumo operacional)

Para reproduzir este tomo a partir dos dois Excel de entrada (+ histórico de
referências anteriores):

| Artefato | Quantidade | Deriva de |
|---|---|---|
| Tabelas de parâmetros de frete | 4 (T2, T3, T6, T8) | parâmetros externos (DMT, R$/km) — **não estão nos 2 Excel** |
| Tabelas de UF direcionadora | 3 (T1, T5, T7) | parâmetros externos |
| Lista de relevantes | 2 (T9, T22) | lista curada (faixa A da curva ABC) |
| Tabelas de variação por UF | 3 (T11, T15, T23, T24) | preço atual × preço da referência anterior |
| Tabelas de distribuição | 6 (T10, T13, T14, T17, T21, T26) | binning das variações/amplitudes |
| Tabelas de justificativa | 4 (T12, T16, T18, T25) | origem do preço (`II.09.0`) + curadoria textual |
| Tabelas de cotações | 9 (T19, T20, T28–T36) | arquivos de cotação do DNIT (entrada adicional) |
| Gráficos de evolução | 44 (G1–41, G48–50) | série histórica de 10 referências, agregada por região |
| Gráficos de ordenamento | 13 (G42–47, G56–62) | preço por item dentro da família (UFF na restrita) |
| Gráficos de amplitude | 5 (G51–55) | preço por UF + amplitude |
| Gráfico varejo × atacado | 1 (G63) | pesquisa de varejo + margem PAC |

**Entradas que ainda não temos** (necessárias para o relatório completo):
histórico de preços das 10 referências anteriores; classificação
líder/liderado e família por insumo; classificação ampla/restrita;
classificação de material (`Natural - Mineral e Derivados` etc.);
lista de relevantes (curva ABC); pesos em CCU; parâmetros de frete (DMT,
R$/km); base de cotações do DNIT; base do varejo.
