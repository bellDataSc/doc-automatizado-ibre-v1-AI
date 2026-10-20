"""Aplicação Streamlit - Automatizador de Relatórios DNIT - SICRO.

Tela de entrada e roteamento entre as três frentes de relatório do contrato:
Materiais, Equipamentos e Mão de Obra.
"""

import importlib

import streamlit as st

from dnit_sicro_config import (
    CONTRATO,
    FGV_AZUL,
    FGV_AZUL_CLARO,
    FGV_CINZA,
    FGV_FUNDO,
    FRENTES,
    SUBTITULO,
)

st.set_page_config(
    page_title=f"{SUBTITULO} | {CONTRATO}",
    page_icon="📊",
    layout="wide",
)


def aplicar_estilo() -> None:
    st.markdown(
        f"""
        <style>
        section[data-testid="stSidebar"] {{
            background-color: {FGV_FUNDO};
            border-right: 1px solid #E2E6EB;
        }}
        .fgv-marca {{
            border-left: 4px solid {FGV_AZUL};
            padding-left: .75rem;
            margin-bottom: 1.25rem;
        }}
        .fgv-marca .fgv-contrato {{
            color: {FGV_AZUL};
            font-size: 1.05rem;
            font-weight: 700;
            line-height: 1.2;
        }}
        .fgv-marca .fgv-sub {{
            color: {FGV_CINZA};
            font-size: .78rem;
            text-transform: uppercase;
            letter-spacing: .04em;
        }}
        .fgv-titulo {{
            color: {FGV_AZUL};
            font-size: 2.6rem;
            font-weight: 800;
            margin-bottom: .25rem;
        }}
        .fgv-breadcrumb {{
            color: {FGV_CINZA};
            font-size: .9rem;
            margin-bottom: 1.5rem;
        }}
        .fgv-regua {{
            height: 3px;
            width: 96px;
            background: linear-gradient(90deg, {FGV_AZUL}, {FGV_AZUL_CLARO});
            margin: 0 0 1.25rem 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def cabecalho_lateral() -> None:
    st.sidebar.markdown(
        f"""
        <div class="fgv-marca">
            <div class="fgv-sub">FGV IBRE</div>
            <div class="fgv-contrato">{CONTRATO}</div>
            <div class="fgv-sub">{SUBTITULO}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def selecionar_frente() -> str:
    chaves = list(FRENTES)
    return st.sidebar.radio(
        "Frente de relatório",
        options=chaves,
        format_func=lambda chave: FRENTES[chave]["titulo"],
        key="frente",
    )


def cabecalho_principal(titulo: str) -> None:
    st.markdown(f'<div class="fgv-titulo">{titulo}</div>', unsafe_allow_html=True)
    st.markdown('<div class="fgv-regua"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="fgv-breadcrumb">{CONTRATO} · {titulo} · Relatório</div>',
        unsafe_allow_html=True,
    )


def main() -> None:
    aplicar_estilo()
    cabecalho_lateral()

    chave = selecionar_frente()
    frente = FRENTES[chave]

    cabecalho_principal(frente["titulo"])
    st.sidebar.divider()

    modulo = importlib.import_module(frente["modulo"])
    modulo.render()


if __name__ == "__main__":
    main()
