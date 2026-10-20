# Automatizador de Relatórios - DNIT - SICRO

Aplicação Streamlit para geração automatizada dos relatórios do contrato
DNIT - SICRO (FGV IBRE), organizada em três frentes independentes:

- Materiais
- Equipamentos
- Mão de Obra

O fluxo de entrada é baseado em planilhas (.xlsx).

## Estado atual

**Materiais** tem o fluxo completo da referência que está sendo processada:

1. **Planilhas** — envio do par II.08.0 + II.09.0, leitura, cruzamento e
   conferência do que foi lido.
2. **Gráficos** — botão `Gerar gráficos`; os gráficos aparecem na tela,
   separados por família, para conferência visual.
3. **Relatório** — só depois da conferência, `Gerar relatório em Word`
   preenche o template da entrega e libera o download.

Nesta versão os gráficos usam **somente a referência processada**. A base
histórica ainda não está ligada: o eixo do tempo da evolução sai com um
único ponto e a coluna `Var.%` fica vazia.

**Equipamentos** e **Mão de Obra** continuam como a casca original.

### O que ainda não sai das duas planilhas

- 13 gráficos de ordenamento por família: falta a composição da família e a
  relação líder/liderado. Na tela o analista pode informar a família; assim
  que o dado tiver uma origem, o painel deixa de ser manual.
- 1 gráfico de comparação atacado × varejo: depende da base do varejo.
- As 33 tabelas do relatório: dependem da referência anterior, da
  classificação ampla/restrita, dos relevantes, do frete, das CCUs, das
  cotações do DNIT e do varejo. O template as mantém como estão.

## Execução

```bash
pip install -r requirements.txt
streamlit run dnit_sicro_st.py
```

## Compatibilidade com Streamlit in Snowflake

As dependências são `streamlit`, `pandas`, `openpyxl`, `matplotlib` e
`python-docx`. Não há `docxtpl`, `geopandas` nem `shapely`: o template é
preenchido com `python-docx` e o mapa do Brasil é desenhado com polígonos
de `dados/uf_brasil.json`.

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
materiais_writer.py      # preenche o template Word com os gráficos conferidos

equipamentos_st.py       # interface da frente Equipamentos
mao_obra_st.py           # interface da frente Mão de Obra

template/                # TEMPLATE_DNIT_Tomo-1_Materiais-SICRO.docx
dados/uf_brasil.json     # contorno das 27 UFs, para o mapa de amplitude
docs/                    # fixtures sintéticos e verificações
```
