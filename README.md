# Automatizador de Relatórios - DNIT - SICRO

Aplicação Streamlit para geração automatizada dos relatórios do contrato
DNIT - SICRO (FGV IBRE), organizada em três frentes independentes:

- Materiais
- Equipamentos
- Mão de Obra

O fluxo de entrada é baseado em planilhas (.xlsx).

## Estado atual (20/10/2026)

**Materiais** é a única frente em desenvolvimento. Fluxo da tela:

0. **Referência** — ano/mês da referência atual (a anterior é deduzida),
   ordinal, nº do relatório, protocolo e mês de emissão. Origem dos dados:
   planilhas enviadas ou base histórica no Snowflake (quando configurada).
1. **Dados da referência** — leitura, cruzamento e conferência do que foi lido.
2. **Gráficos** — botão `Gerar gráficos`; conferência visual por família.
3. **Tabelas** — situação de cada uma das 36 tabelas. Nenhuma é calculada
   ainda: saem no Word com os valores do template (jul/2026) até a planilha
   das tabelas ser mapeada aba a aba.
4. **Textos do relatório** — um bloco por texto que muda a cada referência
   (72 blocos), pré-preenchido com o texto da referência anterior. O analista
   decide bloco a bloco: `Usar texto anterior / OK` ou edita e salva. Nada é
   gerado automaticamente.
5. **Relatório em Word** — preenche marcadores (capa, rodapés e datas no
   texto), escreve os textos decididos e insere os gráficos sob as legendas.

**⚙️ Administração** (área separada na barra lateral) — carga de uma
referência nova no Snowflake. Verifica se a referência já existe e bloqueia a
carga; nunca sobrescreve. Fica inativa até os nomes de schema/tabelas serem
preenchidos em `dnit_sicro_config.SNOWFLAKE`.

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

- As 36 tabelas: dependem da planilha das tabelas (mapeamento pendente).
- Gráficos de evolução com histórico (hoje só 1 ponto) e tabela 26: dependem
  da base histórica no Snowflake.
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
no SiS; localmente, da conexão nomeada em `connections.toml`.

## Snowflake

A estrutura (schema, tabelas, chaves) é criada pelo Cortex Code com o prompt
em `docs/PROMPT_CORTEX_CARGA.md`. Os nomes que ele devolver vão para
`dnit_sicro_config.SNOWFLAKE`; só então a origem "Base histórica" e a área de
Administração passam a funcionar.

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
materiais_writer.py      # preenche marcadores, textos e gráficos no template Word
dnit_sicro_snowflake.py  # leitura da base histórica e carga controlada (sem sobrescrever)
admin_carga_st.py        # área de Administração: carga de referência nova
gerar_template_docx.py   # gera o template e o catálogo de textos do Word revisado
materiais/textos/        # blocos_<ref>.json: texto de cada bloco editável

equipamentos_st.py       # interface da frente Equipamentos
mao_obra_st.py           # interface da frente Mão de Obra

template/                # TEMPLATE_DNIT_Tomo-1_Materiais-SICRO.docx (gerado)
docs/PROMPT_CORTEX_CARGA.md  # prompt para criar a base histórica no Snowflake
dados/uf_brasil.json     # contorno das 27 UFs, para o mapa de amplitude
docs/                    # fixtures sintéticos e verificações
```
