"""Area de ADMINISTRACAO: carga de uma referencia nova no Snowflake.

Fica fora do fluxo do analista. Nao gera relatorio. Duas cargas, cada uma
feita UMA vez por referencia; o que ja existe na base nunca e sobrescrito:

  1. Precos e origens (II.08, II.09 e II.11): os arquivos vao para a pasta
     AAAA-MM/ do stage de entregas e a procedure SICRO_HIST_SP_CARREGAR_REFERENCIA
     le, valida e grava tudo numa transacao so (ela recusa referencia repetida).
  2. Cadastro (aba "Gerenciamento Atual" da planilha das tabelas do RR):
     alimenta SICRO_HIST_CADASTRO, que as views das tabelas usam para separar
     ampla e restrita.
"""

import tempfile
from pathlib import Path

import streamlit as st

import dnit_sicro_snowflake as sf
from materiais_planilha_rr import resumo_cadastro
from materiais_readers import cruzar, ler_origem_precos, ler_resultado_final
from materiais_st import planilha_rr

TITULO = "Administração"


def _salvar(arquivo, destino: Path) -> Path:
    caminho = destino / arquivo.name
    caminho.write_bytes(arquivo.getbuffer())
    return caminho


def _referencia(chave: str) -> str:
    col1, col2 = st.columns(2)
    ano = col1.number_input("Ano", min_value=2020, max_value=2100, value=2026, step=1,
                            key=f"{chave}_ano")
    mes = col2.selectbox("Mês", [1, 4, 7, 10], format_func=lambda m: f"{m:02d}",
                         key=f"{chave}_mes")
    return f"{int(ano)}-{int(mes):02d}"


# ──────────────────────────────────────────────────────────────
# 1. PRECOS E ORIGENS
# ──────────────────────────────────────────────────────────────
def _carga_precos(existentes: list) -> None:
    st.markdown("### 1. Preços e origens da referência (II.08, II.09, II.11)")
    referencia = _referencia("admin_precos")
    if referencia in existentes:
        st.error(
            f"A referência {referencia} JÁ EXISTE na base. A carga está bloqueada: "
            "esta tela não substitui referências históricas."
        )
        return

    try:
        no_stage = sf.arquivos_no_stage(referencia)
    except Exception as erro:
        st.error(f"Não consegui listar o stage: {erro}")
        return
    st.caption(f"Pasta {sf.caminho_stage(referencia)}: "
               + (", ".join(no_stage) if no_stage else "vazia"))

    preco_arq = st.file_uploader("DNIT_II.08.0 — Resultado Final (.xlsx)", type=["xlsx"], key="admin_preco")
    origem_arq = st.file_uploader("DNIT_II.09.0 — Origem de Preços (.xlsx)", type=["xlsx"], key="admin_origem")
    lider_arq = st.file_uploader("DNIT_II.11.0 — Relação Líder-Liderado (.xlsx)", type=["xlsx"], key="admin_lider")

    if preco_arq and origem_arq:
        with tempfile.TemporaryDirectory(prefix="sicro_admin_") as tmp:
            destino = Path(tmp)
            try:
                preco = ler_resultado_final(_salvar(preco_arq, destino))
                origem = ler_origem_precos(_salvar(origem_arq, destino))
                base = cruzar(preco, origem)
            except Exception as erro:
                st.error(f"Não consegui ler as planilhas: {erro}")
                return
        avisos = preco.avisos + origem.avisos + base.avisos
        if preco.titulo:
            st.caption(f"Título lido na planilha: {preco.titulo}")
            if referencia[:4] not in preco.titulo:
                avisos.append("O ano da referência informada não aparece no título da planilha.")
        for aviso in avisos:
            st.warning(aviso)
        col1, col2 = st.columns(2)
        col1.metric("Códigos no II.08 (todas as frentes)", preco.total_itens)
        col2.metric("Insumos de Materiais", base.total_itens)
        if avisos:
            st.error("Há divergências na leitura. Corrija as planilhas antes de enviar.")
            return

        enviar = [a for a in (preco_arq, origem_arq, lider_arq) if a and a.name not in no_stage]
        if enviar and st.button(f"Enviar {len(enviar)} arquivo(s) ao stage", key="admin_put"):
            try:
                for arquivo in enviar:
                    arquivo.seek(0)
                    sf.enviar_ao_stage(referencia, arquivo.name, arquivo)
            except Exception as erro:
                st.error(f"O envio ao stage falhou: {erro}")
                return
            st.success("Arquivos no stage.")
            st.rerun()

    if not no_stage:
        st.info("Envie os arquivos ao stage para liberar a carga.")
        return

    confirmo = st.checkbox(
        f"Confirmo a carga da referência {referencia} a partir do stage. "
        "Esta operação não pode ser desfeita por esta tela.",
        key="admin_confirma_precos",
    )
    if confirmo and st.button("Carregar referência no Snowflake", type="primary",
                              key="admin_gravar"):
        try:
            with st.spinner("A procedure está lendo e validando o stage…"):
                retorno = sf.carregar_referencia_pelo_stage(referencia)
        except sf.ReferenciaJaExiste as erro:
            st.error(str(erro))
            return
        except Exception as erro:
            st.error(f"A carga falhou (a procedure desfaz o que gravou): {erro}")
            return
        st.success(f"Referência {referencia} carregada. {retorno}")


# ──────────────────────────────────────────────────────────────
# 2. CADASTRO DA PLANILHA DAS TABELAS DO RR
# ──────────────────────────────────────────────────────────────
def _carga_cadastro() -> None:
    st.markdown("### 2. Cadastro da planilha das tabelas do RR")
    st.caption(
        "Lê só a aba 'Gerenciamento Atual' (status, comercialização, tipo, "
        "liderança, família, analista) e grava em SICRO_HIST_CADASTRO. "
        "Sem esse cadastro as tabelas da referência não saem completas da base."
    )
    referencia = _referencia("admin_cadastro")
    try:
        com_cadastro = sf.referencias_com_cadastro()
    except Exception as erro:
        st.error(f"Não consegui consultar o cadastro: {erro}")
        return
    st.caption("Referências com cadastro na base: " + (", ".join(com_cadastro) or "nenhuma"))
    if referencia in com_cadastro:
        st.error(f"O cadastro da referência {referencia} JÁ EXISTE na base. Carga bloqueada.")
        return

    lida = planilha_rr("admin_rr")
    if lida is None:
        return
    if lida["erro_cadastro"]:
        st.error(lida["erro_cadastro"])
        return
    cadastro, nome = lida["cadastro"], lida["nome"]

    st.caption(f"Código lido da coluna '{cadastro.coluna_codigo}'. "
               + "; ".join(f"{d} ← '{o}'" for d, o in cadastro.cabecalhos.items()))
    for aviso in cadastro.avisos:
        st.warning(aviso)
    col1, col2 = st.columns([1, 2])
    col1.metric("Códigos no cadastro", len(cadastro.dados))
    col2.dataframe(resumo_cadastro(cadastro), use_container_width=True, hide_index=True)
    st.dataframe(cadastro.dados.head(20), use_container_width=True, hide_index=True)

    if not cadastro.completo:
        st.error("Faltam colunas do cadastro. Confira o cabeçalho da aba antes de gravar.")
        return
    confirmo = st.checkbox(
        f"Confirmo a carga do cadastro da referência {referencia} "
        f"({len(cadastro.dados)} códigos, arquivo {nome}).",
        key="admin_confirma_cadastro",
    )
    if confirmo and st.button("Gravar cadastro no Snowflake", type="primary",
                              key="admin_gravar_cadastro"):
        try:
            linhas = sf.inserir_cadastro(referencia, cadastro.dados, nome)
        except sf.ReferenciaJaExiste as erro:
            st.error(str(erro))
            return
        except Exception as erro:
            st.error(f"A carga falhou e foi desfeita: {erro}")
            return
        st.success(f"Cadastro da referência {referencia} gravado: {linhas} códigos.")


def render() -> None:
    st.warning(
        "Área de AUTOMAÇÃO / ADMINISTRAÇÃO. Esta tela grava dados na base "
        "histórica do Snowflake. Não faz parte do fluxo de geração do relatório."
    )

    if not sf.configurado():
        st.error(
            "Snowflake não configurado em `dnit_sicro_config.SNOWFLAKE`. "
            "Nenhuma carga é possível por aqui."
        )
        return

    try:
        existentes = sf.listar_referencias()
    except Exception as erro:
        st.error(f"Não consegui consultar a base: {erro}")
        return
    st.caption("Referências de preço na base: " + (", ".join(existentes) or "nenhuma"))

    _carga_precos(existentes)
    st.divider()
    _carga_cadastro()
