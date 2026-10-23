"""Leitura das planilhas de entrada da frente Materiais - DNIT - SICRO.

Entradas (par obrigatorio, mesma referencia):
  - DNIT_II.08.0 Resultado Final  -> VALOR do preco referencial por insumo x UF
  - DNIT_II.09.0 Origem de Precos -> SIGLA de origem do preco por insumo x UF

Os dois arquivos trazem a mesma lista de codigos e a mesma ordem de UFs.
Nenhuma regra de negocio e aplicada aqui: este modulo le, valida e cruza.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

from materiais_config import (
    ORIGEM_PRECOS,
    PADRAO_CODIGO,
    PREFIXO_FRENTE,
    PREFIXO_MATERIAIS,
    REGIAO_DA_UF,
    RESULTADO_FINAL,
    SIGLA_PRECO_ZERADO,
    UFS,
)

_CODIGO = re.compile(PADRAO_CODIGO)


# ──────────────────────────────────────────────────────────────
# RESULTADOS
# ──────────────────────────────────────────────────────────────
@dataclass
class ResultadoLeitura:
    """Uma planilha lida e higienizada."""

    dados: pd.DataFrame          # CÓDIGO, DESCRIÇÃO, UNIDADE + 27 colunas de UF
    arquivo: str
    titulo: str                  # titulo interno da planilha, como veio
    colunas_uf: list[str]
    linhas_descartadas: int = 0  # legenda do rodape e linhas vazias: esperado
    avisos: list[str] = field(default_factory=list)   # divergencias de verdade

    @property
    def total_itens(self) -> int:
        return len(self.dados)


@dataclass
class BaseMateriais:
    """Preco e origem cruzados, ja recortados na frente Materiais."""

    itens: pd.DataFrame          # 1 linha por insumo: codigo, descricao, unidade
    longo: pd.DataFrame          # 1 linha por insumo x UF: + UF, REGIAO, PRECO, ORIGEM
    preco: ResultadoLeitura
    origem: ResultadoLeitura
    avisos: list[str] = field(default_factory=list)
    # referencia, codigo, uf, preco das referencias anteriores (base historica),
    # usado no eixo do tempo dos graficos de evolucao; None sem a base
    historico: pd.DataFrame = None

    @property
    def total_itens(self) -> int:
        return len(self.itens)

    @property
    def total_celulas(self) -> int:
        return len(self.longo)


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────
def _texto(valor) -> str:
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except (TypeError, ValueError):
        pass
    return re.sub(r"\s+", " ", str(valor)).strip()


def _codigo_valido(valor) -> bool:
    return bool(_CODIGO.match(_texto(valor)))


def _colunas_uf_presentes(df: pd.DataFrame) -> list[str]:
    """UFs encontradas, na ordem oficial dos arquivos."""
    existentes = {_texto(col).upper() for col in df.columns}
    return [uf for uf in UFS if uf in existentes]


def _titulo_interno(path, aba: str, skiprows: int) -> str:
    """Le as linhas acima do cabecalho e devolve o texto mais longo.

    E de onde sai a referencia impressa na planilha
    ('... - Ref.Julho de 2026'). Nao e parseado aqui: quem interpreta a
    referencia e quem tem a regra.
    """
    try:
        cabeca = pd.read_excel(path, sheet_name=aba, header=None, nrows=skiprows)
    except Exception:
        return ""

    textos = [_texto(v) for v in cabeca.to_numpy().ravel()]
    textos = [t for t in textos if len(t) > 10]
    return max(textos, key=len) if textos else ""


def _ler_planilha(path, layout: dict, rotulo: str) -> ResultadoLeitura:
    aba = layout["aba"]
    df = pd.read_excel(path, sheet_name=aba, skiprows=layout["skiprows"])
    df.columns = [_texto(col) for col in df.columns]

    faltando = [
        layout[chave]
        for chave in ("col_codigo", "col_descricao", "col_unidade")
        if layout[chave] not in df.columns
    ]
    if faltando:
        raise ValueError(
            f"{rotulo}: nao encontrei a(s) coluna(s) {faltando} na aba '{aba}'. "
            f"Colunas lidas: {list(df.columns)[:6]}..."
        )

    linhas_brutas = len(df)
    df = df[df[layout["col_codigo"]].apply(_codigo_valido)].copy()

    df = df.rename(
        columns={
            layout["col_codigo"]: "codigo",
            layout["col_descricao"]: "descricao",
            layout["col_unidade"]: "unidade",
        }
    )

    for coluna in ("codigo", "descricao", "unidade"):
        df[coluna] = df[coluna].apply(_texto)

    colunas_uf = _colunas_uf_presentes(df)
    avisos = []

    if len(colunas_uf) != len(UFS):
        ausentes = [uf for uf in UFS if uf not in colunas_uf]
        avisos.append(f"{rotulo}: {len(colunas_uf)} de {len(UFS)} UFs. Ausentes: {ausentes}")

    duplicados = df["codigo"].duplicated().sum()
    if duplicados:
        avisos.append(f"{rotulo}: {duplicados} codigo(s) duplicado(s).")

    return ResultadoLeitura(
        dados=df[["codigo", "descricao", "unidade"] + colunas_uf].reset_index(drop=True),
        arquivo=str(getattr(path, "name", path)),
        titulo=_titulo_interno(path, aba, layout["skiprows"]),
        colunas_uf=colunas_uf,
        linhas_descartadas=linhas_brutas - len(df),
        avisos=avisos,
    )


# ──────────────────────────────────────────────────────────────
# LEITORES
# ──────────────────────────────────────────────────────────────
def ler_resultado_final(path) -> ResultadoLeitura:
    """Le o DNIT_II.08.0 - Resultado Final (valores do preco referencial).

    Zero e valor de negocio ("preco zerado"), nao dado faltante: nao vira NaN.
    O valor armazenado tem mais casas do que as 2 exibidas; o arredondamento
    fica para a apresentacao.
    """
    resultado = _ler_planilha(path, RESULTADO_FINAL, "Resultado Final")

    for uf in resultado.colunas_uf:
        resultado.dados[uf] = pd.to_numeric(resultado.dados[uf], errors="coerce")

    vazias = int(resultado.dados[resultado.colunas_uf].isna().sum().sum())
    if vazias:
        resultado.avisos.append(
            f"Resultado Final: {vazias} celula(s) de preco sem valor numerico."
        )

    return resultado


def ler_origem_precos(path) -> ResultadoLeitura:
    """Le o DNIT_II.09.0 - Origem de Precos (sigla de origem por insumo x UF)."""
    resultado = _ler_planilha(path, ORIGEM_PRECOS, "Origem de Precos")

    for uf in resultado.colunas_uf:
        resultado.dados[uf] = resultado.dados[uf].apply(_texto).str.upper()

    return resultado


# ──────────────────────────────────────────────────────────────
# CRUZAMENTO
# ──────────────────────────────────────────────────────────────
def _longo(resultado: ResultadoLeitura, nome_valor: str) -> pd.DataFrame:
    return resultado.dados.melt(
        id_vars=["codigo"],
        value_vars=resultado.colunas_uf,
        var_name="uf",
        value_name=nome_valor,
    )


def cruzar(preco: ResultadoLeitura, origem: ResultadoLeitura) -> BaseMateriais:
    """Cruza preco x origem pelo codigo e recorta a frente Materiais (prefixo M).

    As validacoes de consistencia viram avisos, nunca excecao: a tela mostra
    o que foi lido mesmo quando os dois arquivos discordam.
    """
    avisos: list[str] = []

    codigos_preco = set(preco.dados["codigo"])
    codigos_origem = set(origem.dados["codigo"])

    so_preco = sorted(codigos_preco - codigos_origem)
    so_origem = sorted(codigos_origem - codigos_preco)

    if so_preco:
        avisos.append(
            f"{len(so_preco)} codigo(s) so no Resultado Final "
            f"(ex.: {', '.join(so_preco[:5])})."
        )
    if so_origem:
        avisos.append(
            f"{len(so_origem)} codigo(s) so na Origem de Precos "
            f"(ex.: {', '.join(so_origem[:5])})."
        )

    if preco.colunas_uf != origem.colunas_uf:
        avisos.append("A ordem/lista de UFs difere entre os dois arquivos.")

    base = _longo(preco, "preco").merge(_longo(origem, "origem"), on=["codigo", "uf"])

    itens = preco.dados[["codigo", "descricao", "unidade"]].copy()
    itens["frente"] = itens["codigo"].str[0].map(PREFIXO_FRENTE)

    base = base.merge(itens, on="codigo")
    base["regiao"] = base["uf"].map(REGIAO_DA_UF)

    # Consistencia declarada no relatorio: origem PRZ <=> preco zero.
    prz = base["origem"].eq(SIGLA_PRECO_ZERADO)
    zero = base["preco"].eq(0)
    divergentes = int((prz ^ zero).sum())
    if divergentes:
        avisos.append(
            f"{divergentes} celula(s) em que 'origem PRZ' e 'preco igual a zero' "
            "nao coincidem."
        )

    materiais = base[base["frente"] == PREFIXO_FRENTE[PREFIXO_MATERIAIS]].copy()
    itens_materiais = (
        itens[itens["frente"] == PREFIXO_FRENTE[PREFIXO_MATERIAIS]]
        .drop(columns="frente")
        .reset_index(drop=True)
    )

    colunas = ["codigo", "descricao", "unidade", "uf", "regiao", "preco", "origem"]

    return BaseMateriais(
        itens=itens_materiais,
        longo=materiais[colunas].reset_index(drop=True),
        preco=preco,
        origem=origem,
        avisos=avisos,
    )


# ──────────────────────────────────────────────────────────────
# RECORTES QUE SAEM SO DOS DOIS ARQUIVOS
# ──────────────────────────────────────────────────────────────
def itens_por_prefixo(preco: ResultadoLeitura) -> pd.DataFrame:
    """Contagem de itens por prefixo do codigo e frente correspondente."""
    df = preco.dados[["codigo"]].copy()
    df["prefixo"] = df["codigo"].str[0]
    df["frente"] = df["prefixo"].map(PREFIXO_FRENTE)

    return (
        df.groupby(["prefixo", "frente"], dropna=False)
        .size()
        .reset_index(name="itens")
        .sort_values("itens", ascending=False)
        .reset_index(drop=True)
    )


def distribuicao_origens(base: BaseMateriais) -> pd.DataFrame:
    """Celulas por sigla de origem, dentro de Materiais."""
    total = len(base.longo)
    contagem = base.longo["origem"].value_counts().reset_index()
    contagem.columns = ["sigla", "celulas"]
    contagem["percentual"] = contagem["celulas"] / total * 100 if total else 0.0
    return contagem


def itens_zerados(base: BaseMateriais) -> pd.DataFrame:
    """Itens com preco igual a zero em TODAS as UFs lidas.

    O relatorio (2.1.1) trata esse conjunto como 'materiais com precos
    zerados'. Aqui ele e apenas apurado, sem nenhuma outra regra aplicada.
    """
    por_item = base.longo.groupby("codigo")["preco"]
    zerados = por_item.apply(lambda s: bool(s.eq(0).all())).rename("zerado")

    return (
        base.itens.merge(zerados[zerados].reset_index()[["codigo"]], on="codigo")
        .reset_index(drop=True)
    )


def amplitude(base: BaseMateriais) -> pd.DataFrame:
    """Amplitude por item, conforme a formula da secao 2.3 do relatorio.

        Amplitude = (maior preco das 27 UFs - menor preco das 27 UFs)
                    / menor preco das 27 UFs

    Apurada apenas para itens com preco em todas as UFs lidas. Itens com
    algum preco zerado ficam de fora, como 'itens sem preco nas 27 UFs'.
    """
    faltantes = set(base.longo.loc[base.longo["preco"].isna(), "codigo"])

    agregado = (
        base.longo.groupby("codigo")["preco"]
        .agg(preco_min="min", preco_max="max", ufs="count")
        .reset_index()
    )

    n_ufs = base.longo["uf"].nunique()
    completo = (
        agregado["ufs"].eq(n_ufs)
        & agregado["preco_min"].gt(0)
        & ~agregado["codigo"].isin(faltantes)
    )

    agregado["amplitude_pct"] = pd.NA
    agregado.loc[completo, "amplitude_pct"] = (
        (agregado.loc[completo, "preco_max"] - agregado.loc[completo, "preco_min"])
        / agregado.loc[completo, "preco_min"]
        * 100
    )

    return base.itens.merge(agregado, on="codigo").reset_index(drop=True)
