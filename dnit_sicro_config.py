"""Configuração base da aplicação DNIT - SICRO.

Contém apenas identificação do contrato, identidade visual e o registro
das três frentes de relatório. Regras de negócio de cada frente serão
definidas posteriormente.
"""

CONTRATO = "DNIT - SICRO"
SUBTITULO = "Automatizador de Relatórios"

# Identidade visual FGV
FGV_AZUL = "#0D3B7C"
FGV_AZUL_CLARO = "#1B5DAF"
FGV_CINZA = "#5B6570"
FGV_FUNDO = "#F5F7FA"

# Frentes de relatório do contrato.
# `modulo` aponta para o arquivo Python que renderiza a interface da frente.
FRENTES = {
    "materiais": {
        "titulo": "Materiais",
        "modulo": "materiais_st",
        "pasta": "materiais",
    },
    "equipamentos": {
        "titulo": "Equipamentos",
        "modulo": "equipamentos_st",
        "pasta": "equipamentos",
    },
    "mao_obra": {
        "titulo": "Mão de Obra",
        "modulo": "mao_obra_st",
        "pasta": "mao_obra",
    },
}

# ──────────────────────────────────────────────────────────────
# SNOWFLAKE — base historica das referencias
# ──────────────────────────────────────────────────────────────
# Nomes devolvidos pelo Cortex Code (RESUMO_BASE_HISTORICA_SNOWFLAKE.md,
# 22/10/2026). Todos os objetos tem o prefixo SICRO_HIST_; as tabelas antigas
# SICRO_* nao sao usadas pelo app. Deixar "database" ou "schema" vazios
# desliga a base e o app trabalha so com as planilhas enviadas.
SNOWFLAKE = {
    "database": "BASES_SAPR",
    "schema": "AGENTE_SAPR",
    # 1 linha por referencia x codigo x UF (preco e sigla de origem)
    "tabela_precos": "SICRO_HIST_PRECO_UF",
    # 1 linha por referencia carregada (controle de duplicidade)
    "tabela_referencias": "SICRO_HIST_CONTROLE_REFERENCIA",
    # cadastro da aba "Gerenciamento Atual" da planilha das tabelas do RR
    "tabela_cadastro": "SICRO_HIST_CADASTRO",
    # listas fixas de relevantes (LISTA = T09, T22, T23)
    "tabela_lista_relevante": "SICRO_HIST_LISTA_RELEVANTE",
    # stage com uma pasta por referencia (AAAA-MM/) e a procedure que a carrega
    "stage_entregas": "SICRO_HIST_STG_ENTREGAS",
    "procedure_carga": "SICRO_HIST_SP_CARREGAR_REFERENCIA",
    # views que ja recalculam as tabelas do relatorio
    "views": {
        "serie_hist": "SICRO_HIST_VW_SERIE_HIST",
        "amplitude": "SICRO_HIST_VW_AMPLITUDE",
        "variacao": "SICRO_HIST_VW_VARIACAO",
        "tab_faixas": "SICRO_HIST_VW_TAB_FAIXAS",
        "tab_t19_t20": "SICRO_HIST_VW_TAB_T19_T20",
        "tab_variacao_item": "SICRO_HIST_VW_TAB_VARIACAO_ITEM",
        "tab_var_resumo": "SICRO_HIST_VW_TAB_VAR_RESUMO",
    },
    # nomes das colunas na tabela de precos
    "colunas": {
        "referencia": "REFERENCIA",   # AAAA-MM
        "codigo": "CODIGO",
        "descricao": "DESCRICAO",
        "unidade": "UNIDADE",
        "uf": "UF",
        "preco": "PRECO",
        "origem": "ORIGEM",
    },
    # conexao local (fora do Streamlit in Snowflake): nome em connections.toml
    "connection_name": "default",
}
