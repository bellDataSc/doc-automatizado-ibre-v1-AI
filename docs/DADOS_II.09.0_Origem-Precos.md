# DNIT_II.09.0 — Origem de Preços SICRO (Ref. Jul/2026)

Documentação técnica do arquivo de entrada de **origem metodológica do preço**.
Gerada por inspeção direta do arquivo (openpyxl + pandas).

- **Nome do arquivo:** `DNIT_II.09.0_2ºOrigem-Precos-SICRO-Ref-Jul.2026.xlsx`
- **Tamanho:** ~0,31 MB
- **Papel no processo:** para cada insumo × UF, informa **como** o preço
  referencial foi obtido (coletado, imputado, estimado, com frete
  metodológico, zerado…). É o arquivo citado no relatório como
  `DNIT_II.09.0_2ºOrigem-Precos-SICRO-Ref-Jul.2026`.
- **Par obrigatório:** `DNIT_II.08.0_2ºResultado-Final-SICRO-Ref-Jul.2026.xlsx`
  (os **valores**). Mesma lista de 2.395 códigos e mesma ordem de UFs.
- Título interno (célula `D1`): `Planilha de Origem Metodológica de Preço - Ref.Julho de 2026`

## Estrutura da pasta de trabalho

- Planilhas: **2**
  - `ENTREGA` — visível, é a planilha de dados.
  - `Tabela RGB utilizada` — **oculta**, auxiliar de cores (ver seção final).
- `ENTREGA`: painel congelado em `D6`; dimensões `A1:AD2424`; 80 faixas
  mescladas (quase todas no bloco de legenda do rodapé).

### Mapa de linhas da aba `ENTREGA`

| Linha | Conteúdo |
|---|---|
| 1-4 | `A1:C4` mesclado (marca) · `D1:AD4` mesclado = título `Planilha de Origem Metodológica de Preço - Ref.Julho de 2026` |
| **5** | **Cabeçalho das colunas** |
| **6 … 2400** | **Dados — 2.395 insumos, 1 por linha** |
| 2401-2402 | vazias |
| **2403 … 2423** | **Bloco de legenda** (glossário das siglas, col. `A` e `G`) **+ tabela-resumo** (col. `V` a `AD`) |

> Atenção: o bloco do rodapé tem dois conteúdos lado a lado na mesma faixa de
> linhas — o glossário em duas colunas (`A…` e `G…`) e a tabela de contagem
> (`V`…`AD`). Ver detalhamento abaixo.

## Colunas (30)

| Col | Cabeçalho (linha 5) | Tipo | Observações |
|---|---|---|---|
| A | `CÓDIGO` | texto | Código SICRO. Igual ao do arquivo `II.08.0` |
| B | `DESCRIÇÃO DO ITEM` | texto | Nome do cabeçalho **difere** do `II.08.0` (`DESCRIÇÃO`) |
| C | `UNIDADE DO ITEM` | texto | Nome do cabeçalho **difere** do `II.08.0` (`UNIDADE`) |
| D … AD | 27 siglas de UF | texto | **Sigla de origem do preço** (3 letras), ex. `PFM`, `PC`, `PRE` |

Ordem das 27 UFs — **idêntica** à do `II.08.0` (validado):

```
AC, AM, AP, PA, RO, RR, TO,          # Norte
AL, BA, CE, MA, PB, PE, PI, RN, SE,  # Nordeste
ES, MG, RJ, SP,                      # Sudeste
PR, RS, SC,                          # Sul
DF, GO, MS, MT                       # Centro-Oeste
```

## Conteúdo dos dados

- **2.395 insumos × 27 UFs = 64.665 células**, nenhuma vazia.
- Conjunto de códigos **idêntico** ao do `II.08.0` (0 códigos exclusivos de
  qualquer lado).
- Distribuição por prefixo idêntica: `M` 1.704 · `E` 457 · `A` 89 · `P` 145.

### Siglas de origem observadas nos dados (15)

Contagem sobre as 64.665 células. Os percentuais conferem com a tabela-resumo
do próprio arquivo (rodapé, colunas `V:AD`).

| Sigla | Descrição (legenda do arquivo) | Células | % |
|---|---|---:|---:|
| `PFM` | Preço com frete metodológico | 31.512 | 48,73% |
| `PRE` | Preço referencial estimado | 9.051 | 14,00% |
| `PCI` | Preço coletado atualizado por índice | 5.247 | 8,11% |
| `PMP` | Precificado por metodologia de parametrização | 4.740 | 7,33% |
| `SDP` | Salário de fontes secundárias de dados públicos | 3.285 | 5,08% |
| `PRI` | Preço referencial imputado | 2.674 | 4,14% |
| `PC` | Preço coletado | 2.141 | 3,31% |
| `PRZ` | Preço referencial zerado | 1.836 | 2,84% |
| `PMT` | Precificado por metodologia de parametrização com tratamento | 1.824 | 2,82% |
| `PCT` | Preço coletado com tratamento | 645 | 1,00% |
| `SPC` | Salário definido pelo piso da categoria | 627 | 0,97% |
| `PEE` | Precificado por estudo específico | 621 | 0,96% |
| `PEI` | Precificado por extrapolação ou interpolação | 405 | 0,63% |
| `PFE` | Preço de fontes externas | 54 | 0,08% |
| `SMN` | Salário substituído pelo mínimo nacional/estadual | 3 | 0,00% |
| | **Total** | **64.665** | **100%** |

Siglas **previstas na legenda mas com contagem 0** nesta referência:
`PND` (Preço não determinado) e `SCM` (Salário definido por coleta de mercado).

### Glossário completo (texto literal do rodapé, linhas 2403-2423)

- **PND — Preço não determinado**: "Representa um insumo com previsão de
  pesquisa cujo preço referencial não pôde ser determinado."
- **PRZ — Preço referencial zerado**: "Representa um insumo sem previsão de
  pesquisa cujo preço referencial é divulgado com valor igual a zero."
- **PCI — Preço coletado atualizado por índice**: "Representa um insumo cujo
  preço referencial foi calculado pelo reajustamento do valor divulgado no mês
  de referência anterior, por meio da aplicação de índice de atualização
  específico ou setorial. Um insumo com origem de preço tipo PCI possui
  previsão de pesquisa, mas a coleta não foi realizada no mês de referência,
  seja por premissa metodológica de precificação, seja por descadastramento de
  empresas respondentes da amostra."
- **PC — Preço coletado**: "Representa um insumo cujo preço referencial foi
  calculado a partir de preços pesquisados."
- **PCT — Preço coletado com tratamento**: "Representa um insumo cujo preço
  referencial foi calculado a partir de preços pesquisados, com a posterior
  aplicação de tratamentos para adequá-lo aos critérios de formação de preços
  referenciais."
- **PFM — Preço com frete metodológico**: "Representa um insumo cujo preço
  referencial foi calculado a partir de preços de aquisição pesquisados na
  localidade da empresa fabricante, produtora ou distribuidora, com acréscimo
  do custo de transporte computado por metodologia específica de precificação
  do frete."
- **PEE — Precificado por estudo específico**: "Representa um insumo cujo preço
  referencial foi calculado por metodologia específica, seja por premissa de
  precificação, seja por restrições de mercado."
- **PMP — Precificado por metodologia de parametrização**: "Representa um
  insumo cujo preço referencial foi calculado por metodologia de parametrização
  em função de sua correlação com o preço do insumo líder da família. Um insumo
  com origem de preço tipo PMP não possui previsão de pesquisa no mês de
  referência."
- **PMT — Precificado por metodologia de parametrização com tratamento**:
  "Representa um insumo cujo preço referencial foi calculado por metodologia de
  parametrização em função de sua correlação com o preço do insumo líder da
  família, com a posterior aplicação de tratamentos para adequá-lo aos
  critérios de formação de preços referenciais. Um insumo com origem de preço
  tipo PMT não possui previsão de pesquisa no mês de referência."
- **PRE — Preço referencial estimado**: "Representa um insumo cujo preço
  referencial foi estimado por procedimentos diversos, ou cujo preço
  referencial calculado ainda requer confirmação do nível de preço."
- **PEI — Precificado por extrapolação ou interpolação**: "Representa um insumo
  com previsão de pesquisa cujo preço referencial foi estimado pelas técnicas
  matemáticas de interpolação ou extrapolação em função de características dos
  demais insumos da mesma família."
- **PRI — Preço referencial imputado**: "Representa um insumo com previsão de
  pesquisa cujo preço referencial foi imputado de outra localidade."
- **PFE — Preço de fontes externas**: "Representa um insumo cujo preço
  referencial foi calculado a partir de preços obtidos em fontes externas de
  pesquisa, como bases de dados oficiais e mídias especializadas."
- **SMN — Salário substituído pelo mínimo nacional**: "Representa uma categoria
  de mão de obra cujo salário referencial foi definido a partir do
  salário-mínimo nacional."
- **SPC — Salário definido pelo piso da categoria**: "Representa uma categoria
  de mão de obra cujo salário referencial foi definido a partir do piso
  estabelecido em Convenção Coletiva de Trabalho."
- **SDP — Salário de fontes secundárias de dados públicos**: "Representa uma
  categoria de mão de obra cujo salário referencial foi calculado a partir de
  bases de dados oficiais."
- **SCM — Salário definido por coleta de mercado**: "Representa uma categoria
  de mão de obra cujo salário referencial foi calculado a partir de pesquisa de
  mercado."

Layout do glossário no rodapé: textos alternam entre a coluna `A` (linhas
2403, 2405, 2407, 2410, 2412, 2414, 2417, 2420, 2423) e a coluna `G` (linhas
2403, 2405, 2407, 2409, 2411, 2413, 2415, 2417), cada um em célula mesclada.

### Tabela-resumo do rodapé (colunas V:AD, linhas 2404-2422)

| Coluna | Conteúdo |
|---|---|
| `V` | Sigla |
| `W` (mesclada `W:Z`) | Descrição |
| `AA` (mesclada `AA:AB`) | `Qtde. Itens` |
| `AC` (mesclada `AC:AD`) | `Percentual` (fração, formato `%`) |

Linha 2404 = cabeçalho (`Descrição`, `Qtde. Itens`, `Percentual`);
linhas 2405-2421 = uma por sigla (ordem: PND, PRZ, PCI, PC, PCT, PFM, PEE,
PMP, PMT, PRE, PEI, PRI, PFE, SMN, SPC, SDP, SCM);
linha 2422 = total (`64665`, `1`).

> Essa tabela é a **fonte pronta** do quantitativo por sigla — o mesmo número
> pode ser recalculado a partir dos dados, o que serve de validação cruzada.

## Sigla de origem × frente (prefixo do código)

Cruzamento calculado sobre as 64.665 células. **Cada frente usa um subconjunto
próprio de siglas** — informação central para separar as três interfaces:

### `M` — Materiais (1.704 itens · 46.008 células) — 11 siglas

| Sigla | Células | % da frente |
|---|---:|---:|
| `PFM` | 23.816 | 51,76% |
| `PMP` | 4.740 | 10,30% |
| `PCI` | 4.275 | 9,29% |
| `PRE` | 3.948 | 8,58% |
| `PRI` | 2.674 | 5,81% |
| `PC` | 1.889 | 4,11% |
| `PRZ` | 1.836 | 3,99% |
| `PMT` | 1.824 | 3,96% |
| `PCT` | 601 | 1,31% |
| `PEI` | 351 | 0,76% |
| `PFE` | 54 | 0,12% |

`PRZ`, `PMP`, `PMT`, `PRI` e `PFE` ocorrem **exclusivamente** em materiais.

### `E` — Equipamentos (457 itens · 12.339 células) — 7 siglas

| Sigla | Células | % |
|---|---:|---:|
| `PFM` | 5.980 | 48,46% |
| `PRE` | 4.590 | 37,20% |
| `PCI` | 864 | 7,00% |
| `PEE` | 621 | 5,03% |
| `PC` | 191 | 1,55% |
| `PEI` | 54 | 0,44% |
| `PCT` | 39 | 0,32% |

`PEE` ocorre **exclusivamente** no prefixo `E`.

### `A` — Equipamentos/veículos (89 itens · 2.403 células) — 5 siglas

| Sigla | Células | % |
|---|---:|---:|
| `PFM` | 1.716 | 71,41% |
| `PRE` | 513 | 21,35% |
| `PCI` | 108 | 4,49% |
| `PC` | 61 | 2,54% |
| `PCT` | 5 | 0,21% |

### `P` — Mão de Obra (145 itens · 3.915 células) — 3 siglas, todas `S*`

| Sigla | Células | % |
|---|---:|---:|
| `SDP` | 3.285 | 83,91% |
| `SPC` | 627 | 16,02% |
| `SMN` | 3 | 0,08% |

**Regra observada:** as siglas que começam com `S` (salário) aparecem **somente**
em itens de prefixo `P`; as que começam com `P` (preço) **nunca** aparecem em
itens `P`. Ou seja, mão de obra e insumos materiais/equipamentos têm
vocabulários de origem disjuntos.

## Materiais (`M`) — siglas por UF

Contagem de itens de prefixo `M` (1.704 por UF) por sigla de origem. Útil para
os diagnósticos por UF do relatório.

| UF | PC | PCI | PCT | PEI | PFE | PFM | PMP | PMT | PRE | PRI | PRZ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AC | 14 | 157 | 7 | 13 | 2 | 916 | 196 | 79 | 146 | 106 | 68 |
| AM | 28 | 158 | 22 | 13 | 2 | 916 | 194 | 68 | 146 | 89 | 68 |
| AP | 13 | 157 | 5 | 13 | 2 | 916 | 193 | 90 | 147 | 100 | 68 |
| PA | 27 | 158 | 8 | 13 | 2 | 916 | 191 | 80 | 146 | 95 | 68 |
| RO | 25 | 158 | 9 | 13 | 2 | 916 | 190 | 79 | 146 | 98 | 68 |
| RR | 12 | 157 | 6 | 13 | 2 | 916 | 201 | 78 | 147 | 104 | 68 |
| TO | 24 | 157 | 12 | 13 | 2 | 916 | 180 | 86 | 146 | 100 | 68 |
| AL | 26 | 157 | 5 | 13 | 2 | 916 | 198 | 79 | 146 | 94 | 68 |
| BA | 43 | 157 | 23 | 13 | 2 | 908 | 193 | 62 | 146 | 89 | 68 |
| CE | 50 | 157 | 13 | 13 | 2 | 916 | 197 | 52 | 146 | 90 | 68 |
| MA | 12 | 157 | 5 | 13 | 2 | 916 | 220 | 61 | 146 | 104 | 68 |
| PB | 17 | 157 | 10 | 13 | 2 | 916 | 209 | 64 | 146 | 102 | 68 |
| PE | 45 | 157 | 12 | 13 | 2 | 916 | 189 | 62 | 146 | 94 | 68 |
| PI | 22 | 157 | 5 | 13 | 2 | 916 | 214 | 60 | 146 | 101 | 68 |
| RN | 18 | 157 | 6 | 13 | 2 | 915 | 207 | 67 | 146 | 105 | 68 |
| SE | 14 | 158 | 6 | 13 | 2 | 916 | 197 | 78 | 146 | 106 | 68 |
| ES | 34 | 157 | 17 | 13 | 2 | 911 | 187 | 72 | 146 | 97 | 68 |
| MG | 143 | 158 | 63 | 13 | 2 | 885 | 120 | 44 | 145 | 63 | 68 |
| RJ | 393 | 173 | 57 | 13 | 2 | 613 | 9 | 3 | 146 | 227 | 68 |
| SP | 628 | 171 | 172 | 13 | 2 | 431 | 7 | 3 | 146 | 63 | 68 |
| PR | 68 | 157 | 33 | 13 | 2 | 894 | 164 | 77 | 146 | 82 | 68 |
| RS | 42 | 158 | 25 | 13 | 2 | 913 | 176 | 72 | 146 | 89 | 68 |
| SC | 82 | 157 | 33 | 13 | 2 | 859 | 185 | 68 | 147 | 90 | 68 |
| DF | 22 | 157 | 16 | 13 | 2 | 916 | 183 | 86 | 147 | 94 | 68 |
| GO | 46 | 157 | 21 | 13 | 2 | 915 | 184 | 65 | 146 | 87 | 68 |
| MS | 23 | 157 | 6 | 13 | 2 | 916 | 191 | 77 | 148 | 103 | 68 |
| MT | 18 | 157 | 4 | 13 | 2 | 916 | 165 | 112 | 147 | 102 | 68 |

Padrões visíveis: `PRZ` = 68 em **todas** as UFs (os 68 itens zerados);
`PEI` = 13 e `PFE` = 2 constantes; **SP** (628 `PC`) e **RJ** (393 `PC`)
concentram a coleta direta, enquanto as UFs do Norte/Nordeste dependem de
`PFM`/`PMP`/`PRI`.

## Cores das siglas (formatação condicional de `D6:AD2401`)

Como no `II.08.0`, as células **não têm fill estático**; a cor vem de 19 regras
`cellIs equal` — uma por sigla. **Esta é a paleta oficial da entrega** e deve
ser reutilizada em tabelas e gráficos do relatório.

| Sigla | Fundo | Fonte |
|---|---|---|
| `PC` | sem preenchimento (`auto`) | padrão |
| `PFM` | `#E6E6E6` | padrão |
| `PRE` | `#C4C6BE` | padrão |
| `PMT` | `#979797` | padrão |
| `PRI` | `#97B3A6` | padrão |
| `PRZ` | `#4FB4AD` | padrão |
| `PFE` | `#B7E4C7` | padrão |
| `PEI` | `#A8D5FF` | padrão |
| `PEE` | `#74CFFC` | padrão |
| `PCI` | `#FFD6A5` | padrão |
| `PTF` | `#FFF3B0` | padrão |
| `PC¹` | `#D9C2FF` | padrão |
| `SMN` | `#FF7F11` | padrão |
| `PMP` | `#058ED1` | **branca** |
| `PCT` | `#001E68` | **branca** |
| `MDO` | `#003E7E` | **branca** |
| `SPC` | `#006D77` | **branca** |
| `SDP` | `#2F2F2F` | **branca** |
| `SCM` | `#6A994E` | **branca** |

As mesmas 19 regras também se aplicam à faixa `V2405:V2421` (coluna de siglas
da tabela-resumo), o que mantém legenda e dados com cores idênticas.

> Há regras para `PTF`, `PC¹` e `MDO`, siglas que **não ocorrem** nos dados nem
> no glossário desta entrega — são resquícios/reservas de referências
> anteriores. Mantenha as cores no dicionário, mas não crie categorias na
> saída.

## Aba oculta `Tabela RGB utilizada`

Tabela auxiliar 11×26 com **nomenclatura antiga** de tipos de preço, diferente
das siglas em uso na aba `ENTREGA`:

| Sigla | Descrição | Qtde | % | R | G | B | Fonte |
|---|---|---:|---:|---:|---:|---:|---|
| `DMT` | Imputação Metodológica DMT | 31.148 | 51,11% | 230 | 230 | 230 | Preto |
| `EST` | Estimado | 10.611 | 17,41% | 196 | 198 | 190 | Preto |
| `P` | Preço Coletado | 4.023 | 6,60% | – | – | – | Preto |
| `ECT` | Extrapolado Com Tratamento | 3.532 | 5,80% | 151 | 151 | 151 | Preto |
| `E` | Extrapolado | 3.054 | 5,01% | 5 | 142 | 209 | Branco |
| `I` | Imputado | 3.014 | 4,95% | 151 | 179 | 166 | Preto |
| `MDO` | Imputação Metodológica MDO | 2.970 | 4,87% | 0 | 62 | 126 | Branco |
| `Z` | Zerado | 1.863 | 3,06% | 79 | 180 | 173 | Preto |
| `PCT` | Pesquisado Com Tratamento | 724 | 1,19% | 0 | 30 | 104 | Branco |
| `PPE` | Precificado por Estudo | 3.024 | 4,96% | 116 | 207 | 252 | Preto |

Observações:

- Os quantitativos **não** correspondem à referência de julho/2026 (soma
  63.963 ≠ 64.665) — é uma tabela **herdada** de referência anterior.
- Há também um bloco de correspondência solto nas colunas `L:Y`, linhas 6-7,
  relacionando a nomenclatura antiga (`EST`, `ECT`, `MDO`, `PCT`, `P`, `E`,
  `DMT`, `I`, `PPE`, `Z`).
- **Não use esta aba como fonte de dados.** Serve apenas como histórico da
  paleta RGB. A paleta vigente é a da formatação condicional da aba `ENTREGA`.

## Receita de leitura (validada)

```python
import pandas as pd

ORI = "DNIT_II.09.0_2ºOrigem-Precos-SICRO-Ref-Jul.2026.xlsx"

org = pd.read_excel(ORI, sheet_name="ENTREGA", skiprows=4)             # -> (2418, 30)
org = org[org["CÓDIGO"].astype(str).str.match(r"^[AEMP]\d+$")]          # -> (2395, 30)
org = org.rename(columns={"DESCRIÇÃO DO ITEM": "DESCRIÇÃO",
                          "UNIDADE DO ITEM": "UNIDADE"})
```

- `skiprows=4` (cabeçalho na linha 5) — **diferente** do `II.08.0`, que usa
  `skiprows=3`.
- O filtro por regex descarta as linhas vazias e todo o bloco de legenda, que
  entraria como parágrafos longos na coluna `CÓDIGO`.

### Cruzamento preço × origem

```python
UFS = ["AC","AM","AP","PA","RO","RR","TO",
       "AL","BA","CE","MA","PB","PE","PI","RN","SE",
       "ES","MG","RJ","SP","PR","RS","SC","DF","GO","MS","MT"]

p = preco.melt(id_vars=["CÓDIGO"], value_vars=UFS, var_name="UF", value_name="PRECO")
o = org.melt(id_vars=["CÓDIGO"],  value_vars=UFS, var_name="UF", value_name="ORIGEM")
base = p.merge(o, on=["CÓDIGO", "UF"])   # 64.665 linhas
```

Consistência esperada: `ORIGEM == "PRZ"` ⟺ `PRECO == 0` (1.836 células em ambos
os lados).

## Armadilhas conhecidas

1. **Cabeçalho na linha 5** (`skiprows=4`), ao contrário do `II.08.0`
   (`skiprows=3`). Errar isso desloca tudo silenciosamente.
2. Nomes de coluna **diferentes** do arquivo de preços: `DESCRIÇÃO DO ITEM`,
   `UNIDADE DO ITEM`.
3. O **bloco de legenda do rodapé** (linhas 2403+) contém parágrafos enormes e
   células mescladas; sem filtro, viram linhas de dados.
4. A aba `Tabela RGB utilizada` está **oculta** — `pd.read_excel(..., sheet_name=None)`
   a traz junto e com nomenclatura incompatível.
5. As **cores não estão nas células**: só existem como formatação condicional.
   Para reproduzir o visual, use o dicionário de cores acima.
6. Siglas `PTF`, `PC¹`, `MDO`, `PND`, `SCM` existem em regras/legenda mas têm
   **zero ocorrências** nos dados desta referência.
7. Valores são **texto** (`str`), não categorias — normalize com `.strip()`
   antes de comparar.
