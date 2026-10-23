# Automatizador de Relatórios - DNIT - SICRO

Aplicação Streamlit para geração automatizada dos relatórios do contrato
DNIT - SICRO (FGV IBRE), organizada em três frentes independentes:

- Materiais
- Equipamentos
- Mão de Obra

O fluxo de entrada é baseado em planilhas (.xlsx).

## Estado atual (23/10/2026)

**Materiais** é a única frente em desenvolvimento. Fluxo da tela:

0. **Referência** — ano/mês da referência atual (a anterior é deduzida),
   ordinal, nº do relatório, protocolo e mês de emissão. Origem dos dados:
   planilhas enviadas ou base histórica no Snowflake (quando configurada).
1. **Dados da referência** — leitura, cruzamento e conferência do que foi lido.
2. **Gráficos** — botão `Gerar gráficos`; conferência visual por família.
3. **Tabelas** — situação de cada uma das 36 tabelas e o conteúdo lido de
   duas fontes, lado a lado: as views `SICRO_HIST_VW_*` da base (tabelas 9 a
   26, exceto a 18) e, opcionalmente, as abas "Tabela ..." da planilha das
   tabelas do RR (.xlsm), como o analista as deixou. O app não refaz os
   cálculos: lê o que a base e a planilha já calcularam. As tabelas 12, 16 e
   25 têm uma grade de **justificativas** editável, pré-preenchida com o texto
   do template para o mesmo código. Botão para baixar as tabelas da base em
   Excel. As tabelas lidas da base são escritas no Word
   (`materiais_tabelas.py` monta, `materiais_writer.preencher_tabelas`
   escreve), mantendo a formatação das linhas do template; partes "(2/2)"
   crescem, encolhem ou somem conforme o número de linhas.
4. **Textos do relatório** — um bloco por texto que muda a cada referência
   (72 blocos), pré-preenchido com o texto da referência anterior. O analista
   decide bloco a bloco: `Usar texto anterior / OK` ou edita e salva. Nada é
   gerado automaticamente.
5. **Relatório em Word** — preenche marcadores (capa, rodapés e datas no
   texto), escreve os textos decididos e insere os gráficos sob as legendas.

Os gráficos de evolução usam as referências anteriores da base (até 10,
hoje 7: 2025-01 a 2026-07) quando o Snowflake está disponível; a referência
atual vem da origem escolhida. A Var.% da legenda é preço atual ÷ anterior − 1.

**⚙️ Administração** (área separada na barra lateral), duas cargas, cada uma
uma vez por referência, sem sobrescrever:

1. Preços e origens: II.08, II.09 e II.11 vão para a pasta `AAAA-MM/` do
   stage `SICRO_HIST_STG_ENTREGAS` e a procedure
   `SICRO_HIST_SP_CARREGAR_REFERENCIA` grava (ela recusa referência repetida).
2. Cadastro: a aba "Gerenciamento Atual" da planilha das tabelas do RR
   (enviada ou lida do stage) vai para `SICRO_HIST_CADASTRO`.

**Equipamentos** e **Mão de Obra** continuam como a casca original.

### Template e textos

O template `template/TEMPLATE_DNIT_Tomo-1_Materiais-SICRO.docx` é gerado por
`gerar_template_docx.py` a partir do Word revisado da referência anterior
(grifo amarelo = muda; rosa = fixo; comentários = instruções):

```bash
python gerar_template_docx.py --origem "DNIT_..._REVISÃO.docx" --referencia 2026-07 --anterior 2026-04
```

Ele mantém todo o texto fixo, remove grifos, comentários e imagens, troca datas
e nomes de arquivo por marcadores `{{...}}`, marca cada bloco editável com um
bookmark `TXT_<id>` e grava o catálogo `materiais/textos/blocos_<ref>.json`
com o texto de cada bloco. A cada referência publicada, roda-se o script de
novo sobre o Word revisado daquela referência.

### O que ainda não sai das planilhas

- Tabelas 1 a 8 (frete/DMT), 18 (sem view) e 27 a 36 (varejo e cotações):
  fora da base, saem com os valores do template.
- Cor de fundo das células das tabelas 11, 15, 23 e 24 (vermelho/azul no
  template, sem regra consistente): o app escreve sem fundo até a regra ser
  definida.
- 13 gráficos de ordenamento por família: a família é informada na tela até
  a composição ter uma origem (planilha GERENCIAMENTO ou base).
- 7 datas dentro de blocos editáveis ficaram como texto (run com formatação
  diferente); o analista ajusta na edição do bloco.

## Execução

```bash
pip install -r requirements.txt
streamlit run dnit_sicro_st.py
```

## Compatibilidade com Streamlit in Snowflake

As dependências são `streamlit`, `pandas`, `openpyxl`, `matplotlib` e
`python-docx`. Não há `docxtpl`, `geopandas` nem `shapely`: o template é
preenchido com `python-docx` e o mapa do Brasil é desenhado com polígonos
de `dados/uf_brasil.json`. A sessão Snowflake vem de `get_active_session()`
no SiS; localmente, de `.streamlit/secrets.toml` (`[connections.snowflake]`,
modelo em `.streamlit/secrets.toml.exemplo`) ou da conexão nomeada em
`~/.snowflake/connections.toml`. Sem nenhuma das três, a tela mostra o motivo.

## Snowflake

Objetos em `BASES_SAPR.AGENTE_SAPR`, prefixo `SICRO_HIST_` (configurados em
`dnit_sicro_config.SNOWFLAKE`): `PRECO_UF`, `CONTROLE_REFERENCIA`,
`LIDERANCA`, `CADASTRO`, `LISTA_RELEVANTE`, o stage `STG_ENTREGAS`, a
procedure `SP_CARREGAR_REFERENCIA` e as views `VW_SERIE_HIST`,
`VW_AMPLITUDE`, `VW_VARIACAO`, `VW_TAB_FAIXAS`, `VW_TAB_T19_T20`,
`VW_TAB_VARIACAO_ITEM`, `VW_TAB_VAR_RESUMO`. A correspondência entre as
tabelas do template e as da planilha/views está em
`materiais_config.TABELAS_RR`.

Quando uma view junta várias tabelas, o app separa as linhas pela coluna
`TABELA` (ou `COD_TABELA`, `ID_TABELA`...). Se a view não tiver essa coluna, a
tela mostra a view inteira e avisa. A tela tem um painel "Estrutura das
views" com as colunas reais de cada uma.

### Planilha das tabelas do RR (.xlsm pesado)

Aberta com `openpyxl` em modo somente leitura e com os valores calculados
pelo Excel (`read_only=True, data_only=True`): não recalcula fórmula, não roda
VBA e lê só as abas necessárias. Localmente o limite de upload foi para 400 MB
(`.streamlit/config.toml`). No Streamlit in Snowflake o limite de upload é
do próprio SiS e o `config.toml` não vale para ele: se o arquivo passar do
limite, ponha-o no stage e use a opção "Ler do stage do Snowflake".

## Estrutura

```
dnit_sicro_st.py         # aplicação e roteamento entre as frentes
dnit_sicro_config.py     # identificação do contrato, identidade visual, frentes
dnit_sicro_utils.py      # componentes compartilhados de interface
.streamlit/config.toml   # cores FGV IBRE

materiais_st.py          # tela de Materiais: planilhas, gráficos, relatório
materiais_config.py      # constantes extraídas dos arquivos da frente
materiais_readers.py     # leitura, validação e cruzamento das duas planilhas
materiais_catalogo.py    # catálogo dos 63 gráficos, lido do template
materiais_charts.py      # amplitude, evolução e ordenamento
materiais_writer.py      # preenche marcadores, textos, tabelas e gráficos no template Word
materiais_tabelas.py     # monta cada tabela do relatório a partir das views (sem recalcular)
materiais_planilha_rr.py # leitura somente leitura da planilha das tabelas do RR (.xlsm)
dnit_sicro_snowflake.py  # base histórica: preços, histórico, views das tabelas e carga controlada
admin_carga_st.py        # área de Administração: carga de referência nova
gerar_template_docx.py   # gera o template e o catálogo de textos do Word revisado
materiais/textos/        # blocos_<ref>.json: texto de cada bloco editável

equipamentos_st.py       # interface da frente Equipamentos
mao_obra_st.py           # interface da frente Mão de Obra

template/                # TEMPLATE_DNIT_Tomo-1_Materiais-SICRO.docx (gerado)
docs/PROMPT_CORTEX_CARGA.md  # prompt para criar a base histórica no Snowflake
dados/uf_brasil.json     # contorno das 27 UFs, para o mapa de amplitude
docs/                    # fixtures sintéticos e verificações
                         # (testar_snowflake.py: base simulada em SQLite)
```
