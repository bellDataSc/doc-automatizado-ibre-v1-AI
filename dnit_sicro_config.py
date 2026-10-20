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
# Os nomes abaixo sao preenchidos DEPOIS que o Cortex Code criar a estrutura
# e devolver schema, tabelas e colunas (ver docs/PROMPT_CORTEX_CARGA.md).
# Enquanto estiverem vazios, o app trabalha so com as planilhas enviadas e a
# area de Administracao fica bloqueada.
SNOWFLAKE = {
    "database": "",
    "schema": "",
    # tabela em formato longo: 1 linha por referencia x codigo x UF
    "tabela_precos": "",
    # tabela com 1 linha por referencia carregada (controle de duplicidade)
    "tabela_referencias": "",
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
