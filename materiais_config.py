"""Constantes da frente Materiais - DNIT - SICRO.

Tudo aqui foi extraido por inspecao direta dos arquivos de entrada e do
relatorio da referencia julho/2026. Nada foi inferido: o que nao estava nos
arquivos nao esta aqui.
"""

# ──────────────────────────────────────────────────────────────
# ARQUIVOS DE ENTRADA
# ──────────────────────────────────────────────────────────────
# DNIT_II.08.0_<n>ºResultado-Final-SICRO-Ref-<Mes>.<Ano>.xlsx
RESULTADO_FINAL = {
    "aba": "Resultado Final",
    "skiprows": 3,          # cabecalho na linha 4
    "col_codigo": "CÓDIGO",
    "col_descricao": "DESCRIÇÃO",
    "col_unidade": "UNIDADE",
}

# DNIT_II.09.0_<n>ºOrigem-Precos-SICRO-Ref-<Mes>.<Ano>.xlsx
ORIGEM_PRECOS = {
    "aba": "ENTREGA",
    "skiprows": 4,          # cabecalho na linha 5
    "col_codigo": "CÓDIGO",
    "col_descricao": "DESCRIÇÃO DO ITEM",
    "col_unidade": "UNIDADE DO ITEM",
    "aba_ignorar": "Tabela RGB utilizada",   # oculta, nomenclatura antiga
}

# Codigo de insumo SICRO. Prefixo + digitos.
PADRAO_CODIGO = r"^[AEMP]\d+$"

# ──────────────────────────────────────────────────────────────
# UFs — ordem exata das colunas nos dois arquivos.
# Alfabetica DENTRO de cada regiao; as regioes nesta sequencia.
# Preservar nas tabelas e graficos do relatorio.
# ──────────────────────────────────────────────────────────────
UFS_POR_REGIAO = {
    "Norte":        ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
    "Nordeste":     ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Sudeste":      ["ES", "MG", "RJ", "SP"],
    "Sul":          ["PR", "RS", "SC"],
    "Centro-Oeste": ["DF", "GO", "MS", "MT"],
}

UFS = [uf for ufs in UFS_POR_REGIAO.values() for uf in ufs]   # 27

REGIAO_DA_UF = {uf: regiao for regiao, ufs in UFS_POR_REGIAO.items() for uf in ufs}

# ──────────────────────────────────────────────────────────────
# PREFIXO DO CODIGO → FRENTE DO CONTRATO
# O Tomo 1 - Materiais trata apenas do prefixo M.
# ──────────────────────────────────────────────────────────────
PREFIXO_FRENTE = {
    "M": "materiais",
    "E": "equipamentos",
    "A": "equipamentos",
    "P": "mao_obra",
}

PREFIXO_MATERIAIS = "M"

# ──────────────────────────────────────────────────────────────
# SIGLAS DE ORIGEM DE PRECO
# Descricoes: glossario literal do rodape do arquivo II.09.0.
# Cores: formatacao condicional da aba ENTREGA (paleta oficial da entrega).
# ──────────────────────────────────────────────────────────────
SIGLAS_ORIGEM = {
    "PND": "Preço não determinado",
    "PRZ": "Preço referencial zerado",
    "PCI": "Preço coletado atualizado por índice",
    "PC":  "Preço coletado",
    "PCT": "Preço coletado com tratamento",
    "PFM": "Preço com frete metodológico",
    "PEE": "Precificado por estudo específico",
    "PMP": "Precificado por metodologia de parametrização",
    "PMT": "Precificado por metodologia de parametrização com tratamento",
    "PRE": "Preço referencial estimado",
    "PEI": "Precificado por extrapolação ou interpolação",
    "PRI": "Preço referencial imputado",
    "PFE": "Preço de fontes externas",
    "SMN": "Salário substituído pelo mínimo nacional",
    "SPC": "Salário definido pelo piso da categoria",
    "SDP": "Salário de fontes secundárias de dados públicos",
    "SCM": "Salário definido por coleta de mercado",
}

# Fundo e cor de fonte por sigla. PTF, PC¹ e MDO tem regra de cor no arquivo
# mas nao ocorrem nos dados nem no glossario - mantidas no dicionario, sem
# virar categoria na saida.
CORES_SIGLAS = {
    "PC":  {"fundo": None,      "fonte": "#000000"},
    "PFM": {"fundo": "#E6E6E6", "fonte": "#000000"},
    "PRE": {"fundo": "#C4C6BE", "fonte": "#000000"},
    "PMT": {"fundo": "#979797", "fonte": "#000000"},
    "PRI": {"fundo": "#97B3A6", "fonte": "#000000"},
    "PRZ": {"fundo": "#4FB4AD", "fonte": "#000000"},
    "PFE": {"fundo": "#B7E4C7", "fonte": "#000000"},
    "PEI": {"fundo": "#A8D5FF", "fonte": "#000000"},
    "PEE": {"fundo": "#74CFFC", "fonte": "#000000"},
    "PCI": {"fundo": "#FFD6A5", "fonte": "#000000"},
    "PTF": {"fundo": "#FFF3B0", "fonte": "#000000"},
    "PC¹": {"fundo": "#D9C2FF", "fonte": "#000000"},
    "SMN": {"fundo": "#FF7F11", "fonte": "#000000"},
    "PMP": {"fundo": "#058ED1", "fonte": "#FFFFFF"},
    "PCT": {"fundo": "#001E68", "fonte": "#FFFFFF"},
    "MDO": {"fundo": "#003E7E", "fonte": "#FFFFFF"},
    "SPC": {"fundo": "#006D77", "fonte": "#FFFFFF"},
    "SDP": {"fundo": "#2F2F2F", "fonte": "#FFFFFF"},
    "SCM": {"fundo": "#6A994E", "fonte": "#FFFFFF"},
}

SIGLA_PRECO_ZERADO = "PRZ"

# ──────────────────────────────────────────────────────────────
# AMPLITUDE (relatorio, secao 2.3)
#   Amplitude = (maior preco das 27 UFs - menor preco das 27 UFs)
#               / menor preco das 27 UFs
#   Apurada apenas para itens com preco nas 27 UFs.
# Faixas da tabela 17 (materiais de ampla comercializacao).
# ──────────────────────────────────────────────────────────────
FAIXAS_AMPLITUDE_AMPLA = [
    ("Entre 0% e 30%",    0.0,   30.0),
    ("Entre 30% e 50%",  30.0,   50.0),
    ("Entre 50% e 100%", 50.0,  100.0),
    ("Maior que 100%",  100.0,   None),
]

# ──────────────────────────────────────────────────────────────
# TABELAS DO RELATORIO x BASE SNOWFLAKE x PLANILHA DAS TABELAS DO RR
# Fonte: PLANILHA_TABELAS_RR_Tomo1-Materiais.md e
#        RESUMO_BASE_HISTORICA_SNOWFLAKE.md (22/10/2026).
#
# A chave e o numero da tabela NO TEMPLATE Word. "planilha" e o numero que a
# planilha SICRO_..._TABELAS-MATERIAIS-RR-TOMO-1 usa (T10, T25...). Da T1 a
# T23 os dois coincidem. Depois deles a planilha tem uma tabela a mais (T24,
# restritas relevantes com |var| >= 10%), que o template nao tem; por isso
# T25, T26 e T27 da planilha correspondem as tabelas 24, 25 e 26 do template.
# Essa correspondencia foi feita pelo titulo e esta A CONFIRMAR.
#
# "fonte": view   -> le a view (SNOWFLAKE["views"][<view>]) e separa as linhas
#                    da tabela pela coluna que identifica a tabela, se houver.
#          lista  -> SICRO_HIST_LISTA_RELEVANTE, LISTA = <lista>
#          fora   -> nao sai da base (frete/DMT, texto do analista, cotacoes)
# ──────────────────────────────────────────────────────────────
TABELAS_RR = {
    1:  {"planilha": "T1",  "fonte": "fora", "motivo": "frete/DMT (valores digitados)"},
    2:  {"planilha": "T2",  "fonte": "fora", "motivo": "frete/DMT"},
    3:  {"planilha": "T3",  "fonte": "fora", "motivo": "frete/DMT (arquivo externo PÉTREOS)"},
    4:  {"planilha": "T4",  "fonte": "fora", "motivo": "frete/DMT"},
    5:  {"planilha": "T5",  "fonte": "fora", "motivo": "DMT (a lista de UFs com PRI sai da base)"},
    6:  {"planilha": "T6",  "fonte": "fora", "motivo": "frete/DMT"},
    7:  {"planilha": "T7",  "fonte": "fora", "motivo": "DMT (a lista de UFs com PRI sai da base)"},
    8:  {"planilha": "T8",  "fonte": "fora", "motivo": "frete/DMT"},
    9:  {"planilha": "T9",  "fonte": "lista", "lista": "T09"},
    10: {"planilha": "T10", "fonte": "view", "view": "tab_faixas"},
    11: {"planilha": "T11", "fonte": "view", "view": "tab_variacao_item"},
    12: {"planilha": "T12", "fonte": "view", "view": "tab_var_resumo"},
    13: {"planilha": "T13", "fonte": "view", "view": "tab_faixas"},
    14: {"planilha": "T14", "fonte": "view", "view": "tab_faixas"},
    15: {"planilha": "T15", "fonte": "view", "view": "tab_variacao_item"},
    16: {"planilha": "T16", "fonte": "view", "view": "tab_var_resumo",
         "observacao": "justificativa é texto do analista"},
    17: {"planilha": "T17", "fonte": "view", "view": "tab_faixas"},
    18: {"planilha": "T18", "fonte": "fora",
         "motivo": "sem view na base (números SIM + cadastro; texto do analista)"},
    19: {"planilha": "T19", "fonte": "view", "view": "tab_t19_t20"},
    20: {"planilha": "T20", "fonte": "view", "view": "tab_t19_t20",
         "observacao": "na planilha o total 1.090 da célula B6 é digitado"},
    21: {"planilha": "T21", "fonte": "view", "view": "tab_faixas"},
    22: {"planilha": "T22", "fonte": "lista", "lista": "T22"},
    23: {"planilha": "T23", "fonte": "view", "view": "tab_variacao_item"},
    24: {"planilha": "T25", "fonte": "view", "view": "tab_variacao_item"},
    25: {"planilha": "T26", "fonte": "view", "view": "tab_var_resumo",
         "observacao": "justificativa é texto do analista"},
    26: {"planilha": "T27", "fonte": "view", "view": "tab_faixas"},
    27: {"planilha": "",    "fonte": "fora", "motivo": "varejo × atacado (fora da planilha das tabelas)"},
    28: {"planilha": "",    "fonte": "fora", "motivo": "cotações"},
    29: {"planilha": "",    "fonte": "fora", "motivo": "cotações"},
    30: {"planilha": "",    "fonte": "fora", "motivo": "cotações"},
    31: {"planilha": "",    "fonte": "fora", "motivo": "cotações"},
    32: {"planilha": "",    "fonte": "fora", "motivo": "cotações"},
    33: {"planilha": "",    "fonte": "fora", "motivo": "cotações"},
    34: {"planilha": "",    "fonte": "fora", "motivo": "cotações"},
    35: {"planilha": "",    "fonte": "fora", "motivo": "cotações"},
    36: {"planilha": "",    "fonte": "fora", "motivo": "cotações"},
}

# Tabela que a planilha tem e o template nao (ver acima). Fica visivel na tela.
TABELAS_RR_SEM_TEMPLATE = {"T24": "tab_var_resumo"}

# Grafico de evolucao: quantas referencias no eixo do tempo, contando a atual.
# Plano de 24/09/2026: ate 10 referencias. A base tem 7 (2025-01 a 2026-07).
HISTORICO_MAX_REFERENCIAS = 10

# ──────────────────────────────────────────────────────────────
# PLANILHA DAS TABELAS DO RR (SICRO_AAAA.MM_TABELAS-MATERIAIS-RR-TOMO-1_*.xlsm)
# Aba "Gerenciamento Atual", cabecalho na linha 2. Cabecalhos conforme o
# mapeamento da planilha; colunas de destino conforme SICRO_HIST_CADASTRO.
# A comparacao do cabecalho ignora acento, caixa e espacos.
# O CODIGO e a coluna "Externo(código)" ou "Elementar": o leitor escolhe a que
# traz codigos no padrao PADRAO_CODIGO e mostra qual usou.
# ──────────────────────────────────────────────────────────────
PLANILHA_RR = {
    "aba_cadastro": "Gerenciamento Atual",
    "linha_cabecalho_cadastro": 2,
    "candidatas_codigo": ["externo(codigo)", "externo", "codigo externo", "elementar"],
    "colunas_cadastro": {
        "STATUS": ["status"],
        "MODALIDADE": ["modalidade"],
        "TIPO": ["tipo"],
        "COMERCIALIZACAO": ["comercializacao"],
        "RELACAO_LIDERANCA": ["relacao lideranca", "relacao de lideranca"],
        "CODIGO_LIDER": ["lider", "codigo lider"],
        "CLASSIFICACAO": ["classificacao"],
        "FAMILIA_1": ["familia_1", "familia 1"],
        "FAMILIA_2": ["familia_2", "familia 2"],
        "ANALISTA": ["analista atual"],
    },
    # abas com o resultado de cada tabela, lidas como estao (valores calculados)
    "prefixo_abas_tabelas": "Tabela",
    "abas_listas": ["Relevantes Infraestrutura", "Tabela 9"],
}
