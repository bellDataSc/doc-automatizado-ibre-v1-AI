"""Utilitários compartilhados entre as frentes de relatório do DNIT - SICRO."""

import streamlit as st


def painel_planilhas(frente: str, titulo: str) -> list:
    """Renderiza na barra lateral o envio das planilhas de entrada da frente.

    As planilhas específicas de cada frente ainda não foram definidas, por isso
    o envio é livre neste momento.
    """
    st.sidebar.subheader(f"Planilhas de {titulo.lower()}")
    return st.sidebar.file_uploader(
        "Planilhas de entrada (.xlsx)",
        type=["xlsx"],
        accept_multiple_files=True,
        key=f"upload_{frente}",
    )


def aviso_pendente(titulo: str, arquivos: list) -> None:
    """Mostra o estado atual da frente enquanto as regras não forem definidas."""
    if not arquivos:
        st.info(f"Envie as planilhas de {titulo.lower()} para iniciar.")
        return

    st.success(f"{len(arquivos)} planilha(s) recebida(s).")
    for arquivo in arquivos:
        st.write(f"· {arquivo.name}")
    st.caption(
        "Geração de tabelas e gráficos ainda não implementada para esta frente."
    )
