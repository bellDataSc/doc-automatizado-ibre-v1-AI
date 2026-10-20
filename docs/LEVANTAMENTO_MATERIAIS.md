# Levantamento de entradas — Relatório de MATERIAIS (Tomo 1)

Resultado da execução do plano `levantamento-funcional-materiais`. Todas as
afirmações abaixo foram conferidas lendo os arquivos da pasta de rede
`Y:\A02_REFERENCIAS\01_DNIT\01_SICRO\` contra o PDF do 2º RR de julho/2026.

## 1. Mapa de fontes localizadas

Caminho base: `Y:\A02_REFERENCIAS\01_DNIT\01_SICRO\{AAAA.MM}\`

| Necessidade do relatório | Arquivo | Local | Status |
|---|---|---|---|
| Preço atual por UF | `DNIT_II.08.0_*Resultado-Final*` | `04_ENTREGA\<pasta da entrega>` | confirmado |
| Origem do preço | `DNIT_II.09.0_*Origem-Precos*` | idem | confirmado |
| Líder / liderado | `DNIT_II.11.0_*Relacao-Lider-Liderado*` | idem | confirmado (295 liderados = T14) |
| Descrições e fator de conversão | `DNIT_II.10.0_*Descricoes-Fatores*` | idem | uso não evidente no texto — pendente |
| **Histórico de preços** | `II.08.0` de cada referência | `{ref}\04_ENTREGA\` (existe de 2021.10 a 2026.07) | confirmado |
| **Ampla / restrita, família, classificação** | `SICROBR_Lista_Insumos_*_PROD.xlsx`, aba `LISTA_INSUMOS` | `{ref}\01_LISTA-INSUMOS\` | confirmado (ver §3) |
| Composição de itens compostos | mesma lista, aba `LISTA_COMPOSTOS` | idem | disponível |
| Variações em CCU (2.2.3, 3.2.2) | `DNIT_II.01.4_*Variacao-CCUs*` | `04_ENTREGA` ou `02_MEMORIAS-CALCULO\03_MAT\` | confirmado |
| Matriz de variação **dos relevantes com justificativa** | `II.01.4`, aba `Relação_Mat_Item63.1` (48 itens, todos com justificativa) | idem | confirmado |
| Matriz de variação geral com justificativa | `II.01.4`, aba `Tabela_Variações_Insumo` (230 `M`) | idem | confirmado |
| Varejo (§4) | `DNIT_II.01.5_*Resultado-Varejo*` (preço varejo x 27 UFs) | idem | confirmado |
| Tratamentos, imputações, descartes da referência | `SICRO_*_TRATAMENTOS-REALIZADOS.csv`, `*_IMPUTACAO-DE-PRECO.csv`, `*_DESCARTE-PRECO*.csv`, `*_APROVAR-PAINEL.csv` | `02_MEMORIAS-CALCULO\03_MAT\01_CARGA-SFPC\` | disponível; uso a validar |
| Painel de preços | `DNIT-SICRO_*_PAINEL-PRECO-FECHAMENTO_*.xlsx` (88.766 x 91) | `03_PAINEL-PRECOS\03_FECHAMENTO\` | candidato a "BP" — pendente |
| Parâmetros de frete (T1–T8) | — | não localizado | **pendente: enviar** |
| Cotações DNIT (§5, T28–T36) | — | não localizado | **pendente: enviar** |
| Esforço de pesquisa (§6) | — | não localizado | **pendente: enviar** |

### Versões de uma mesma referência

Cada referência tem mais de uma entrega: 1ª (`II.08.0_`), retificação
(`II.08.0_2º`) e valoração (`*_VALORACAO`, às vezes `3º`). **O relatório de
julho compara com o abril retificado (2º)**: na T13, a faixa −50%/−20% dá 3
com o abril 2º e 6 com o abril 1º; o PDF publica 3.

Regra proposta (validar): histórico = última versão de retificação de cada
referência, excluindo pastas de valoração e `00_HISTORICO`.

## 2. Tabelas de controle reproduzidas (julho/2026 x abril/2026 2º)

| Tabela | PDF | Reproduzido | Diferença |
|---|---|---|---|
| T14 liderados — itens | 295 | 291 | 4 itens sem preço comparável em abril |
| T14 — faixas | 0·1·146·805·2353·304·2867·1154·308·27·0·0 | 0·1·146·802·2349·277·2830·1120·305·27·0·0 | proporcional aos 4 itens |
| T13 líderes ampla — itens | 112 | 110 | 2 itens |
| T13 — faixas | 0·3·192·294·582·501·838·440·170·4·0·0 | 0·3·192·321·581·501·800·405·167·0·0·0 | faixas centrais deslocadas |
| T17 amplitudes — itens | 407 | 398 | 9 itens (classificação ampla, ver §3) |
| T17 — faixas | 175·68·129·35 | 174·64·125·35 | faixa >100% exata |
| T19/T20 — frete metodológico | 916 | 916 | exato |
| T20 — índice / extrap. / imputado | 156 / 13 / 15 | 156 / 13 / 15 | exato |
| 2.1.1 — zerados | 68 | 68 | exato |

Conclusão: método (variação = atual/anterior − 1; faixas; amplitude =
(máx − mín)/mín sobre 27 UFs; filtros por liderança e comercialização) está
correto. As diferenças vêm da definição exata dos universos.

## 3. Classificação ampla x restrita

Fonte: `LISTA_INSUMOS.comercialização` (todos os 1.704 `M` publicados estão na
lista, `status = Produção`).

| Lista de Insumos | Itens | Relatório |
|---|---|---|
| Ampla | 398 | 475 ampla (= 407 com preço + 68 sem) |
| Sem precificação | 68 | (incluídos nos 475) |
| Taxa | 2 | ? |
| Restrita | 1.236 | 1.229 |

398 + 68 + 2 = 468 → faltam 7 para 475; e há 7 a mais em Restrita. Os 7
restritos que não se encaixam em nenhuma metodologia da T20 são os candidatos
a terem sido tratados como ampla no relatório. **Pendente:** confirmar se a
lista correta é a `V05_PROD` ou outra versão, ou se há reclassificação manual.

## 4. Onde o "BP" se encaixa

O histórico de preços publicado já existe nos `II.08.0` de cada referência.
O BP só é necessário se trouxer algo que eles não têm. Candidatos:

- preços coletados por respondente (para STJ/CV da §5 ou para explicar
  variações);
- origem detalhada do preço por referência anterior (se o `II.09.0` antigo
  não bastar);
- painel de fechamento (`03_PAINEL-PRECOS`), se for esse o "BP".

**Pendente:** confirmar o que é o BP e qual arquivo o representa.

## 5. Entradas por referência (proposta para a interface de Materiais)

| # | Entrada | Obrigatória | Partes que alimenta |
|---|---|---|---|
| 1 | `II.08.0` atual | sim | quase todas |
| 2 | `II.09.0` atual | sim | 2.1.1, 3.1, justificativas, T33 |
| 3 | `II.11.0` atual | sim | T13, T14, T16, T25 |
| 4 | `II.08.0` das 10 referências anteriores | sim | variações, G1–50, T26 |
| 5 | Lista de Insumos `_PROD` | sim | ampla/restrita, família, classificação |
| 6 | `II.01.4` | sim | T9/T11/T12 (relevantes e justificativas), T15/T16, T24/T25, 2.2.3 |
| 7 | `II.01.5` | para §4 | G63, T27 |
| 8 | `II.10.0` | a validar | descrição/unidade |
| 9 | Parâmetros de frete | para 2.1.2–2.1.4 | T1–T8 — **a enviar** |
| 10 | Cotações DNIT | para §5 | T28–T36 — **a enviar** |
| 11 | Esforço de pesquisa | para §6 | — **a enviar ou digitar** |

Item 4 pode ser lido direto da pasta de rede, sem upload, se o app tiver
acesso a `Y:`.

## 6. Decisões registradas

- **Versão-base:** mantido o template do **1º RR** (`materiais/template/`).
- **BP (Banco de Preços FGV IBRE):** fonte de **ficha técnica dos insumos**, não
  de histórico de preços. O histórico vem dos `II.08.0` de cada referência.
- **Textos:** a usuária enviará um Word com o relatório inteiramente mapeado
  (o que muda e o que fica por referência), **com comentários que devem ser
  lidos**. Diretriz: o que muda é pouco; automatizar onde possível e, nos
  demais casos, oferecer caixa de texto na tela para a justificativa antes de
  baixar o relatório.
- **Frete:** tem planilha e bancos próprios; a metodologia será enviada para
  gerar o cálculo em código. Cotações e esforço de pesquisa: a enviar.

## 7. Pendências de validação (atualizadas)

1. Versão-base: há `DNIT_II.01.1_2ºRR_*.docx` em `02_MEMORIAS-CALCULO\03_MAT\02_SEGUNDA-ENTREGA`. O template atual foi gerado do 1º RR; recomenda-se regenerar do 2º.
2. Regra de versão do histórico (retificação x valoração).
3. Diferença de 7 itens ampla/restrita e de 2–4 itens nos universos T13/T14.
4. Uso do `II.10.0`.
5. Agregação "por região" nos gráficos de evolução.
6. Identificação da UFF.
7. Conversão varejo → atacado (margem PAC).
8. Seleção dos itens G51–55 e das famílias G56–62.
9. Definição do BP.
10. Textos: rascunho automático x redação do analista.
11. Fontes de frete, cotações e esforço de pesquisa.
