"""Graficos do Tomo 1 - Materiais - DNIT - SICRO.

Tres familias de grafico, reproduzidas a partir dos exemplos da referencia
julho/2026 enviados por bel:

  amplitude    "Precos e amplitude Item M0427 ..."  (Graficos 51 a 55)
                mapa do Brasil + barras das 27 UFs + a amplitude em destaque

  evolucao     "Evolucao dos precos do Item M0003 ..." (Graficos 1 a 41, 48 a 50)
                cinco paineis: NORTE / NORDESTE / SUDESTE E SUL / CENTRO OESTE
                / MAX MED MIN, com a tabela MAX-MED-MIN embaixo

  ordenamento  "Ordenamento da familia ..." (Graficos 42 a 47, 56 a 62)
                uma linha por insumo da familia ao longo das 27 UFs, com a
                tabela de legenda embaixo

Nesta primeira versao os graficos usam SOMENTE a referencia que esta sendo
processada, como pedido. O eixo do tempo da evolucao sai com um unico ponto
e a coluna Var.% sai vazia ate a base historica existir.

O ordenamento depende da composicao da familia e da relacao lider/liderado,
que nao estao nas duas planilhas de entrada: a funcao existe e recebe esses
dados de fora.

Compatibilidade Streamlit in Snowflake: so matplotlib, pandas e json. O mapa
e desenhado com poligonos de dados/uf_brasil.json, sem biblioteca geografica.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from matplotlib.ticker import FuncFormatter
import pandas as pd

from materiais_catalogo import AMPLITUDE, EVOLUCAO, ORDENAMENTO, catalogo
from materiais_config import UFS, UFS_POR_REGIAO

# ──────────────────────────────────────────────────────────────
# PADRAO VISUAL, lido dos graficos da referencia julho/2026
# ──────────────────────────────────────────────────────────────
VERDE_CLARO = "#A1D99B"     # menor preco, no mapa e nas barras
VERDE_ESCURO = "#31A354"    # maior preco
ESCALA_PRECO = LinearSegmentedColormap.from_list(
    "sicro_verde", [VERDE_CLARO, VERDE_ESCURO]
)

CINZA_GRADE = "#D9D9D9"
CINZA_EIXO = "#BFBFBF"
PRETO = "#000000"

# Cor e marcador de cada serie do ordenamento, na ordem observada no
# grafico da familia Roller Bit (13 series). Familias menores usam o inicio
# da lista. E so aparencia: trocar aqui nao muda nenhum numero.
SERIES_ORDENAMENTO = [
    {"cor": "#E8447F", "marcador": "P", "vazado": True},
    {"cor": "#00A14B", "marcador": "X", "vazado": True},
    {"cor": "#E799C4", "marcador": "D", "vazado": True},
    {"cor": "#C55A11", "marcador": "d", "vazado": False},
    {"cor": "#2E5FA3", "marcador": "^", "vazado": True},
    {"cor": "#FFD24C", "marcador": "^", "vazado": False},
    {"cor": "#00A14B", "marcador": "*", "vazado": False},
    {"cor": "#4EA6DC", "marcador": "s", "vazado": False},
    {"cor": "#F0A22E", "marcador": "x", "vazado": False},
    {"cor": "#000000", "marcador": "o", "vazado": False},
    {"cor": "#E8A33D", "marcador": "s", "vazado": False},
    {"cor": "#00A14B", "marcador": "^", "vazado": False},
    {"cor": "#4EA6DC", "marcador": "+", "vazado": False},
]

# Cor de cada UF nos paineis da evolucao, na ordem em que a UF aparece
# dentro do painel.
SERIES_EVOLUCAO = [
    {"cor": "#F4796B", "marcador": "o"},
    {"cor": "#C8A11A", "marcador": "^"},
    {"cor": "#8BAE2B", "marcador": "s"},
    {"cor": "#3BAF54", "marcador": "D"},
    {"cor": "#22B9A0", "marcador": "*"},
    {"cor": "#29B6E8", "marcador": "X"},
    {"cor": "#6E97F2", "marcador": "P"},
    {"cor": "#B98BE8", "marcador": "p"},
    {"cor": "#F06AC4", "marcador": "h"},
]

CORES_MAX_MED_MIN = {
    "MAX": "#D98218",
    "MED": "#00A88F",
    "MIN": "#1F7FD4",
}
MARCADORES_MAX_MED_MIN = {"MAX": "o", "MED": "^", "MIN": "s"}

# Os paineis da evolucao. Sudeste e Sul dividem o mesmo painel.
PAINEIS_EVOLUCAO = [
    ("NORTE", ["Norte"]),
    ("NORDESTE", ["Nordeste"]),
    ("SUDESTE E SUL", ["Sudeste", "Sul"]),
    ("CENTRO OESTE", ["Centro-Oeste"]),
]

# Sigla da regiao na tabela MAX/MED/MIN do rodape do grafico de evolucao.
SIGLA_REGIAO = {
    "Norte": "N",
    "Nordeste": "NE",
    "Sudeste": "SE",
    "Sul": "SE",
    "Centro-Oeste": "CO",
}

# Rotulo do grupo de UFs no eixo X do ordenamento, como sai no relatorio.
ROTULO_REGIAO = {
    "Norte": "Norte",
    "Nordeste": "Nordeste",
    "Sudeste": "Sudeste",
    "Sul": "Sul",
    "Centro-Oeste": "Centro Oeste",
}

GEOMETRIA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "dados", "uf_brasil.json"
)


@dataclass
class ResultadoGrafico:
    """Um grafico do catalogo e o que saiu dele."""

    grafico: object          # materiais_catalogo.Grafico
    figura: object = None    # matplotlib Figure, ou None
    erro: str = ""

    @property
    def ok(self) -> bool:
        return self.figura is not None


# ──────────────────────────────────────────────────────────────
# FORMATACAO
# ──────────────────────────────────────────────────────────────
def br(valor: float, casas: int = 2) -> str:
    """1234.5678 -> '1.234,57'."""
    if valor is None:
        return ""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def reais(valor: float, casas: int = 4) -> str:
    return "R$ " + br(valor, casas)


def _passo_eixo(maximo: float) -> float:
    """Passo do eixo Y, como nos graficos da referencia.

    O eixo vai de zero ate seis passos, com passo = maior valor / 5 truncado.
    Reproduz os graficos das familias brita, areia, cimento, portico e
    roller bit da referencia julho/2026.
    """
    if maximo <= 0:
        return 1.0
    bruto = maximo / 5.0
    if bruto >= 1:
        return float(int(bruto))
    casas = 2
    fator = 10 ** casas
    return max(int(bruto * fator) / fator, 10 ** -casas)


def _aplicar_eixo_y(ax, maximo: float) -> None:
    passo = _passo_eixo(maximo)
    ticks = [passo * i for i in range(7)]
    casas = 2
    ax.set_ylim(0, ticks[-1])
    ax.set_yticks(ticks)
    ax.set_yticklabels([br(t, casas) for t in ticks])


def _sem_moldura(ax, manter=("left", "bottom")) -> None:
    for lado, spine in ax.spines.items():
        spine.set_visible(lado in manter)
        if lado in manter:
            spine.set_color(CINZA_EIXO)
            spine.set_linewidth(0.8)


# ──────────────────────────────────────────────────────────────
# DADOS DE UM INSUMO
# ──────────────────────────────────────────────────────────────
def _serie_do_item(base, codigo: str):
    """Preco por UF de um insumo, na ordem oficial das UFs."""
    recorte = base.longo[base.longo["codigo"] == codigo]
    if recorte.empty:
        raise ValueError(f"o insumo {codigo} nao esta na planilha lida")

    precos = recorte.set_index("uf")["preco"]
    ufs = [uf for uf in UFS if uf in precos.index]
    valores = [float(precos[uf]) for uf in ufs]

    linha = base.itens[base.itens["codigo"] == codigo]
    descricao = linha["descricao"].iloc[0] if not linha.empty else ""
    unidade = linha["unidade"].iloc[0] if not linha.empty else ""

    return ufs, valores, descricao, unidade


# ──────────────────────────────────────────────────────────────
# MAPA
# ──────────────────────────────────────────────────────────────
_geometria_cache = {}


def _geometria():
    if "uf" not in _geometria_cache:
        with open(GEOMETRIA, encoding="utf-8") as arquivo:
            _geometria_cache["uf"] = json.load(arquivo)
    return _geometria_cache["uf"]


def _desenhar_mapa(ax, valores_por_uf: dict) -> None:
    """Pinta as 27 UFs do mais claro (menor preco) ao mais escuro (maior)."""
    geo = _geometria()
    validos = [v for v in valores_por_uf.values() if v is not None]
    menor, maior = (min(validos), max(validos)) if validos else (0.0, 1.0)
    faixa = (maior - menor) or 1.0

    for uf, aneis in geo.items():
        valor = valores_por_uf.get(uf)
        cor = ESCALA_PRECO((valor - menor) / faixa) if valor is not None else "#FFFFFF"
        for anel in aneis:
            ax.add_patch(
                Polygon(anel, closed=True, facecolor=cor,
                        edgecolor="#8C8C8C", linewidth=0.5)
            )

    ax.set_aspect("equal")
    ax.autoscale_view()
    ax.set_xlim(-74.5, -33.5)
    ax.set_ylim(-34.5, 6.5)
    ax.axis("off")


# ──────────────────────────────────────────────────────────────
# GRAFICO DE AMPLITUDE  (Graficos 51 a 55)
# ──────────────────────────────────────────────────────────────
def figura_amplitude(base, codigo: str):
    """Mapa + barras das 27 UFs + amplitude percentual do insumo."""
    ufs, valores, _descricao, _unidade = _serie_do_item(base, codigo)

    pares = sorted(zip(ufs, valores), key=lambda par: par[1])
    ufs_ordem = [uf for uf, _ in pares]
    valores_ordem = [v for _, v in pares]

    menor, maior = valores_ordem[0], valores_ordem[-1]
    amplitude_pct = (maior - menor) / menor * 100 if menor > 0 else None
    faixa = (maior - menor) or 1.0

    figura = Figure(figsize=(14.0, 8.0), dpi=110)
    figura.patch.set_facecolor("white")
    eixo_mapa = figura.add_axes([0.01, 0.06, 0.46, 0.92])
    eixo_barras = figura.add_axes([0.62, 0.06, 0.24, 0.90])

    _desenhar_mapa(eixo_mapa, dict(zip(ufs, valores)))

    texto = br(amplitude_pct, 2) + "%" if amplitude_pct is not None else "—"
    eixo_mapa.text(0.04, 0.12, texto, transform=eixo_mapa.transAxes,
                   fontsize=30, fontweight="bold", color=PRETO)
    eixo_mapa.text(0.04, 0.06, "Amplitude percentual", transform=eixo_mapa.transAxes,
                   fontsize=13, color=PRETO)

    # Barra de cima = menor preco. Comprimento proporcional ao preco.
    posicoes = list(range(len(ufs_ordem)))[::-1]
    cores = [ESCALA_PRECO((v - menor) / faixa) for v in valores_ordem]
    eixo_barras.barh(posicoes, valores_ordem, color=cores, height=0.72,
                     edgecolor="none")

    eixo_barras.set_yticks(posicoes)
    eixo_barras.set_yticklabels(ufs_ordem, fontsize=10)
    eixo_barras.set_ylabel("UF", fontsize=10)
    eixo_barras.set_xlabel("Preço (R$)", fontsize=11, fontweight="bold")
    eixo_barras.set_xlim(0, maior * 1.02)
    eixo_barras.set_xticks([maior * fracao for fracao in (0.25, 0.5, 0.75, 1.0)])
    eixo_barras.set_xticklabels([])
    eixo_barras.tick_params(axis="y", length=0)
    eixo_barras.grid(axis="x", color=CINZA_GRADE, linewidth=0.5,
                     linestyle=(0, (1, 4)))
    eixo_barras.set_axisbelow(True)
    _sem_moldura(eixo_barras, manter=())

    for pos, valor in zip(posicoes, valores_ordem):
        eixo_barras.text(maior * 1.05, pos, reais(valor, 4), va="center",
                         ha="left", fontsize=9.5)

    return figura


# ──────────────────────────────────────────────────────────────
# EIXO DO TEMPO DA EVOLUCAO
# ──────────────────────────────────────────────────────────────
_MES_ABREV = ["jan", "fev", "mar", "abr", "mai", "jun",
              "jul", "ago", "set", "out", "nov", "dez"]


def _rotulo_referencia(codigo: str) -> str:
    """'2026-07' -> 'jul/2026'."""
    ano, mes = codigo.split("-")
    return f"{_MES_ABREV[int(mes) - 1]}/{ano}"


def _var_pct(serie: list) -> str:
    """Var.% da ultima referencia contra a anterior; '—' sem as duas."""
    if len(serie) < 2:
        return "—"
    atual, anterior = serie[-1], serie[-2]
    if atual != atual or anterior != anterior or not anterior:
        return "—"
    return f"{br((atual / anterior - 1) * 100, 2)}%"


# ──────────────────────────────────────────────────────────────
# GRAFICO DE EVOLUCAO  (Graficos 1 a 41, 48 a 50)
# ──────────────────────────────────────────────────────────────
def figura_evolucao(base, codigo: str, referencia: str = "referência atual"):
    """Cinco paineis de serie historica, com a tabela MAX/MED/MIN embaixo.

    Com `base.historico` (referencias anteriores lidas da base Snowflake), o
    eixo do tempo traz uma coluna por referencia e a legenda mostra a Var.% de
    cada UF: preco atual / preco anterior - 1, a mesma regra da aba Serie Hist.
    e da view SICRO_HIST_VW_VARIACAO; sem preco nas duas, fica "—".
    Sem historico, cada UF aparece como um ponto e a Var.% fica vazia.
    """
    ufs, valores, _descricao, unidade = _serie_do_item(base, codigo)
    historico = getattr(base, "historico", None)
    if historico is not None and not historico[historico["codigo"] == codigo].empty:
        recorte = historico[historico["codigo"] == codigo]
        codigos_ref = sorted(recorte["referencia"].unique())
        tabela = recorte.pivot_table(index="uf", columns="referencia", values="preco",
                                     aggfunc="first")
        series_uf = {
            uf: [float(tabela.at[uf, r]) if uf in tabela.index and r in tabela.columns
                 and pd.notna(tabela.at[uf, r]) else float("nan") for r in codigos_ref]
            for uf in ufs
        }
        referencias = [_rotulo_referencia(r) for r in codigos_ref]
    else:
        series_uf = {uf: [v] for uf, v in zip(ufs, valores)}
        referencias = [referencia]
    preco_por_uf = {uf: serie[-1] for uf, serie in series_uf.items()}

    figura = Figure(figsize=(11.5, 14.0), dpi=110)
    figura.patch.set_facecolor("white")
    grade = figura.add_gridspec(
        6, 1, height_ratios=[1, 1, 1, 1, 1, 0.55],
        left=0.10, right=0.72, top=0.98, bottom=0.03, hspace=0.30,
    )

    def preparar(ax, rotulo_linha: str, valores_painel: list) -> None:
        ax.set_ylabel(f"Preço Unitário (R$/{unidade})", fontsize=9)
        ax.set_xticks(range(len(referencias)))
        ax.set_xticklabels([])
        ax.set_xlim(-0.5, len(referencias) - 0.5)
        if valores_painel:
            menor, maior = min(valores_painel), max(valores_painel)
            margem = (maior - menor) or abs(maior) * 0.1 or 1.0
            ax.set_ylim(menor - margem * 0.6, maior + margem * 0.6)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: br(v, 2)))
        ax.grid(True, color=CINZA_GRADE, linewidth=0.5)
        ax.set_axisbelow(True)
        _sem_moldura(ax, manter=())
        ax.tick_params(length=0, labelsize=9)
        ax.text(-0.13, 0.5, rotulo_linha, transform=ax.transAxes, rotation=90,
                va="center", ha="center", fontsize=11, fontweight="bold")

    for indice, (rotulo, regioes) in enumerate(PAINEIS_EVOLUCAO):
        ax = figura.add_subplot(grade[indice])
        ufs_painel = [uf for regiao in regioes for uf in UFS_POR_REGIAO[regiao]]
        ufs_painel = [uf for uf in ufs_painel if uf in preco_por_uf]
        serie = [v for uf in ufs_painel for v in series_uf[uf] if v == v]

        for posicao, uf in enumerate(ufs_painel):
            estilo = SERIES_EVOLUCAO[posicao % len(SERIES_EVOLUCAO)]
            ax.plot(range(len(referencias)), series_uf[uf],
                    color=estilo["cor"], marker=estilo["marcador"], markersize=6,
                    linewidth=1.8, label=f"{uf}   |   {_var_pct(series_uf[uf])}")

        preparar(ax, rotulo, serie)
        ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5),
                  title="Legenda: UF e Var.%", frameon=False, fontsize=9,
                  title_fontproperties={"weight": "bold", "size": 10},
                  handlelength=2.2, labelspacing=0.7)

    # Painel MAX / MED / MIN
    maximos, medias, minimos = [], [], []
    uf_max, uf_min = [], []
    for posicao_ref in range(len(referencias)):
        pares = [(series_uf[uf][posicao_ref], uf) for uf in ufs
                 if series_uf[uf][posicao_ref] == series_uf[uf][posicao_ref]]
        if not pares:
            maximos.append(float("nan")); minimos.append(float("nan"))
            medias.append(float("nan")); uf_max.append(""); uf_min.append("")
            continue
        maior, menor = max(pares), min(pares)
        maximos.append(maior[0]); uf_max.append(maior[1])
        minimos.append(menor[0]); uf_min.append(menor[1])
        medias.append(sum(v for v, _ in pares) / len(pares))

    ax = figura.add_subplot(grade[4])
    for nome, serie in (("MAX", maximos), ("MED", medias), ("MIN", minimos)):
        ax.plot(range(len(referencias)), serie, color=CORES_MAX_MED_MIN[nome],
                marker=MARCADORES_MAX_MED_MIN[nome], markersize=8, linewidth=2.2,
                label=f"{nome} | —")
    preparar(ax, "MAX  MED  MIN", [v for v in maximos + minimos if v == v])
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5),
              title="Legenda: UF e Var.%", frameon=False, fontsize=9,
              title_fontproperties={"weight": "bold", "size": 10},
              handlelength=2.2, labelspacing=0.7)

    # Tabela MAX / MED / MIN
    from materiais_config import REGIAO_DA_UF

    eixo_tabela = figura.add_subplot(grade[5])
    eixo_tabela.axis("off")
    colunas = [0.0] + [
        0.16 + 0.84 * (i + 0.5) / len(referencias) for i in range(len(referencias))
    ]
    linhas_y = [0.92, 0.66, 0.40, 0.14]

    eixo_tabela.plot([0, 1], [1.02, 1.02], color="#808080", linewidth=1.2,
                     transform=eixo_tabela.transAxes, clip_on=False)
    eixo_tabela.text(colunas[0], linhas_y[0], "Legenda", fontsize=9.5,
                     fontweight="bold", va="center")
    for indice, rotulo in enumerate(referencias):
        eixo_tabela.text(colunas[indice + 1], linhas_y[0], rotulo, fontsize=9.5,
                         fontweight="bold", va="center", ha="center")

    conteudo = [
        ("MAX", [f"{br(v, 2)}\n{SIGLA_REGIAO.get(REGIAO_DA_UF.get(u, ''), '')}"
                 if v == v else "—" for v, u in zip(maximos, uf_max)]),
        ("MED", [br(v, 2) if v == v else "—" for v in medias]),
        ("MIN", [f"{br(v, 2)}\n{SIGLA_REGIAO.get(REGIAO_DA_UF.get(u, ''), '')}"
                 if v == v else "—" for v, u in zip(minimos, uf_min)]),
    ]
    for linha, (nome, celulas) in enumerate(conteudo, start=1):
        y = linhas_y[linha]
        eixo_tabela.plot([0, 1], [y + 0.13, y + 0.13], color="#D0D0D0",
                         linewidth=0.8, transform=eixo_tabela.transAxes,
                         clip_on=False)
        eixo_tabela.text(colunas[0], y, nome, fontsize=9.5, va="center")
        for indice, celula in enumerate(celulas):
            eixo_tabela.text(colunas[indice + 1], y, celula, fontsize=9,
                             va="center", ha="center", linespacing=1.4)
    eixo_tabela.plot([0, 1], [0.0, 0.0], color="#808080", linewidth=1.0,
                     transform=eixo_tabela.transAxes, clip_on=False)
    eixo_tabela.set_xlim(0, 1)
    eixo_tabela.set_ylim(0, 1)

    return figura


# ──────────────────────────────────────────────────────────────
# GRAFICO DE ORDENAMENTO  (Graficos 42 a 47, 56 a 62)
# ──────────────────────────────────────────────────────────────
def figura_ordenamento(base, codigos: list, lider: str = "") -> object:
    """Uma linha por insumo da familia ao longo das 27 UFs.

    `codigos` e a composicao da familia e `lider` e o insumo lider. Nenhum
    dos dois sai das planilhas de entrada: quem chama informa.
    """
    if not codigos:
        raise ValueError("informe ao menos um insumo da familia")

    series = []
    for codigo in codigos:
        ufs, valores, descricao, unidade = _serie_do_item(base, codigo)
        series.append({
            "codigo": codigo,
            "ufs": ufs,
            "valores": valores,
            "descricao": descricao,
            "unidade": unidade,
        })

    unidade = series[0]["unidade"]
    ufs_eixo = [uf for uf in UFS if uf in series[0]["ufs"]]
    posicao_da_uf = {uf: i for i, uf in enumerate(ufs_eixo)}

    altura_tabela = 0.38 + 0.30 * len(series)
    faixa_regiao = 0.72          # espaco para os rotulos Norte, Nordeste, ...
    total = 5.9 + faixa_regiao + altura_tabela
    figura = Figure(figsize=(16.0, total), dpi=110)
    figura.patch.set_facecolor("white")
    eixo = figura.add_axes(
        [0.06, (altura_tabela + faixa_regiao) / total, 0.92, 5.5 / total]
    )
    eixo_tabela = figura.add_axes([0.06, 0.02, 0.92, (altura_tabela - 0.04) / total])

    maximo = 0.0
    for indice, serie in enumerate(series):
        estilo = SERIES_ORDENAMENTO[indice % len(SERIES_ORDENAMENTO)]
        xs = [posicao_da_uf[uf] for uf in serie["ufs"] if uf in posicao_da_uf]
        ys = [v for uf, v in zip(serie["ufs"], serie["valores"])
              if uf in posicao_da_uf]
        maximo = max(maximo, max(ys) if ys else 0.0)
        eixo.plot(
            xs, ys,
            color=estilo["cor"], linewidth=1.8,
            marker=estilo["marcador"], markersize=9,
            markerfacecolor="white" if estilo["vazado"] else estilo["cor"],
            markeredgecolor=estilo["cor"], markeredgewidth=1.6,
        )

    eixo.set_xlim(-0.6, len(ufs_eixo) - 0.4)
    eixo.set_xticks(range(len(ufs_eixo)))
    eixo.set_xticklabels(ufs_eixo, fontsize=11)
    eixo.set_ylabel(f"Preço Unitário ( R$ / {unidade} )", fontsize=12,
                    fontweight="bold")
    _aplicar_eixo_y(eixo, maximo)
    eixo.tick_params(axis="both", length=0, labelsize=11)
    eixo.grid(True, color=CINZA_GRADE, linewidth=0.6)
    eixo.set_axisbelow(True)
    _sem_moldura(eixo, manter=("left",))

    # Rotulo da regiao, centrado no grupo de UFs, na faixa entre o eixo e a
    # tabela de legenda.
    caixa_eixo = eixo.get_position()
    caixa_tabela = eixo_tabela.get_position()
    y_rotulo = caixa_tabela.y1 + 0.34 * (caixa_eixo.y0 - caixa_tabela.y1)
    for regiao, ufs_regiao in UFS_POR_REGIAO.items():
        presentes = [posicao_da_uf[uf] for uf in ufs_regiao if uf in posicao_da_uf]
        if not presentes:
            continue
        centro = sum(presentes) / len(presentes)
        x_figura = eixo.transData.transform((centro, 0))[0]
        x_figura = figura.transFigure.inverted().transform((x_figura, 0))[0]
        figura.text(x_figura, y_rotulo, ROTULO_REGIAO[regiao], ha="center",
                    va="center", fontsize=12, fontweight="bold")

    _tabela_ordenamento(eixo_tabela, series, lider)
    return figura


def _tabela_ordenamento(ax, series: list, lider: str) -> None:
    """Tabela de legenda: marcador, item, descricao, lider, media, min, max, amplitude."""
    import textwrap

    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    colunas = [0.015, 0.115, 0.215, 0.545, 0.640, 0.750, 0.860, 0.945]
    titulos = ["Legenda\n(ver obs)", "Item", "Descrição e Unidade de Medida",
               "Item\nLíder", "Média", "Mínimo", "Máximo", "Amplitude"]

    linhas = 1 + len(series)
    passo = 1.0 / (linhas + 0.35)
    y_titulo = 1.0 - passo * 0.7

    ax.plot([0, 1], [1.0, 1.0], color="#808080", linewidth=1.2, clip_on=False)
    for x, titulo in zip(colunas, titulos):
        ax.text(x, y_titulo, titulo, fontsize=10.5, fontweight="bold",
                va="center", linespacing=1.5)
    ax.plot([0, 1], [y_titulo - passo * 0.55, y_titulo - passo * 0.55],
            color="#BFBFBF", linewidth=0.8, clip_on=False)

    for indice, serie in enumerate(series):
        y = y_titulo - passo * (indice + 1.1)
        estilo = SERIES_ORDENAMENTO[indice % len(SERIES_ORDENAMENTO)]
        valores = serie["valores"]
        media = sum(valores) / len(valores)
        menor, maior = min(valores), max(valores)
        amplitude_pct = (maior - menor) / menor * 100 if menor > 0 else None

        ax.plot([colunas[0] + 0.018], [y], marker=estilo["marcador"],
                markersize=11, color=estilo["cor"],
                markerfacecolor="white" if estilo["vazado"] else estilo["cor"],
                markeredgecolor=estilo["cor"], markeredgewidth=1.6,
                clip_on=False)

        rotulo_lider = "LÍDER" if serie["codigo"] == lider else (lider or "—")
        descricao = textwrap.fill(
            f"{serie['descricao']} - {serie['unidade']}", 58
        )
        celulas = [
            (colunas[1], serie["codigo"]),
            (colunas[2], descricao),
            (colunas[3], rotulo_lider),
            (colunas[4], br(media, 2)),
            (colunas[5], br(menor, 2)),
            (colunas[6], br(maior, 2)),
            (colunas[7], f"{amplitude_pct:.0f}%" if amplitude_pct is not None else "—"),
        ]
        for x, texto in celulas:
            ax.text(x, y, texto, fontsize=10, va="center", linespacing=1.5)
        ax.plot([0, 1], [y - passo * 0.5, y - passo * 0.5], color="#E5E5E5",
                linewidth=0.6, clip_on=False)

    ax.plot([0, 1], [y - passo * 0.5, y - passo * 0.5], color="#808080",
            linewidth=1.0, clip_on=False)


# ──────────────────────────────────────────────────────────────
# GERACAO EM LOTE, NA ORDEM DO RELATORIO
# ──────────────────────────────────────────────────────────────
def gerar_graficos_iter(base, referencia: str = "referência atual",
                        familias: dict = None):
    """Percorre o catalogo do template e gera o que a referencia sustenta.

    Devolve um ResultadoGrafico por vez, para a tela poder mostrar o
    andamento. `familias` mapeia o numero do grafico de ordenamento para
    {"codigos": [...], "lider": "M0191"}; sem ele os ordenamentos saem
    como pendentes.
    """
    familias = familias or {}

    for grafico in catalogo():
        if grafico.tipo == AMPLITUDE:
            construtor = lambda g=grafico: figura_amplitude(base, g.codigos[0])
        elif grafico.tipo == EVOLUCAO:
            construtor = lambda g=grafico: figura_evolucao(base, g.codigos[0],
                                                           referencia)
        elif grafico.tipo == ORDENAMENTO:
            familia = familias.get(grafico.numero)
            if not familia or not familia.get("codigos"):
                yield ResultadoGrafico(grafico, None, grafico.pendente)
                continue
            construtor = lambda f=familia: figura_ordenamento(
                base, f["codigos"], f.get("lider", "")
            )
        else:
            yield ResultadoGrafico(grafico, None, grafico.pendente)
            continue

        try:
            yield ResultadoGrafico(grafico, construtor())
        except Exception as erro:
            yield ResultadoGrafico(grafico, None, str(erro))


def gerar_graficos(base, referencia: str = "referência atual",
                   familias: dict = None) -> list:
    """gerar_graficos_iter em forma de lista."""
    return list(gerar_graficos_iter(base, referencia, familias))


def figura_para_png(figura, dpi: int = 200) -> BytesIO:
    buffer = BytesIO()
    figura.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight",
                   facecolor="white")
    buffer.seek(0)
    return buffer
