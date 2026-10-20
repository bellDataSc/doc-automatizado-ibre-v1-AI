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
