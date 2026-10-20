"""Area de ADMINISTRACAO: carga de uma referencia nova no Snowflake.

Fica fora do fluxo do analista. Nao gera relatorio: so le as planilhas da
referencia, valida, mostra o que vai gravar e grava UMA vez. Uma referencia
que ja existe na base nunca e sobrescrita por aqui.
"""

import tempfile
from pathlib import Path

import streamlit as st

import dnit_sicro_snowflake as sf
from materiais_readers import cruzar, ler_origem_precos, ler_resultado_final

TITULO = "Administração"


def _salvar(arquivo, destino: Path) -> Path:
    caminho = destino / arquivo.name
    caminho.write_bytes(arquivo.getbuffer())
    return caminho


def render() -> None:
    st.warning(
        "Área de AUTOMAÇÃO / ADMINISTRAÇÃO. Esta tela grava dados na base "
        "histórica do Snowflake. Não faz parte do fluxo de geração do relatório."
    )

    if not sf.configurado():
        st.error(
            "Snowflake ainda não configurado: preencha database, schema e "
            "tabelas em `dnit_sicro_config.SNOWFLAKE` com os nomes devolvidos "
            "pelo Cortex Code. Até lá, nenhuma carga é possível por aqui."
        )
        return

    st.markdown("### 1. Referência a carregar")
    col1, col2 = st.columns(2)
    ano = col1.number_input("Ano", min_value=2020, max_value=2100, value=2026, step=1)
    mes = col2.selectbox("Mês", [1, 4, 7, 10], format_func=lambda m: f"{m:02d}")
    referencia = f"{int(ano)}-{int(mes):02d}"

    try:
        existentes = sf.listar_referencias()
    except Exception as erro:
        st.error(f"Não consegui consultar a base: {erro}")
        return

    st.caption("Referências já na base: " + (", ".join(existentes) or "nenhuma"))
    if referencia in existentes:
        st.error(
            f"A referência {referencia} JÁ EXISTE na base. A carga está bloqueada: "
            "esta tela não substitui referências históricas."
        )
        return

    st.markdown("### 2. Planilhas da referência")
    preco_arq = st.file_uploader("DNIT_II.08.0 — Resultado Final (.xlsx)", type=["xlsx"], key="admin_preco")
    origem_arq = st.file_uploader("DNIT_II.09.0 — Origem de Preços (.xlsx)", type=["xlsx"], key="admin_origem")
    if not (preco_arq and origem_arq):
        st.info("Envie as duas planilhas para validar a carga.")
        return

    with tempfile.TemporaryDirectory(prefix="sicro_admin_") as tmp:
        destino = Path(tmp)
        try:
            preco = ler_resultado_final(_salvar(preco_arq, destino))
            origem = ler_origem_precos(_salvar(origem_arq, destino))
            base = cruzar(preco, origem)
        except Exception as erro:
            st.error(f"Não consegui ler as planilhas: {erro}")
            return

    st.markdown("### 3. Validação")
    avisos = preco.avisos + origem.avisos + base.avisos
    for aviso in avisos:
        st.warning(aviso)
    if preco.titulo:
        st.caption(f"Título lido na planilha: {preco.titulo}")
        if referencia[:4] not in preco.titulo:
            avisos.append("O ano da referência informada não aparece no título da planilha.")
            st.warning(avisos[-1])

    col1, col2, col3 = st.columns(3)
    col1.metric("Insumos de Materiais", base.total_itens)
    col2.metric("Linhas a gravar (insumo × UF)", base.total_celulas)
    col3.metric("UFs", base.longo["uf"].nunique())
    st.dataframe(base.longo.head(20), use_container_width=True, hide_index=True)

    if avisos:
        st.error("Há divergências na leitura. Corrija as planilhas antes de carregar.")
        return

    st.markdown("### 4. Gravação")
    confirmo = st.checkbox(
        f"Confirmo a carga da referência {referencia} ({base.total_celulas} linhas). "
        "Esta operação não pode ser desfeita por esta tela."
    )
    if not confirmo:
        return
    if st.button("Gravar no Snowflake", type="primary", key="admin_gravar"):
        try:
            linhas = sf.inserir_referencia(referencia, base.longo, usuario=st.session_state.get("usuario", ""))
        except sf.ReferenciaJaExiste as erro:
            st.error(str(erro))
            return
        except Exception as erro:
            st.error(f"A carga falhou e foi desfeita: {erro}")
            return
        st.success(f"Referência {referencia} gravada: {linhas} linhas.")
