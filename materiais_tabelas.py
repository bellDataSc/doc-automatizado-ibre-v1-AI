"""Tabelas do relatorio prontas para o Word, a partir das views do Snowflake.

Entrada: o que a tela leu da base (views SICRO_HIST_VW_TAB_* e
SICRO_HIST_LISTA_RELEVANTE), com as colunas reais informadas pela analista em
23/10/2026. Saida: uma `TabelaPronta` por tabela do template, com as celulas
ja em texto no formato do Word (percentual com virgula, milhar com ponto).

Nenhum calculo de negocio e refeito aqui. As unicas contas sao as que o
proprio rotulo da linha do Word declara:
  - "Totais de Ocorrencias" / "Total" = soma das linhas acima;
  - "Total Geral" = soma de todas as faixas;
  - "Insumos correspondentes (÷ 27 UFs)" = total ÷ 27;
  - rodape da tabela 19: "do total de X itens, Y por frete e Z por outras"
    com Z = X − Y.

Variacoes e proporcoes chegam como fracao (0,0222 = 2,22%), como na
planilha (Atual/Anterior − 1) e na view PROPORCAO.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

from materiais_config import TABELAS_RR, UFS

# Separador entre descricao e unidade na coluna "Descricao e Unidade",
# como esta em cada tabela do template (jul/2026).
_SEPARADOR_UNIDADE = {11: " – ", 23: " – ", 15: " – ", 24: " – ",
                      12: " - ", 16: " - ", 25: " - "}

# Rotulos de linha que nao sao faixa (rodape das tabelas de distribuicao).
_RE_TOTAL = re.compile(r"^(total|totais)", re.IGNORECASE)
_RE_TOTAL_GERAL = re.compile(r"^total\s+geral", re.IGNORECASE)
_RE_INSUMOS = re.compile(r"^insumos\s+correspondentes", re.IGNORECASE)

_MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
          "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


@dataclass
class TabelaPronta:
    """O que vai para uma tabela do template."""

    numero: int
    tipo: str                               # lista | faixas | historico | uf | resumo | fixa
    linhas: list = field(default_factory=list)      # linhas de dados, cada uma lista de str
    rodape: dict = field(default_factory=dict)      # tipo faixas: {rotulo_regex: [valores]}
    cabecalho: list = field(default_factory=list)   # tipo historico: rotulos das referencias
    celulas: dict = field(default_factory=dict)     # tipo fixa: {(linha, coluna): texto}
    avisos: list = field(default_factory=list)


# ──────────────────────────────────────────────────────────────
# FORMATACAO
# ──────────────────────────────────────────────────────────────
def _num(valor) -> float | None:
    try:
        if valor is None or pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def pct(valor, casas: int = 2) -> str:
    """Fracao -> '2,22%'. Vazio quando nao ha valor."""
    v = _num(valor)
    if v is None:
        return ""
    texto = f"{v * 100:,.{casas}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".") + "%"


def inteiro(valor) -> str:
    """1107 -> '1.107'."""
    v = _num(valor)
    if v is None:
        return ""
    return f"{int(round(v)):,}".replace(",", ".")


def rotulo_referencia(codigo: str) -> str:
    """'2026-07' -> 'julho/26', como no cabecalho da tabela 26."""
    ano, mes = codigo.split("-")
    return f"{_MESES[int(mes) - 1]}/{ano[2:]}"


def _col(df: pd.DataFrame, nome: str) -> pd.Series:
    """Coluna por nome, sem diferenciar caixa."""
    for c in df.columns:
        if str(c).upper() == nome:
            return df[c]
    raise KeyError(f"a view não tem a coluna {nome} (tem: {list(df.columns)})")


def _tem(df: pd.DataFrame, nome: str) -> bool:
    return any(str(c).upper() == nome for c in df.columns)


def _descricao_unidade(df: pd.DataFrame, numero: int) -> pd.Series:
    sep = _SEPARADOR_UNIDADE.get(numero, " – ")
    desc = _col(df, "DESCRICAO").fillna("").astype(str).str.strip()
    if not _tem(df, "UNIDADE"):
        return desc
    un = _col(df, "UNIDADE").fillna("").astype(str).str.strip()
    return [d + (sep + u if u else "") for d, u in zip(desc, un)]


# ──────────────────────────────────────────────────────────────
# POR TIPO DE TABELA
# ──────────────────────────────────────────────────────────────
def _lista(numero: int, df: pd.DataFrame) -> TabelaPronta:
    """Tabelas 9 e 22: codigo e descricao, na ordem gravada."""
    df = df.sort_values("ORDEM") if _tem(df, "ORDEM") else df
    desc = _col(df, "DESCRICAO").fillna("").astype(str)
    linhas = [[c, d] for c, d in zip(_col(df, "CODIGO").astype(str), desc)]
    return TabelaPronta(numero, "lista", linhas)


def _faixas(numero: int, df: pd.DataFrame, casas: int) -> TabelaPronta:
    """Tabelas 10, 13, 14, 17, 21: uma linha por faixa, na ORDEM do Word."""
    df = df.sort_values("ORDEM")
    linhas = [[inteiro(q), pct(p, casas)]
              for q, p in zip(_col(df, "QUANTIDADE"), _col(df, "PROPORCAO"))]
    quantidades = [_num(q) or 0 for q in _col(df, "QUANTIDADE")]
    pronta = TabelaPronta(numero, "faixas", linhas)
    pronta.rodape = {"quantidades": quantidades}
    return pronta


def _historico(numero: int, df: pd.DataFrame, referencias: list, casas: int) -> TabelaPronta:
    """Tabela 26: faixas x referencias (quantidade e proporcao), mais o total."""
    refs = [r for r in referencias if r in set(_col(df, "REFERENCIA").astype(str))]
    pronta = TabelaPronta(numero, "historico")
    pronta.cabecalho = [rotulo_referencia(r) for r in refs]
    ordens = sorted(_col(df, "ORDEM").dropna().unique())
    ref_col = _col(df, "REFERENCIA").astype(str)
    totais = {r: 0.0 for r in refs}
    for ordem in ordens:
        qtd, prop = [], []
        for r in refs:
            linha = df[(ref_col == r) & (_col(df, "ORDEM") == ordem)]
            q = _num(_col(linha, "QUANTIDADE").iloc[0]) if not linha.empty else None
            p = _col(linha, "PROPORCAO").iloc[0] if not linha.empty else None
            qtd.append(inteiro(q))
            prop.append(pct(p, casas))
            totais[r] += q or 0
        pronta.linhas.append(qtd)
        pronta.linhas.append(prop)
    pronta.rodape = {"total": [inteiro(totais[r]) for r in refs]}
    faltam = [r for r in referencias if r not in refs]
    if faltam:
        pronta.avisos.append(f"sem dados na base para {', '.join(faltam)}")
    return pronta


def _uf(numero: int, df: pd.DataFrame, casas: int) -> TabelaPronta:
    """Tabelas 11, 15, 23, 24: item x 27 UFs com a variacao."""
    codigo = _col(df, "CODIGO").astype(str)
    uf = _col(df, "UF").astype(str).str.upper()
    var = _col(df, "VARIACAO")
    ordem = _col(df, "ORDEM") if _tem(df, "ORDEM") else pd.Series(range(len(df)), index=df.index)
    valores = {}
    for c, u, v in zip(codigo, uf, var):
        valores.setdefault(c, {})[u] = v
    primeiro = (pd.DataFrame({"codigo": codigo, "ordem": ordem, "desc": _descricao_unidade(df, numero)})
                .drop_duplicates("codigo").sort_values("ordem"))
    linhas = []
    for c, d in zip(primeiro["codigo"], primeiro["desc"]):
        linhas.append([c, d] + [pct(valores[c].get(u), casas) for u in UFS])
    return TabelaPronta(numero, "uf", linhas)


def _resumo(numero: int, df: pd.DataFrame, justificativas: dict, casas: int) -> TabelaPronta:
    """Tabelas 12, 16, 25: uma linha por item, com a justificativa do analista."""
    df = df.sort_values("ORDEM") if _tem(df, "ORDEM") else df
    codigo = _col(df, "CODIGO").astype(str).tolist()
    desc = _descricao_unidade(df, numero)
    linhas, sem_justificativa = [], []
    for i, c in enumerate(codigo):
        j = (justificativas or {}).get(c, "")
        if not j:
            sem_justificativa.append(c)
        if numero == 12:
            linhas.append([c, desc[i], pct(_col(df, "VAR_MAX").iloc[i], casas),
                           pct(_col(df, "VAR_MIN").iloc[i], casas), j])
        else:
            linhas.append([c, desc[i], str(_col(df, "RELACAO_LIDERANCA").iloc[i] or ""),
                           str(_col(df, "UFS_ACIMA_20").iloc[i] or ""), j])
    pronta = TabelaPronta(numero, "resumo", linhas)
    if sem_justificativa:
        pronta.avisos.append("sem justificativa: " + ", ".join(sem_justificativa))
    return pronta


def _t19_t20(df: pd.DataFrame) -> tuple:
    """Tabelas 19 e 20 a partir da linha unica de SICRO_HIST_VW_TAB_T19_T20.

    Correspondencia (a confirmar com a analista):
      T19 linha 1  = T19_PRECOS_UFF_DMT        (precos na UFF com frete)
      T19 linha 2  = T19_PRECOS_DMT_27UF       (x 27 UFs)
      T19 rodape   = ITENS_RESTRITA, T19_PRECOS_UFF_DMT e a diferenca
      T20 linhas   = T19_PRECOS_UFF_DMT, T20_PRE, T20_PCI, T20_PEI, T20_PRI, T20_TOTAL
    """
    linha = df.iloc[0]

    def v(nome):
        return _num(_col(df, nome).iloc[0]) if _tem(df, nome) else None

    uff = v("T19_PRECOS_UFF_DMT")
    itens = v("ITENS_RESTRITA")
    outras = (itens - uff) if (itens is not None and uff is not None) else None
    t19 = TabelaPronta(19, "fixa")
    t19.celulas = {
        (1, 1): inteiro(uff),
        (2, 1): inteiro(v("T19_PRECOS_DMT_27UF")),
        (3, 0): (f"(1) do total de {inteiro(itens)} itens, {inteiro(uff)} foram estabelecidos "
                 f"por frete metodológico e {inteiro(outras)} por outras metodologias."),
    }
    t20 = TabelaPronta(20, "fixa")
    t20.celulas = {
        (1, 1): inteiro(uff),
        (2, 1): inteiro(v("T20_PRE")),
        (3, 1): inteiro(v("T20_PCI")),
        (4, 1): inteiro(v("T20_PEI")),
        (5, 1): inteiro(v("T20_PRI")),
        (6, 1): inteiro(v("T20_TOTAL")),
    }
    del linha
    return t19, t20


# ──────────────────────────────────────────────────────────────
# MONTAGEM
# ──────────────────────────────────────────────────────────────
# Casas decimais do percentual em cada tabela, como no template jul/2026.
_CASAS = {13: 1, 10: 2, 14: 2, 17: 1, 21: 2, 26: 2, 11: 2, 12: 2, 15: 2, 23: 2, 24: 2}


def montar(da_base: dict, justificativas: dict = None, historico_t26: pd.DataFrame = None,
           referencias_t26: list = None) -> dict:
    """{numero do template: TabelaPronta} para o que a base trouxe.

    `da_base` e o dicionario da tela: {numero: {"dados": df, "nota": str}}.
    `justificativas` = {numero: {codigo: texto}} decididas na tela.
    `historico_t26` = linhas da view TAB_FAIXAS (T27) das ultimas referencias.
    """
    prontas, justificativas = {}, justificativas or {}
    for numero, regra in TABELAS_RR.items():
        item = da_base.get(numero)
        if not item or item.get("dados") is None or len(item["dados"]) == 0:
            continue
        df = item["dados"]
        try:
            if regra["fonte"] == "lista":
                prontas[numero] = _lista(numero, df)
            elif regra["view"] == "tab_faixas" and numero != 26:
                prontas[numero] = _faixas(numero, df, _CASAS.get(numero, 2))
            elif regra["view"] == "tab_variacao_item":
                prontas[numero] = _uf(numero, df, _CASAS.get(numero, 2))
            elif regra["view"] == "tab_var_resumo":
                prontas[numero] = _resumo(numero, df, justificativas.get(numero, {}),
                                          _CASAS.get(numero, 2))
            elif regra["view"] == "tab_t19_t20" and numero == 19:
                t19, t20 = _t19_t20(df)
                prontas[19], prontas[20] = t19, t20
        except Exception as erro:
            prontas[numero] = TabelaPronta(numero, "erro", avisos=[str(erro)])

    if historico_t26 is not None and len(historico_t26) and referencias_t26:
        try:
            prontas[26] = _historico(26, historico_t26, referencias_t26, _CASAS[26])
        except Exception as erro:
            prontas[26] = TabelaPronta(26, "erro", avisos=[str(erro)])
    return prontas


def justificativas_do_template(numero: int, linhas_template: list) -> dict:
    """{codigo: justificativa} lidas das linhas da tabela no template."""
    saida = {}
    for linha in linhas_template:
        if len(linha) >= 5 and re.match(r"^[AEMP]\d+$", str(linha[0]).strip()):
            saida[str(linha[0]).strip()] = str(linha[-1]).strip()
    return saida
