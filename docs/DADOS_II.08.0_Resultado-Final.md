# DNIT_II.08.0 — Resultado Final SICRO (Ref. Jul/2026)

Documentação técnica do arquivo de entrada de **preços referenciais**.
Gerada por inspeção direta do arquivo (openpyxl + pandas), sem inferências
sobre regras não observáveis nos dados.

- **Nome do arquivo:** `DNIT_II.08.0_2ºResultado-Final-SICRO-Ref-Jul.2026.xlsx`
- **Tamanho:** ~0,63 MB
- **Papel no processo:** contém o **valor** do preço referencial de cada insumo
  em cada UF. É o arquivo citado no relatório como
  `DNIT_II.08.0_2ºResultado-Final-SICRO-Ref-Jul.2026`.
- **Par obrigatório:** `DNIT_II.09.0_2ºOrigem-Precos-SICRO-Ref-Jul.2026.xlsx`
  (mesma lista de 2.395 códigos, mesma ordem de UFs; ver doc própria).

## Convenção do nome do arquivo

`DNIT_II.<seq>.<sub>_<n>º<Conteúdo>-SICRO-Ref-<Mês>.<Ano>.xlsx`

| Parte | Valor neste arquivo | Significado observado |
|---|---|---|
| `DNIT_II` | `DNIT_II` | Contrato DNIT, **Objetivo II** (Pesquisa Nacional de Preços de Insumos) |
| `08.0` | `08.0` | Identificador do produto/entrega dentro do objetivo |
| `2º` | `2º` | 2ª entrega/relatório da referência |
| conteúdo | `Resultado-Final-SICRO` | Resultado final da pesquisa |
| referência | `Ref-Jul.2026` | Mês/ano de referência dos preços |

## Estrutura da pasta de trabalho

- Planilhas: **1** — `Resultado Final` (visível). Não há abas ocultas.
- Painel congelado: `D5` (trava cabeçalho + 3 primeiras colunas).
- Dimensões declaradas: `A1:AD2402` → 30 colunas, 2.402 linhas.
- Células mescladas: `A1:B3`, `C1:AC1`, `C2:AC2`, `C3:AC3`, `A2401:A2402`.

### Mapa de linhas

| Linha | Conteúdo |
|---|---|
| 1 | `A1:B3` mesclado (logo/marca, sem texto); `C1:AC1` vazio |
| 2 | `C2` = `SICRO` · `AD2` = `DNIT` |
| 3 | `C3` = `Resultado Final - Pesquisa Nacional de Preços - Ref.Julho de 2026` |
| **4** | **Cabeçalho das colunas** |
| **5 … 2399** | **Dados — 2.395 insumos, 1 por linha** |
| 2400 | vazia |
| 2401 | `A2401` = `Legenda` · `B2401` = `Preços zerados` (célula pintada de cinza) |
| 2402 | `B2402` = `Preços sem necessidade de precificação` (célula pintada de verde `#92D050`) |

## Colunas (30)

| Col | Cabeçalho (linha 4) | Tipo | Observações |
|---|---|---|---|
| A | `CÓDIGO` | texto | Código SICRO do insumo. Único (0 duplicatas). Formato `^[AEMP]\d{4}$` |
| B | `DESCRIÇÃO` | texto | Descrição completa do insumo. Formato de célula `@` (texto) |
| C | `UNIDADE` | texto | Unidade de medida |
| D … AD | 27 siglas de UF | numérico | Preço referencial em R$. `number_format = 0.00`, mas o valor armazenado tem até 4 decimais |

### Ordem exata das 27 colunas de UF (D → AD)

```
AC, AM, AP, PA, RO, RR, TO,          # Norte (7)
AL, BA, CE, MA, PB, PE, PI, RN, SE,  # Nordeste (9)
ES, MG, RJ, SP,                      # Sudeste (4)
PR, RS, SC,                          # Sul (3)
DF, GO, MS, MT                       # Centro-Oeste (4)
```

A ordem **não é alfabética global**: é alfabética *dentro* de cada região, e as
regiões aparecem nessa sequência. A mesma ordem é usada no arquivo de Origem de
Preços. Preserve-a ao gerar tabelas e gráficos.

## Conteúdo dos dados

- **2.395 insumos** (linhas 5 a 2399), **27 UFs** → **64.665 células de preço**.
- Nenhum código duplicado; nenhuma célula de preço vazia.

### Prefixo do código = frente do relatório

O primeiro caractere do código separa as três frentes do contrato:

| Prefixo | Itens | Unidades | Exemplos | Frente |
|---|---|---|---|---|
| `M` | **1.704** | un (814), m (581), kg (107), m² (70), m³ (47), l (40), t (33), par (4), `Kg` (3), cj (3), kwh (1), dm³ (1) | `M0003 Aço CA 25` · `M0004 Aço CA 50` · `M0191 Brita 1` | **Materiais** |
| `E` | **457** | un (457) | `E9001 Conjunto vibratório para tubos de concreto…` · `E9007 Bomba de pistão triplex…` | **Equipamentos** |
| `A` | **89** | un (89) | `A9293 Caminhão plataforma 6 x 2, PBT 23.000 kg…` · `A9296 Carroceria de madeira…` | **Equipamentos** (veículos / aquisição) |
| `P` | **145** | h (90), mês (54), un (1) | `P9801 Ajudante` · `P9803 Almoxarife - mensalista` · `P9982 Vigia` | **Mão de Obra** |

Soma: 1.704 + 457 + 89 + 145 = **2.395**. ✔

> O relatório PDF desta entrega (`Tomo 1 – Materiais SICRO`) trata **apenas do
> prefixo `M`**. Os prefixos `A`/`E` e `P` são objeto de outros tomos, o que é
> consistente com a separação em três frentes na aplicação.

### Preços zerados

- **68 insumos têm 0,00 em todas as 27 UFs** — todos de prefixo `M`.
- **Nenhum insumo tem zeros parciais** (é tudo-ou-nada por linha).
- Isso casa com o relatório (seção 2.1.1): "constam 68 insumos com preços
  zerados em todas as UFs". No arquivo de Origem esses itens aparecem como
  `PRZ` (68 × 27 = **1.836** células `PRZ`). ✔
- Primeiros códigos zerados: `M0104`, `M0451`, `M0452`, `M0453`, `M0454`,
  `M0614`, `M0785`, `M1129`, `M1556`, `M1943`, `M1944`, `M1945`, `M1946`,
  `M1947`, `M1949`, `M1950`, `M1952`, `M1955`, `M1956`, `M1958`, …

## Cores / destaques (formatação condicional)

As células de dados **não têm preenchimento estático** (`fill = None`). O
destaque visual é feito por **formatação condicional** sobre `D5:AD2399`:

| Regra | Condição | Preenchimento | Significado (legenda linhas 2401-2402) |
|---|---|---|---|
| `expression` | `$A5="M3504"` | verde `#92D050` | "Preços sem necessidade de precificação" |
| `cellIs equal` | `= 0` | cinza (tema 0, tint −0,25 ≈ `#BFBFBF`) | "Preços zerados" |

Consequências práticas:

1. Ler o arquivo com pandas/openpyxl **não traz as cores** — elas precisam ser
   reconstruídas por regra (`valor == 0` → cinza; `código == "M3504"` → verde).
2. O item **`M3504`** é tratado como caso único "sem necessidade de
   precificação" nesta referência.

## Receita de leitura (validada)

```python
import pandas as pd

RES = "DNIT_II.08.0_2ºResultado-Final-SICRO-Ref-Jul.2026.xlsx"

df = pd.read_excel(RES, sheet_name="Resultado Final", skiprows=3)   # -> (2398, 30)
df = df[df["CÓDIGO"].astype(str).str.match(r"^[AEMP]\d+$")]          # -> (2395, 30)
```

- `skiprows=3` põe a linha 4 como cabeçalho.
- O filtro por regex remove a linha vazia (2400) e as duas linhas de legenda
  (2401-2402), que entram como `CÓDIGO = NaN` / `"Legenda"`.
- Colunas de UF já vêm como `float64`.

### Formato longo (recomendado para gráficos e cruzamentos)

```python
UFS = ["AC","AM","AP","PA","RO","RR","TO",
       "AL","BA","CE","MA","PB","PE","PI","RN","SE",
       "ES","MG","RJ","SP","PR","RS","SC","DF","GO","MS","MT"]

longo = df.melt(id_vars=["CÓDIGO", "DESCRIÇÃO", "UNIDADE"],
                value_vars=UFS, var_name="UF", value_name="PRECO")
# -> 64.665 linhas

longo["FRENTE"] = longo["CÓDIGO"].str[0].map(
    {"M": "materiais", "E": "equipamentos", "A": "equipamentos", "P": "mao_obra"}
)
```

## Armadilhas conhecidas

1. **Cabeçalho na linha 4**, não na 1. `skiprows=3` é obrigatório.
2. **Duas linhas de legenda no fim** precisam ser descartadas, senão viram
   "insumos" fantasmas.
3. **Acentos nos nomes de coluna**: `CÓDIGO`, `DESCRIÇÃO`. No arquivo de Origem
   os nomes são diferentes (`DESCRIÇÃO DO ITEM`, `UNIDADE DO ITEM`) — não
   assuma nomes iguais entre os dois arquivos.
4. **`Kg` vs `kg`**: 3 itens usam `Kg` com K maiúsculo. Normalize antes de
   agrupar por unidade.
5. **Precisão**: exibido com 2 decimais (`0.00`), armazenado com até 4
   (ex. `663140.1643`). Use o valor armazenado nos cálculos e arredonde só na
   apresentação.
6. `0` é **valor de negócio** ("preço zerado"), não dado faltante. Não troque
   por `NaN` sem intenção.
7. As cores citadas no relatório **não existem como fill** no arquivo; são
   formatação condicional (ver seção acima).

## Cruzamento com a Origem de Preços

Os dois arquivos são alinhados 1:1 pelo `CÓDIGO` (validado: 2.395 → 2.395, sem
sobras em nenhum dos lados):

```python
base = preco.merge(origem, on="CÓDIGO", suffixes=("_preco", "_origem"))  # (2395, 59)
```

Cada par (insumo, UF) passa então a ter **valor** (deste arquivo) + **origem
metodológica do preço** (do arquivo `II.09.0`), que é a base de praticamente
todos os diagnósticos do relatório.
