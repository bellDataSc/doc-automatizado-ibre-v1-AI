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
