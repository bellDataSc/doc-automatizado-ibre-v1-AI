"""Interface da frente Materiais - DNIT - SICRO.

Fluxo da tela, na ordem em que o analista trabalha:

  1. Planilhas   envia o par da referencia e confere o que foi lido
  2. Graficos    botao "Gerar graficos", conferencia visual na tela
  3. Relatorio   so depois da conferencia, gera o Word a partir do template

Os graficos ficam guardados na sessao: uma vez gerados, mexer na tela nao
refaz o trabalho. Cada frente usa chaves proprias no session_state, entao
Materiais nao interfere em Equipamentos nem em Mao de Obra.
"""

import tempfile
from io import BytesIO
from pathlib import Path

import streamlit as st

from materiais_catalogo import AMPLITUDE, EVOLUCAO, ORDENAMENTO, catalogo
from materiais_charts import figura_para_png, gerar_graficos_iter
from materiais_config import CORES_SIGLAS, SIGLAS_ORIGEM, UFS
from materiais_readers import (
    amplitude,
    cruzar,
    distribuicao_origens,
    itens_por_prefixo,
    itens_zerados,
    ler_origem_precos,
    ler_resultado_final,
)
from materiais_writer import gerar_relatorio

TITULO = "Materiais"

# Resolucao da tela e do documento. A da tela e menor de proposito: sao
# dezenas de imagens na mesma pagina.
DPI_TELA = 85
DPI_WORD = 160

CHAVE_GRAFICOS = "materiais_graficos"
CHAVE_FAMILIAS = "materiais_familias"

_UPLOADS = [
    {
        "chave": "resultado_final",
        "rotulo": "DNIT_II.08.0 — Resultado Final (.xlsx)",
        "ajuda": "Preço referencial de cada insumo em cada UF.",
    },
    {
        "chave": "origem_precos",
        "rotulo": "DNIT_II.09.0 — Origem de Preços (.xlsx)",
        "ajuda": "Sigla da origem metodológica do preço, por insumo e UF.",
    },
]

_CAMPOS_CAPA = [
    ("NUM_RELATORIO", "Número do relatório", "Sai em 'RELATÓRIO DE RESULTADOS Nº'."),
    ("REFERENCIA", "Referência", "Como sai na capa, por exemplo JULHO/2026."),
    ("PROTOCOLO_FGV", "Protocolo FGV IBRE", ""),
    ("MES_ANO_EMISSAO", "Mês e ano de emissão", ""),
    ("ANO", "Ano", ""),
]


# ──────────────────────────────────────────────────────────────
# ENTRADA
# ──────────────────────────────────────────────────────────────
def _salvar(arquivo, destino: Path) -> Path:
    caminho = destino / arquivo.name
    caminho.write_bytes(arquivo.getbuffer())
    return caminho


def _painel_uploads() -> dict:
    st.sidebar.subheader("Planilhas da referência")
    st.sidebar.caption(
        "As duas são do mesmo par: mesma referência, mesma lista de códigos."
    )

    enviados = {}
    for item in _UPLOADS:
        enviados[item["chave"]] = st.sidebar.file_uploader(
            item["rotulo"],
            type=["xlsx"],
            help=item["ajuda"],
            key=f"materiais_{item['chave']}",
        )
    return enviados


def _assinatura(enviados: dict) -> tuple:
    """Identifica o par enviado, para saber quando os gráficos envelheceram."""
    return tuple(
        (enviados[item["chave"]].name, enviados[item["chave"]].size)
        for item in _UPLOADS
    )


# ──────────────────────────────────────────────────────────────
# PASSO 1 — PLANILHAS
# ──────────────────────────────────────────────────────────────
def _cor_da_sigla(sigla: str) -> str:
    cores = CORES_SIGLAS.get(sigla)
    if not cores or not cores.get("fundo"):
        return ""
    return f"background-color: {cores['fundo']}; color: {cores['fonte']}"


def _pintar(styler, funcao, colunas):
    """Aplica estilo por celula.

    Styler.map existe a partir do pandas 2.1 e substituiu Styler.applymap,
    removido no pandas 3. A versao servida pelo Snowflake nao esta sob nosso
    controle, entao aceitamos as duas.
    """
    metodo = getattr(styler, "map", None) or styler.applymap
    return metodo(funcao, subset=colunas)


def _bloco_leitura(base) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Insumos de Materiais", f"{base.total_itens:,}".replace(",", "."))
    col2.metric("UFs", len(base.longo["uf"].unique()))
    col3.metric("Células preço × origem", f"{base.total_celulas:,}".replace(",", "."))

    referencia = base.preco.titulo or base.origem.titulo
    if referencia:
        st.caption(f"Título lido na planilha: {referencia}")

    descartadas = base.preco.linhas_descartadas + base.origem.linhas_descartadas
    if descartadas:
        st.caption(
            f"{descartadas} linha(s) sem código válido foram ignoradas: "
            "linhas vazias e o bloco de legenda do rodapé."
        )

    avisos = base.preco.avisos + base.origem.avisos + base.avisos
    for aviso in avisos:
        st.warning(aviso)
    if not avisos:
        st.success("Os dois arquivos foram lidos e cruzaram sem divergência.")


def _bloco_composicao(preco) -> None:
    st.caption(
        "O Tomo 1 trata apenas do prefixo M. Os demais prefixos são de outras frentes."
    )
    st.dataframe(itens_por_prefixo(preco), use_container_width=True, hide_index=True)


def _bloco_origens(base) -> None:
    tabela = distribuicao_origens(base)
    tabela["descrição"] = tabela["sigla"].map(SIGLAS_ORIGEM).fillna("—")
    tabela = tabela[["sigla", "descrição", "celulas", "percentual"]]

    st.dataframe(
        _pintar(tabela.style, _cor_da_sigla, ["sigla"]).format(
            {"celulas": "{:,.0f}", "percentual": "{:.2f}%"}
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.caption("Cores conforme a formatação condicional do próprio arquivo de origem.")


def _bloco_zerados(base) -> None:
    zerados = itens_zerados(base)
    st.caption(f"{len(zerados)} item(ns) com preço zerado em todas as UFs.")
    st.dataframe(zerados, use_container_width=True, hide_index=True)


def _bloco_amplitude(base) -> None:
    st.caption(
        "Amplitude = (maior preço das UFs − menor preço das UFs) ÷ menor preço "
        "das UFs, apurada apenas para itens com preço em todas as UFs."
    )

    tabela = amplitude(base)
    com_preco = tabela[tabela["amplitude_pct"].notna()]

    col1, col2 = st.columns(2)
    col1.metric("Itens com preço nas UFs", len(com_preco))
    col2.metric("Itens sem preço nas UFs", len(tabela) - len(com_preco))

    st.dataframe(
        com_preco.sort_values("amplitude_pct", ascending=False)[
            ["codigo", "descricao", "unidade", "preco_min", "preco_max", "amplitude_pct"]
        ].style.format(
            {
                "preco_min": "R$ {:,.4f}",
                "preco_max": "R$ {:,.4f}",
                "amplitude_pct": "{:.2f}%",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def _bloco_consulta(base) -> None:
    codigos = base.itens["codigo"].tolist()
    if not codigos:
        return

    escolhido = st.selectbox(
        "Código",
        codigos,
        format_func=lambda c: (
            f"{c} — {base.itens.loc[base.itens['codigo'] == c, 'descricao'].iloc[0]}"
        ),
        key="materiais_consulta_codigo",
    )

    recorte = base.longo[base.longo["codigo"] == escolhido]
    ordem = {uf: i for i, uf in enumerate(UFS)}
    recorte = recorte.sort_values("uf", key=lambda s: s.map(ordem))

    st.dataframe(
        _pintar(
            recorte[["uf", "regiao", "preco", "origem"]].style, _cor_da_sigla, ["origem"]
        ).format({"preco": "R$ {:,.4f}"}),
        use_container_width=True,
        hide_index=True,
        height=320,
    )


def _passo_planilhas(base, preco) -> None:
    _bloco_leitura(base)

    abas = st.tabs(
        ["Composição", "Origem dos preços", "Preços zerados", "Amplitude", "Por insumo"]
    )
    with abas[0]:
        _bloco_composicao(preco)
    with abas[1]:
        _bloco_origens(base)
    with abas[2]:
        _bloco_zerados(base)
    with abas[3]:
        _bloco_amplitude(base)
    with abas[4]:
        _bloco_consulta(base)


# ──────────────────────────────────────────────────────────────
# PASSO 2 — GRÁFICOS
# ──────────────────────────────────────────────────────────────
def _painel_familias(base) -> dict:
    """Composicao das familias do ordenamento.

    A familia do insumo e a relacao lider/liderado nao estao nas duas
    planilhas de entrada. Enquanto nao vierem de algum lugar, quem informa
    e o analista, aqui.
    """
    pendentes = [g for g in catalogo() if g.tipo == ORDENAMENTO]
    guardado = st.session_state.setdefault(CHAVE_FAMILIAS, {})

    with st.expander(
        f"Famílias do ordenamento — {len(pendentes)} gráficos aguardando composição",
        expanded=False,
    ):
        st.caption(
            "A composição da família e o item líder não vêm das duas planilhas. "
            "Informe aqui os insumos de cada família para que o gráfico saia; "
            "deixe em branco para pular o gráfico."
        )
        codigos = base.itens["codigo"].tolist()
        rotulo = dict(zip(base.itens["codigo"], base.itens["descricao"]))

        cabecalho = st.columns([3, 1])
        cabecalho[0].caption("Insumos da família")
        cabecalho[1].caption("Item líder")

        for grafico in pendentes:
            st.markdown(f"**{grafico.titulo}**")
            col1, col2 = st.columns([3, 1])
            escolhidos = col1.multiselect(
                "Insumos da família",
                codigos,
                format_func=lambda c: f"{c} — {rotulo.get(c, '')}",
                key=f"materiais_familia_{grafico.numero}",
                placeholder="Escolha os insumos da família",
                label_visibility="collapsed",
            )
            lider = col2.selectbox(
                "Item líder",
                ["—"] + escolhidos,
                key=f"materiais_lider_{grafico.numero}",
                label_visibility="collapsed",
            )
            guardado[grafico.numero] = {
                "codigos": escolhidos,
                "lider": "" if lider == "—" else lider,
            }

    return {n: f for n, f in guardado.items() if f.get("codigos")}


def _gerar(base, referencia: str, familias: dict, assinatura: tuple) -> dict:
    total = len(catalogo())
    barra = st.progress(0.0, text="Gerando os gráficos…")

    imagens_tela, imagens_word, falhas, pendentes = {}, {}, [], []

    for indice, resultado in enumerate(
        gerar_graficos_iter(base, referencia, familias), start=1
    ):
        grafico = resultado.grafico
        if resultado.ok:
            imagens_tela[grafico.numero] = figura_para_png(
                resultado.figura, DPI_TELA
            ).getvalue()
            imagens_word[grafico.numero] = figura_para_png(
                resultado.figura, DPI_WORD
            ).getvalue()
        elif grafico.pendente:
            pendentes.append((grafico, resultado.erro))
        else:
            falhas.append((grafico, resultado.erro))

        barra.progress(indice / total, text=f"{grafico.titulo[:70]} ({indice}/{total})")

    barra.empty()
    return {
        "assinatura": assinatura,
        "referencia": referencia,
        "tela": imagens_tela,
        "word": imagens_word,
        "pendentes": pendentes,
        "falhas": falhas,
    }


def _mostrar_graficos(guardado: dict) -> None:
    tela = guardado["tela"]
    por_tipo = {
        AMPLITUDE: ("Amplitude", []),
        EVOLUCAO: ("Evolução", []),
        ORDENAMENTO: ("Ordenamento", []),
    }
    for grafico in catalogo():
        if grafico.numero in tela and grafico.tipo in por_tipo:
            por_tipo[grafico.tipo][1].append(grafico)

    rotulos = [f"{nome} ({len(itens)})" for nome, itens in por_tipo.values()]
    for aba, (_nome, itens) in zip(st.tabs(rotulos), por_tipo.values()):
        with aba:
            if not itens:
                st.info("Nenhum gráfico desta família foi gerado.")
                continue
            for grafico in itens:
                st.markdown(f"**{grafico.titulo}**")
                st.image(tela[grafico.numero], use_container_width=True)
                st.caption("Fonte: FGV IBRE")
                st.divider()


def _passo_graficos(base, referencia: str, assinatura: tuple):
    familias = _painel_familias(base)
    guardado = st.session_state.get(CHAVE_GRAFICOS)

    if guardado and guardado["assinatura"] != assinatura:
        st.info("As planilhas mudaram. Gere os gráficos de novo antes do relatório.")
        st.session_state.pop(CHAVE_GRAFICOS, None)
        guardado = None

    if st.button("Gerar gráficos", type="primary", key="materiais_gerar_graficos"):
        st.session_state[CHAVE_GRAFICOS] = _gerar(base, referencia, familias, assinatura)
        guardado = st.session_state[CHAVE_GRAFICOS]

    if not guardado:
        st.info(
            "Os gráficos saem da referência que está sendo processada. "
            "Gere e confira antes de montar o relatório."
        )
        return None

    col1, col2, col3 = st.columns(3)
    col1.metric("Gráficos gerados", len(guardado["tela"]))
    col2.metric("Aguardando dado que falta", len(guardado["pendentes"]))
    col3.metric("Gráficos do relatório", len(catalogo()))

    for grafico, erro in guardado["falhas"]:
        st.warning(f"{grafico.titulo}: {erro}")

    if guardado["pendentes"]:
        with st.expander(
            f"{len(guardado['pendentes'])} gráficos que dependem de dado fora "
            "das duas planilhas"
        ):
            for grafico, motivo in guardado["pendentes"]:
                st.write(f"· {grafico.titulo} — falta {motivo}")

    _mostrar_graficos(guardado)
    return guardado


# ──────────────────────────────────────────────────────────────
# PASSO 3 — RELATÓRIO
# ──────────────────────────────────────────────────────────────
def _passo_relatorio(guardado, base) -> None:
    if not guardado:
        st.info("Gere e confira os gráficos para liberar a geração do relatório.")
        return

    st.caption(
        "O relatório sai do template da entrega. Os gráficos conferidos entram "
        "sob as legendas correspondentes; as tabelas continuam como estão no "
        "template."
    )

    titulo_planilha = base.preco.titulo or base.origem.titulo
    if titulo_planilha:
        st.caption(f"Referência impressa na planilha: {titulo_planilha}")

    capa = {}
    colunas = st.columns(len(_CAMPOS_CAPA))
    for coluna, (chave, rotulo, ajuda) in zip(colunas, _CAMPOS_CAPA):
        capa[chave] = coluna.text_input(
            rotulo, key=f"materiais_capa_{chave}", help=ajuda or None
        )

    vazios = [rotulo for chave, rotulo, _ in _CAMPOS_CAPA if not capa[chave].strip()]
    if vazios:
        st.caption(
            "Campos da capa ainda em branco: "
            + ", ".join(vazios)
            + ". O marcador fica no documento até ser preenchido."
        )

    if not st.button(
        "Gerar relatório em Word", type="primary", key="materiais_gerar_relatorio"
    ):
        return

    with tempfile.TemporaryDirectory(prefix="sicro_word_") as tmp:
        destino = Path(tmp) / "DNIT_Tomo-1_Materiais-SICRO.docx"
        try:
            with st.spinner("Montando o documento a partir do template…"):
                resultado = gerar_relatorio(
                    {n: BytesIO(b) for n, b in guardado["word"].items()},
                    str(destino),
                    capa={k: v.strip() for k, v in capa.items() if v.strip()},
                    dpi=DPI_WORD,
                )
                conteudo = destino.read_bytes()
        except Exception as erro:
            st.error(f"Não consegui gerar o documento: {erro}")
            return

    st.success(f"{len(resultado.graficos_inseridos)} gráficos inseridos no template.")
    if resultado.graficos_ausentes:
        st.warning(
            "Sem legenda correspondente no template: "
            + ", ".join(str(n) for n in resultado.graficos_ausentes)
        )
    if resultado.marcadores_restantes:
        st.caption(
            "Marcadores da capa não preenchidos: "
            + ", ".join(resultado.marcadores_restantes)
        )

    st.download_button(
        "Baixar o relatório",
        data=conteudo,
        file_name="DNIT_Tomo-1_Materiais-SICRO.docx",
        mime=(
            "application/vnd.openxmlformats-officedocument"
            ".wordprocessingml.document"
        ),
        key="materiais_baixar",
    )


# ──────────────────────────────────────────────────────────────
# TELA
# ──────────────────────────────────────────────────────────────
def render() -> None:
    enviados = _painel_uploads()

    colunas = st.columns(len(_UPLOADS))
    for coluna, item in zip(colunas, _UPLOADS):
        nome = item["rotulo"].split(" — ")[0]
        coluna.write(
            f"{nome} recebido" if enviados[item["chave"]] else f"{nome} pendente"
        )

    if not all(enviados[item["chave"]] for item in _UPLOADS):
        st.info("Envie as duas planilhas da referência para liberar a leitura.")
        return

    with tempfile.TemporaryDirectory(prefix="sicro_materiais_") as tmp:
        destino = Path(tmp)
        try:
            with st.spinner("Lendo as planilhas…"):
                preco = ler_resultado_final(_salvar(enviados["resultado_final"], destino))
                origem = ler_origem_precos(_salvar(enviados["origem_precos"], destino))
                base = cruzar(preco, origem)
        except Exception as erro:
            st.error(f"Não consegui ler as planilhas: {erro}")
            return

    referencia = st.session_state.get("materiais_capa_REFERENCIA") or "referência atual"

    st.markdown("## 1. Planilhas da referência")
    _passo_planilhas(base, preco)

    st.divider()
    st.markdown("## 2. Gráficos")
    guardado = _passo_graficos(base, referencia, _assinatura(enviados))

    st.divider()
    st.markdown("## 3. Relatório em Word")
    _passo_relatorio(guardado, base)
