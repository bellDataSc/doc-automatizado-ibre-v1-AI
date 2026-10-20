"""Interface da frente Materiais - DNIT - SICRO.

Fluxo da tela, na ordem em que o analista trabalha:

  0. Referencia  dados da referencia atual/anterior e origem dos dados
                 (Snowflake, quando configurado, ou planilhas enviadas)
  1. Planilhas   confere o que foi lido
  2. Graficos    botao "Gerar graficos", conferencia visual na tela
  3. Tabelas     situacao de cada tabela (calculada, fixa ou pendente)
  4. Textos      cada bloco variavel com o texto da referencia anterior:
                 "Usar texto anterior / OK" ou editar
  5. Relatorio   so depois da conferencia, gera o Word a partir do template

Os graficos ficam guardados na sessao: uma vez gerados, mexer na tela nao
refaz o trabalho. Cada frente usa chaves proprias no session_state, entao
Materiais nao interfere em Equipamentos nem em Mao de Obra.
"""

import tempfile
from io import BytesIO
from pathlib import Path

import streamlit as st

import dnit_sicro_snowflake as sf
from materiais_catalogo import (
    AMPLITUDE,
    EVOLUCAO,
    ORDENAMENTO,
    blocos_texto,
    catalogo,
    tabelas,
)
from materiais_charts import figura_para_png, gerar_graficos_iter
from materiais_config import CORES_SIGLAS, SIGLAS_ORIGEM, UFS
from materiais_readers import (
    BaseMateriais,
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
CHAVE_TEXTOS = "materiais_textos"

MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]
MES_ABREV = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
MESES_REFERENCIA = [1, 4, 7, 10]

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
    ("ORDINAL", "Ordinal da entrega", "O '2' de '2ºRR' nos nomes dos arquivos."),
    ("NUM_RELATORIO", "Número do relatório", "Sai em 'RELATÓRIO DE RESULTADOS Nº', ex.: 15-08/2026."),
    ("PROTOCOLO_FGV", "Protocolo FGV IBRE", "Ex.: VDRI/821/2026."),
    ("MES_ANO_EMISSAO", "Mês e ano de emissão", "Ex.: Setembro de 2026."),
]


# ──────────────────────────────────────────────────────────────
# PASSO 0 — REFERÊNCIA E ORIGEM DOS DADOS
# ──────────────────────────────────────────────────────────────
def _referencia_anterior(ano: int, mes: int) -> tuple:
    indice = MESES_REFERENCIA.index(mes)
    if indice == 0:
        return ano - 1, MESES_REFERENCIA[-1]
    return ano, MESES_REFERENCIA[indice - 1]


def _formulario_referencia() -> dict:
    """Dados da referencia que alimentam a capa, os rodapes e as datas no texto."""
    st.markdown("## 0. Referência")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    ano = int(col1.number_input("Ano", min_value=2020, max_value=2100, value=2026, step=1,
                                key="materiais_ref_ano"))
    mes = col2.selectbox("Mês da referência", MESES_REFERENCIA,
                         format_func=lambda m: MESES[m - 1].capitalize(),
                         key="materiais_ref_mes")
    ano_ant, mes_ant = _referencia_anterior(ano, mes)
    col3.text_input("Referência anterior", value=f"{MESES[mes_ant - 1].capitalize()}/{ano_ant}",
                    disabled=True, key="materiais_ref_anterior_rotulo")
    col4.text_input("Código da referência", value=f"{ano}-{mes:02d}", disabled=True,
                    key="materiais_ref_codigo")

    campos = {}
    colunas = st.columns(len(_CAMPOS_CAPA))
    for coluna, (chave, rotulo, ajuda) in zip(colunas, _CAMPOS_CAPA):
        campos[chave] = coluna.text_input(rotulo, key=f"materiais_capa_{chave}", help=ajuda).strip()

    valores = {
        "codigo": f"{ano}-{mes:02d}",
        "codigo_anterior": f"{ano_ant}-{mes_ant:02d}",
        "REFERENCIA": f"{MESES[mes - 1].upper()}/{ano}",
        "ANO": str(ano),
        "REF_ATUAL_EXTENSO": f"{MESES[mes - 1]} de {ano}",
        "REF_ANTERIOR_EXTENSO": f"{MESES[mes_ant - 1]} de {ano_ant}",
        "REF_ATUAL_ARQUIVO": f"{MES_ABREV[mes - 1]}.{ano}",
    }
    valores.update({k: v for k, v in campos.items() if v})
    vazios = [rotulo for chave, rotulo, _ in _CAMPOS_CAPA if not campos[chave]]
    if vazios:
        st.caption("Campos da capa em branco: " + ", ".join(vazios)
                   + ". O marcador fica no Word até serem preenchidos.")
    return valores


def _origem_dos_dados(referencia: dict):
    """Snowflake (quando configurado) ou planilhas. Devolve (fonte, base ou None)."""
    opcoes = ["Planilhas enviadas", "Base histórica (Snowflake)"]
    fonte = st.radio("Origem dos dados da referência", opcoes, horizontal=True,
                     key="materiais_fonte")
    if fonte == opcoes[0]:
        return "planilhas", None

    if not sf.configurado():
        st.warning(
            "A base histórica ainda não está configurada (nomes de schema e tabelas "
            "em `dnit_sicro_config.SNOWFLAKE`). Use as planilhas por enquanto."
        )
        return "snowflake", None
    try:
        disponiveis = sf.listar_referencias()
    except Exception as erro:
        st.error(f"Não consegui consultar a base: {erro}")
        return "snowflake", None
    if referencia["codigo"] not in disponiveis:
        st.warning(
            f"A referência {referencia['codigo']} ainda não está na base "
            f"(disponíveis: {', '.join(disponiveis) or 'nenhuma'}). "
            "A carga é feita na área de Administração."
        )
        return "snowflake", None
    with st.spinner("Lendo a referência na base…"):
        longo = sf.carregar_precos(referencia["codigo"])
    itens = longo[["codigo", "descricao", "unidade"]].drop_duplicates().reset_index(drop=True)
    return "snowflake", BaseMateriais(itens=itens, longo=longo, preco=None, origem=None)


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


def _bloco_leitura_base(base) -> None:
    """Resumo quando a base veio do Snowflake (sem as planilhas na sessao)."""
    col1, col2, col3 = st.columns(3)
    col1.metric("Insumos de Materiais", f"{base.total_itens:,}".replace(",", "."))
    col2.metric("UFs", len(base.longo["uf"].unique()))
    col3.metric("Células preço × origem", f"{base.total_celulas:,}".replace(",", "."))
    st.caption("Dados lidos da base histórica. Calculado pelo sistema; confira antes de seguir.")
    abas = st.tabs(["Origem dos preços", "Preços zerados", "Amplitude", "Por insumo"])
    with abas[0]:
        _bloco_origens(base)
    with abas[1]:
        _bloco_zerados(base)
    with abas[2]:
        _bloco_amplitude(base)
    with abas[3]:
        _bloco_consulta(base)


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
# PASSO 3 — TABELAS
# ──────────────────────────────────────────────────────────────
def _passo_tabelas() -> None:
    """Situacao de cada tabela do relatorio.

    Nenhuma e calculada ainda: a planilha que alimenta as tabelas sera
    mapeada aba a aba antes de qualquer tabela ser preenchida pelo app.
    """
    lista = tabelas()
    st.caption(
        f"O template tem {len(lista)} tabelas. Até a planilha das tabelas ser "
        "mapeada, todas saem no Word com os valores da referência de origem do "
        "template. Confira a situação de cada uma:"
    )
    origem = blocos_texto().get("referencia", "?")
    st.dataframe(
        {
            "Tabela": [f"Tabela {n}" for n, _ in lista],
            "Título": [t for _, t in lista],
            "Situação": [f"Pendente: mantém valores de {origem} (template)" for _ in lista],
        },
        use_container_width=True, hide_index=True,
    )


# ──────────────────────────────────────────────────────────────
# PASSO 4 — TEXTOS
# ──────────────────────────────────────────────────────────────
def _decidir_secao(itens: list) -> None:
    decisoes = st.session_state.setdefault(CHAVE_TEXTOS, {})
    for b in itens:
        if b["id"] not in decisoes:
            anterior = "\n".join(b["paragrafos"])
            decisoes[b["id"]] = {"status": "ok", "texto": anterior}
            st.session_state[f"materiais_texto_{b['id']}"] = anterior


def _decidir_bloco(bid: str, anterior: str, texto) -> None:
    """Callback dos botoes: roda antes do rerun, quando a caixa pode ser alterada."""
    decisoes = st.session_state.setdefault(CHAVE_TEXTOS, {})
    if texto is None:
        texto = st.session_state.get(f"materiais_texto_{bid}", anterior)
    if texto.strip() == anterior.strip():
        decisoes[bid] = {"status": "ok", "texto": anterior}
    else:
        decisoes[bid] = {"status": "editado", "texto": texto}
    st.session_state[f"materiais_texto_{bid}"] = decisoes[bid]["texto"]


def _passo_textos(referencia: dict) -> dict:
    """Um bloco por texto variavel, com o texto da referencia anterior.

    O analista decide bloco a bloco: "Usar texto anterior / OK" ou editar.
    Nada e gerado automaticamente. Devolve {id: texto final} dos blocos
    decididos; os pendentes nao entram e ficam com o texto anterior no Word.
    """
    catalogo_textos = blocos_texto()
    blocos = catalogo_textos.get("blocos", [])
    if not blocos:
        st.warning("Catálogo de textos não encontrado em materiais/textos/.")
        return {}

    decisoes = st.session_state.setdefault(CHAVE_TEXTOS, {})
    origem = catalogo_textos.get("referencia", "?")
    st.caption(
        f"{len(blocos)} blocos de texto mudam a cada referência. O texto mostrado é "
        f"o da referência {origem}, já com as datas trocadas pelos marcadores "
        "{{...}}, que o Word preenche. Revise cada bloco: use o texto anterior "
        "ou edite. Blocos não decididos saem com o texto anterior e ficam "
        "marcados como pendentes."
    )

    por_secao: dict = {}
    for bloco in blocos:
        por_secao.setdefault(bloco["secao"] or "(sem seção)", []).append(bloco)

    total_ok = sum(1 for b in blocos if decisoes.get(b["id"], {}).get("status") == "ok")
    total_ed = sum(1 for b in blocos if decisoes.get(b["id"], {}).get("status") == "editado")
    col1, col2, col3 = st.columns(3)
    col1.metric("Texto anterior mantido", total_ok)
    col2.metric("Editados", total_ed)
    col3.metric("Pendentes de decisão", len(blocos) - total_ok - total_ed)

    for secao, itens in por_secao.items():
        pendentes = sum(1 for b in itens if b["id"] not in decisoes)
        rotulo = f"{secao} — {len(itens)} bloco(s)" + (f", {pendentes} pendente(s)" if pendentes else ", todos decididos")
        with st.expander(rotulo, expanded=False):
            if pendentes:
                st.button(
                    "Usar texto anterior em todos os pendentes desta seção",
                    key=f"materiais_ok_secao_{itens[0]['id']}",
                    on_click=_decidir_secao, args=(itens,),
                )

            for bloco in itens:
                bid = bloco["id"]
                anterior = "\n".join(bloco["paragrafos"])
                decisao = decisoes.get(bid)
                status = decisao["status"] if decisao else "pendente"
                selo = {"ok": "✅ texto anterior", "editado": "✏️ editado", "pendente": "⏳ pendente"}[status]
                st.markdown(f"**{bid}** · {bloco['legenda'] or secao} · {selo}")

                texto = st.text_area(
                    "Texto",
                    value=decisao["texto"] if decisao else anterior,
                    key=f"materiais_texto_{bid}",
                    height=max(90, 24 * (1 + anterior.count("\n") + len(anterior) // 110)),
                    label_visibility="collapsed",
                )
                c1, c2, c3 = st.columns([1, 1, 4])
                c1.button(
                    "Usar texto anterior / OK", key=f"materiais_ok_{bid}",
                    on_click=_decidir_bloco, args=(bid, anterior, anterior),
                )
                c2.button(
                    "Salvar edição", key=f"materiais_salvar_{bid}",
                    on_click=_decidir_bloco, args=(bid, anterior, None),
                )
                if "{{" in anterior:
                    c3.caption("Marcadores {{...}} são trocados pelas datas da referência ao gerar o Word.")
                st.divider()

    return {bid: d["texto"] for bid, d in decisoes.items()}


# ──────────────────────────────────────────────────────────────
# PASSO 5 — RELATÓRIO
# ──────────────────────────────────────────────────────────────
def _passo_relatorio(guardado, referencia: dict, textos: dict) -> None:
    if not guardado:
        st.info("Gere e confira os gráficos para liberar a geração do relatório.")
        return

    total_blocos = len(blocos_texto().get("blocos", []))
    pendentes = total_blocos - len(textos)
    st.caption(
        "O relatório sai do template da entrega: marcadores da capa e das datas "
        "preenchidos, textos decididos acima escritos nos seus blocos, gráficos "
        "conferidos sob as legendas. As tabelas continuam como estão no template."
    )
    if pendentes:
        st.warning(
            f"{pendentes} bloco(s) de texto sem decisão. Eles saem com o texto da "
            "referência anterior; confira antes de entregar."
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
                    capa=referencia,
                    dpi=DPI_WORD,
                    textos=textos,
                )
                conteudo = destino.read_bytes()
        except Exception as erro:
            st.error(f"Não consegui gerar o documento: {erro}")
            return

    st.success(
        f"{len(resultado.graficos_inseridos)} gráficos inseridos e "
        f"{len(resultado.blocos_escritos)} blocos de texto escritos."
    )
    if resultado.blocos_sem_bookmark:
        st.warning("Blocos sem marcação no template: " + ", ".join(resultado.blocos_sem_bookmark))
    if resultado.graficos_ausentes:
        st.warning(
            "Sem legenda correspondente no template: "
            + ", ".join(str(n) for n in resultado.graficos_ausentes)
        )
    if resultado.marcadores_restantes:
        st.caption(
            "Marcadores não preenchidos: "
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
    referencia = _formulario_referencia()
    fonte, base = _origem_dos_dados(referencia)

    if fonte == "planilhas":
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
        assinatura = _assinatura(enviados)
    else:
        if base is None:
            return
        assinatura = ("snowflake", referencia["codigo"])

    st.divider()
    st.markdown("## 1. Dados da referência")
    if base.preco is not None:
        _passo_planilhas(base, base.preco)
    else:
        _bloco_leitura_base(base)

    st.divider()
    st.markdown("## 2. Gráficos")
    guardado = _passo_graficos(base, referencia["REFERENCIA"].lower(), assinatura)

    st.divider()
    st.markdown("## 3. Tabelas")
    _passo_tabelas()

    st.divider()
    st.markdown("## 4. Textos do relatório")
    textos = _passo_textos(referencia)

    st.divider()
    st.markdown("## 5. Relatório em Word")
    _passo_relatorio(guardado, referencia, textos)
