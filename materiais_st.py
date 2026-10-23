"""Interface da frente Materiais - DNIT - SICRO.

Fluxo da tela, na ordem em que o analista trabalha:

  0. Referencia  dados da referencia atual/anterior e origem dos dados
                 (Snowflake, quando configurado, ou planilhas enviadas)
  1. Planilhas   confere o que foi lido
  2. Graficos    botao "Gerar graficos", conferencia visual na tela
  3. Tabelas     tabelas lidas das views da base (Snowflake) e/ou da
                 planilha das tabelas do RR, com a situacao de cada uma
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

import pandas as pd
import streamlit as st

import dnit_sicro_snowflake as sf
from materiais_catalogo import (
    AMPLITUDE,
    EVOLUCAO,
    ORDENAMENTO,
    blocos_texto,
    catalogo,
    linhas_tabelas_template,
    tabelas,
)
from materiais_charts import figura_para_png, gerar_graficos_iter
from materiais_config import (
    CORES_SIGLAS,
    HISTORICO_MAX_REFERENCIAS,
    REGIAO_DA_UF,
    SIGLAS_ORIGEM,
    TABELAS_RR,
    TABELAS_RR_SEM_TEMPLATE,
    UFS,
)
from materiais_tabelas import justificativas_do_template, montar
from materiais_planilha_rr import (
    abas_de_tabelas,
    abrir,
    ler_aba_bruta,
    ler_cadastro,
)
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
CHAVE_JUSTIFICATIVAS = "materiais_justificativas"

# Quantas referencias (contando a atual) a tabela 26 mostra, como no template.
REFERENCIAS_T26 = 5
# Tabelas com coluna "Justificativa" escrita pelo analista.
TABELAS_COM_JUSTIFICATIVA = (12, 16, 25)

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
    longo["regiao"] = longo["uf"].map(REGIAO_DA_UF)
    itens = (longo[["codigo", "descricao", "unidade"]].drop_duplicates("codigo")
             .sort_values("codigo").reset_index(drop=True))
    return "snowflake", BaseMateriais(itens=itens, longo=longo, preco=None, origem=None)


def _anexar_historico(base, referencia: dict) -> None:
    """Referencias anteriores da base, para o eixo do tempo da evolucao.

    Vale para as duas origens: com planilhas, a referencia atual vem delas e
    as anteriores da base. Sem a base, o grafico sai com um ponto so.
    """
    if not sf.configurado():
        return
    usar = st.checkbox(
        "Usar as referências anteriores da base nos gráficos de evolução",
        value=True, key="materiais_usar_historico",
    )
    if not usar:
        return
    codigos = sorted({c for g in catalogo() if g.tipo == EVOLUCAO for c in g.codigos})
    try:
        historico = _historico_cache(tuple(codigos), referencia["codigo"])
    except Exception as erro:
        st.warning(f"Não consegui ler o histórico na base: {erro}")
        return
    # a referencia atual vale sempre a que esta sendo processada
    historico = historico[historico["referencia"] != referencia["codigo"]]
    atual = base.longo[base.longo["codigo"].isin(codigos)][["codigo", "uf", "preco"]].copy()
    atual.insert(0, "referencia", referencia["codigo"])
    base.historico = pd.concat([historico, atual], ignore_index=True)
    refs = sorted(base.historico["referencia"].unique())
    st.caption(f"Evolução com {len(refs)} referência(s): {', '.join(refs)}.")


@st.cache_data(ttl=600, show_spinner="Lendo o histórico na base…")
def _historico_cache(codigos: tuple, referencia: str):
    return sf.carregar_historico(list(codigos), referencia, HISTORICO_MAX_REFERENCIAS)


# ──────────────────────────────────────────────────────────────
# PLANILHA DAS TABELAS DO RR (.xlsm pesado)
# ──────────────────────────────────────────────────────────────
def planilha_rr(chave: str):
    """Envio ou leitura do stage da planilha das tabelas do RR.

    A planilha e aberta uma vez por arquivo e o que foi lido (cadastro e abas
    "Tabela ...") fica na sessao: clicar na tela nao reabre o .xlsm.
    Devolve {"nome", "cadastro", "erro_cadastro", "abas"} ou None.
    """
    opcoes = ["Enviar arquivo", "Ler do stage do Snowflake"]
    if not sf.configurado():
        opcoes = opcoes[:1]
    origem = st.radio(
        "Onde está a planilha das tabelas do RR", opcoes, horizontal=True,
        key=f"{chave}_origem",
        help="No Streamlit in Snowflake o upload tem limite de tamanho; "
             "acima dele, ponha a planilha no stage e leia de lá.",
    )
    if origem == opcoes[0]:
        arquivo = st.file_uploader(
            "SICRO_AAAA.MM_TABELAS-MATERIAIS-RR-TOMO-1 (.xlsm/.xlsx)",
            type=["xlsm", "xlsx"], key=f"{chave}_arquivo",
        )
        if not arquivo:
            return None
        identidade = (arquivo.name, arquivo.size)
        abrir_fonte = lambda: abrir(arquivo)
        nome = arquivo.name
    else:
        caminho = st.text_input(
            "Caminho no stage",
            placeholder=f"{sf.caminho_stage('2026-10')}SICRO_2026.10_TABELAS-MATERIAIS-RR-TOMO-1_V02.xlsm",
            key=f"{chave}_stage",
        ).strip()
        if not caminho:
            return None
        identidade = ("stage", caminho)
        abrir_fonte = lambda: abrir(BytesIO(sf.ler_do_stage(caminho).read()))
        nome = caminho.rsplit("/", 1)[-1]

    guardado = st.session_state.get(f"{chave}_lida")
    if guardado and guardado["identidade"] == identidade:
        return guardado

    try:
        with st.spinner("Abrindo a planilha em modo somente leitura (pode levar alguns minutos)…"):
            livro = abrir_fonte()
            try:
                try:
                    cadastro, erro = ler_cadastro(livro), ""
                except Exception as e:
                    cadastro, erro = None, str(e)
                abas = {aba: ler_aba_bruta(livro, aba) for aba in abas_de_tabelas(livro)}
            finally:
                livro.close()
    except Exception as erro_abrir:
        st.error(f"Não consegui abrir a planilha: {erro_abrir}")
        return None

    guardado = {"identidade": identidade, "nome": nome, "cadastro": cadastro,
                "erro_cadastro": erro, "abas": abas}
    st.session_state[f"{chave}_lida"] = guardado
    return guardado


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
@st.cache_data(ttl=600, show_spinner="Lendo as views das tabelas na base…")
def _views_cache(referencia: str) -> dict:
    """{chave da view: DataFrame ou mensagem de erro} para a referencia."""
    lidas = {}
    usadas = {t["view"] for t in TABELAS_RR.values() if t["fonte"] == "view"}
    usadas |= set(TABELAS_RR_SEM_TEMPLATE.values())
    for chave in sorted(usadas):
        try:
            lidas[chave] = sf.ler_view(chave, referencia)
        except Exception as erro:
            lidas[chave] = f"{erro}"
    return lidas


@st.cache_data(ttl=600, show_spinner=False)
def _lista_cache(lista: str, referencia: str):
    return sf.ler_lista_relevante(lista, referencia)


@st.cache_data(ttl=600, show_spinner=False)
def _historico_t26_cache(referencia: str, quantas: int):
    refs = [r for r in sf.listar_referencias() if r <= referencia][:quantas]
    refs = sorted(refs)
    dados = sf.ler_view_referencias("tab_faixas", refs)
    dados, _ = sf.recortar_tabela(dados, "T27")
    return refs, dados


def _grade_justificativas(numero: int, dados) -> dict:
    """Justificativa por item (tabelas 12, 16 e 25), editavel na tela.

    Pre-preenchida com o texto do template quando o item ja estava la na
    referencia anterior; em branco quando e item novo.
    """
    todas = st.session_state.setdefault(CHAVE_JUSTIFICATIVAS, {})
    anteriores = justificativas_do_template(numero, linhas_tabelas_template().get(numero, []))
    codigos = [str(c) for c in dados["CODIGO"]] if "CODIGO" in dados.columns else []
    guardadas = todas.setdefault(numero, {})
    grade = pd.DataFrame({
        "Código": codigos,
        "Descrição": [str(d) for d in dados["DESCRICAO"]] if "DESCRICAO" in dados.columns else "",
        "Justificativa": [guardadas.get(c, anteriores.get(c, "")) for c in codigos],
    })
    novos = [c for c in codigos if c not in anteriores]
    st.caption(
        "Justificativa de cada item: texto do analista. Pré-preenchida com o que o "
        "template traz para o mesmo código; em branco para item novo"
        + (f" ({len(novos)}: {', '.join(novos[:8])}{'…' if len(novos) > 8 else ''})" if novos else "")
        + ". Edite na própria grade."
    )
    editada = st.data_editor(
        grade, use_container_width=True, hide_index=True, key=f"materiais_just_{numero}",
        column_config={"Código": st.column_config.TextColumn(disabled=True),
                       "Descrição": st.column_config.TextColumn(disabled=True),
                       "Justificativa": st.column_config.TextColumn(width="large")},
    )
    guardadas.update({c: str(j or "") for c, j in zip(editada["Código"], editada["Justificativa"])})
    return guardadas


def _tabelas_da_base(referencia: str, base) -> dict:
    """{numero no template: {"dados": df, "nota": str}} lidos da base."""
    views = _views_cache(referencia)
    descricao = dict(zip(base.itens["codigo"], base.itens["descricao"]))
    saida = {}
    for numero, regra in TABELAS_RR.items():
        if regra["fonte"] == "view":
            lida = views.get(regra["view"])
            if isinstance(lida, str):
                saida[numero] = {"dados": None, "nota": f"erro na view: {lida}"}
                continue
            dados, separou = sf.recortar_tabela(lida, regra["planilha"])
            nota = "" if separou else (
                "a view não tem coluna que identifique a tabela: mostrando a view inteira"
            )
            saida[numero] = {"dados": dados, "nota": nota}
        elif regra["fonte"] == "lista":
            try:
                dados = _lista_cache(regra["lista"], referencia).copy()
                dados["DESCRICAO"] = dados["CODIGO"].map(descricao)
                saida[numero] = {"dados": dados, "nota": ""}
            except Exception as erro:
                saida[numero] = {"dados": None, "nota": f"erro na lista: {erro}"}
    for codigo, chave in TABELAS_RR_SEM_TEMPLATE.items():
        lida = views.get(chave)
        if not isinstance(lida, str):
            dados, _ = sf.recortar_tabela(lida, codigo)
            saida[codigo] = {"dados": dados, "nota": "tabela da planilha sem correspondente no template"}
    return saida


def _aba_provavel(abas: list, codigo_planilha: str) -> int:
    """Indice da aba 'Tabela ...' cujo nome cita o numero da tabela (0 = nenhuma)."""
    import re

    alvo = sf.numero_tabela(codigo_planilha)[1:]
    for indice, aba in enumerate(abas, start=1):
        if alvo and alvo in re.findall(r"\d+", aba):
            return indice
    return 0


def _excel_das_tabelas(da_base: dict) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as escritor:
        for numero, item in da_base.items():
            if item["dados"] is not None:
                nome = f"Tabela {numero}" if isinstance(numero, int) else f"Planilha {numero}"
                item["dados"].to_excel(escritor, sheet_name=nome[:31], index=False)
    return buffer.getvalue()


def _passo_tabelas(referencia: dict, base) -> dict:
    """Tabelas do relatorio lidas da base (views SICRO_HIST_VW_*) e/ou da
    planilha das tabelas do RR, como o analista a deixou.

    Os calculos nao sao refeitos no app: a base ja traz as tabelas prontas nas
    views; a planilha traz os valores calculados pelo Excel. Devolve as
    tabelas lidas da base, {numero: {"dados", "nota"}}.
    """
    lista = dict(tabelas())
    origem_template = blocos_texto().get("referencia", "?")

    da_base = {}
    if sf.configurado():
        try:
            da_base = _tabelas_da_base(referencia["codigo"], base)
        except Exception as erro:
            st.warning(f"Não consegui ler as tabelas na base: {erro}")
    else:
        st.info("Base do Snowflake não configurada: as tabelas só podem vir da planilha.")

    with st.expander("Planilha das tabelas do RR (opcional: conferência ou entrada manual)"):
        st.caption(
            "A planilha .xlsm é aberta em modo somente leitura, com os valores já "
            "calculados pelo Excel. Use quando a referência ainda não estiver na "
            "base ou para conferir a base contra a planilha."
        )
        lida = planilha_rr("materiais_rr")
    abas = list(lida["abas"]) if lida else []

    situacao = []
    for numero, titulo in lista.items():
        regra = TABELAS_RR.get(numero, {"fonte": "fora", "planilha": "", "motivo": "sem regra"})
        item = da_base.get(numero)
        if regra["fonte"] == "fora":
            texto = f"Fora da base: {regra.get('motivo', '')}"
        elif item is None:
            texto = "Base indisponível"
        elif item["dados"] is None:
            texto = item["nota"]
        else:
            texto = f"Base: {len(item['dados'])} linha(s)" + (f" ({item['nota']})" if item["nota"] else "")
        if regra.get("observacao"):
            texto += f" · {regra['observacao']}"
        situacao.append({"Tabela": f"Tabela {numero}", "Planilha": regra.get("planilha", ""),
                         "Título": titulo, "Situação": texto})
    st.dataframe(pd.DataFrame(situacao), use_container_width=True, hide_index=True)
    st.caption(
        f"As tabelas que a base traz são escritas no Word com a formatação do template; "
        f"as demais saem com os valores do template ({origem_template})."
    )

    justificativas: dict = {}
    for numero, titulo in lista.items():
        regra = TABELAS_RR.get(numero, {})
        item = da_base.get(numero)
        tem_base = item is not None and item["dados"] is not None
        if not tem_base and not abas:
            continue
        with st.expander(f"Tabela {numero} - {titulo}"):
            if tem_base:
                st.markdown("**Base (Snowflake)**")
                if item["nota"]:
                    st.caption(item["nota"])
                st.dataframe(item["dados"], use_container_width=True, hide_index=True)
                if numero in TABELAS_COM_JUSTIFICATIVA:
                    justificativas[numero] = _grade_justificativas(numero, item["dados"])
            if abas:
                escolha = st.selectbox(
                    "Aba da planilha", ["—"] + abas,
                    index=_aba_provavel(abas, regra.get("planilha", "")),
                    key=f"materiais_tab_aba_{numero}",
                )
                if escolha != "—":
                    st.markdown(f"**Planilha: aba '{escolha}'**")
                    st.dataframe(lida["abas"][escolha], use_container_width=True)

    for codigo in TABELAS_RR_SEM_TEMPLATE:
        item = da_base.get(codigo)
        if item and item["dados"] is not None:
            with st.expander(f"{codigo} da planilha (sem tabela correspondente no template)"):
                st.dataframe(item["dados"], use_container_width=True, hide_index=True)

    if any(i["dados"] is not None for i in da_base.values()):
        st.download_button(
            "Baixar as tabelas da base (Excel)", data=_excel_das_tabelas(da_base),
            file_name=f"SICRO_tabelas_base_{referencia['codigo']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="materiais_baixar_tabelas",
        )
    if sf.configurado():
        with st.expander("Estrutura das views na base"):
            try:
                st.dataframe(sf.estrutura_views(), use_container_width=True, hide_index=True)
            except Exception as erro:
                st.warning(f"Não consegui ler a estrutura: {erro}")

    # o que vai para o Word
    historico, refs_t26 = None, []
    if da_base and sf.configurado():
        try:
            refs_t26, historico = _historico_t26_cache(referencia["codigo"], REFERENCIAS_T26)
        except Exception as erro:
            st.warning(f"Não consegui ler o histórico da tabela 26: {erro}")
    prontas = montar(da_base, justificativas, historico, refs_t26)
    if prontas:
        st.success(
            f"{len(prontas)} tabela(s) prontas para o Word a partir da base: "
            + ", ".join(str(n) for n in sorted(prontas))
        )
        for pronta in prontas.values():
            for aviso in pronta.avisos:
                st.warning(f"Tabela {pronta.numero}: {aviso}")
    return prontas


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
def _passo_relatorio(guardado, referencia: dict, textos: dict, prontas: dict = None) -> None:
    if not guardado:
        st.info("Gere e confira os gráficos para liberar a geração do relatório.")
        return

    total_blocos = len(blocos_texto().get("blocos", []))
    pendentes = total_blocos - len(textos)
    st.caption(
        "O relatório sai do template da entrega: marcadores da capa e das datas "
        "preenchidos, textos decididos acima escritos nos seus blocos, gráficos "
        "conferidos sob as legendas, tabelas da base escritas nas suas posições."
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
                    tabelas=prontas or {},
                )
                conteudo = destino.read_bytes()
        except Exception as erro:
            st.error(f"Não consegui gerar o documento: {erro}")
            return

    st.success(
        f"{len(resultado.graficos_inseridos)} gráficos inseridos, "
        f"{len(resultado.blocos_escritos)} blocos de texto escritos e "
        f"{len(resultado.tabelas_preenchidas)} tabelas preenchidas."
    )
    for aviso in resultado.tabelas_avisos:
        st.warning(aviso)
    if resultado.tabelas_sem_slot:
        st.warning("Tabelas sem legenda correspondente no template: "
                   + ", ".join(str(n) for n in resultado.tabelas_sem_slot))
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

    _anexar_historico(base, referencia)

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
    prontas = _passo_tabelas(referencia, base)

    st.divider()
    st.markdown("## 4. Textos do relatório")
    textos = _passo_textos(referencia)

    st.divider()
    st.markdown("## 5. Relatório em Word")
    _passo_relatorio(guardado, referencia, textos, prontas)
