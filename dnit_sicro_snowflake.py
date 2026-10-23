"""Acesso ao Snowflake: leitura da base historica e carga controlada.

Regras:
  - No Streamlit in Snowflake a sessao vem de `get_active_session()`, sem
    credencial no codigo. Fora dele, usa a conexao nomeada em
    SNOWFLAKE["connection_name"] (connections.toml).
  - Nada aqui conhece a tela: as funcoes recebem e devolvem DataFrames.
  - Os calculos das tabelas do relatorio NAO sao refeitos aqui: o app le as
    views SICRO_HIST_VW_* que ja existem na base.
  - A gravacao e usada SO pela area de Administracao e recusa a carga quando
    a referencia ja existe; nunca sobrescreve.
  - Os nomes de schema, tabelas e views vem de dnit_sicro_config.SNOWFLAKE.
"""

from __future__ import annotations

import re

import pandas as pd

from dnit_sicro_config import SNOWFLAKE


class SnowflakeNaoConfigurado(RuntimeError):
    pass


class ReferenciaJaExiste(RuntimeError):
    pass


def configurado() -> bool:
    cfg = SNOWFLAKE
    return bool(cfg["database"] and cfg["schema"] and cfg["tabela_precos"]
                and cfg["tabela_referencias"])


def _qualificar(objeto: str) -> str:
    return f'{SNOWFLAKE["database"]}.{SNOWFLAKE["schema"]}.{objeto}'


def _nome(tabela: str) -> str:
    return _qualificar(SNOWFLAKE[tabela])


def nome_view(chave: str) -> str:
    return _qualificar(SNOWFLAKE["views"][chave])


_sessao = None


def sessao():
    """Sessao Snowpark ativa (SiS) ou local; None quando nao ha como conectar."""
    global _sessao
    if _sessao is not None:
        return _sessao
    try:
        from snowflake.snowpark.context import get_active_session
        _sessao = get_active_session()
        return _sessao
    except Exception:
        pass
    try:
        from snowflake.snowpark import Session
        _sessao = Session.builder.config(
            "connection_name", SNOWFLAKE["connection_name"]
        ).create()
        return _sessao
    except Exception:
        return None


def _exigir():
    if not configurado():
        raise SnowflakeNaoConfigurado(
            "Nomes de schema/tabelas do Snowflake nao preenchidos em "
            "dnit_sicro_config.SNOWFLAKE."
        )
    s = sessao()
    if s is None:
        raise SnowflakeNaoConfigurado("Nao foi possivel abrir uma sessao Snowflake.")
    return s


def _consulta(sql: str, params: list = None) -> pd.DataFrame:
    df = _exigir().sql(sql, params=params or []).to_pandas()
    df.columns = [str(c).upper() for c in df.columns]
    return df


def colunas_de(objeto_qualificado: str) -> list[str]:
    """Colunas de uma tabela ou view, sem ler linhas."""
    return [c.strip('"').upper() for c in _exigir().table(objeto_qualificado).schema.names]


# ──────────────────────────────────────────────────────────────
# REFERENCIAS E PRECOS
# ──────────────────────────────────────────────────────────────
def listar_referencias() -> list[str]:
    """Referencias carregadas (AAAA-MM), da mais recente para a mais antiga."""
    col = SNOWFLAKE["colunas"]["referencia"]
    df = _consulta(
        f"SELECT DISTINCT {col} AS REF FROM {_nome('tabela_referencias')} ORDER BY REF DESC"
    )
    return df["REF"].astype(str).tolist()


def referencia_existe(referencia: str) -> bool:
    col = SNOWFLAKE["colunas"]["referencia"]
    df = _consulta(
        f"SELECT COUNT(*) AS N FROM {_nome('tabela_referencias')} WHERE {col} = ?",
        [referencia],
    )
    return int(df["N"].iloc[0]) > 0


def carregar_precos(referencia: str, prefixo: str = "M") -> pd.DataFrame:
    """Base longa de uma referencia, nas mesmas colunas de BaseMateriais.longo.

    A tabela guarda todos os prefixos (M, E, A, P); `prefixo` recorta a frente.
    """
    c = SNOWFLAKE["colunas"]
    df = _consulta(
        f"""
        SELECT {c['codigo']} AS CODIGO, {c['descricao']} AS DESCRICAO,
               {c['unidade']} AS UNIDADE, {c['uf']} AS UF,
               {c['preco']} AS PRECO, {c['origem']} AS ORIGEM
        FROM {_nome('tabela_precos')}
        WHERE {c['referencia']} = ? AND STARTSWITH({c['codigo']}, ?)
        """,
        [referencia, prefixo],
    )
    df.columns = [col.lower() for col in df.columns]
    df["preco"] = pd.to_numeric(df["preco"], errors="coerce")
    return df


def carregar_historico(codigos: list, ate_referencia: str, maximo: int) -> pd.DataFrame:
    """Preco por referencia x codigo x UF das `maximo` referencias ate a atual.

    So os codigos pedidos (os dos graficos de evolucao). Colunas: referencia,
    codigo, uf, preco.
    """
    if not codigos:
        return pd.DataFrame(columns=["referencia", "codigo", "uf", "preco"])
    c = SNOWFLAKE["colunas"]
    refs = [r for r in listar_referencias() if r <= ate_referencia][:maximo]
    if not refs:
        return pd.DataFrame(columns=["referencia", "codigo", "uf", "preco"])
    marcas_ref = ", ".join("?" for _ in refs)
    marcas_cod = ", ".join("?" for _ in codigos)
    df = _consulta(
        f"""
        SELECT {c['referencia']} AS REFERENCIA, {c['codigo']} AS CODIGO,
               {c['uf']} AS UF, {c['preco']} AS PRECO
        FROM {_nome('tabela_precos')}
        WHERE {c['referencia']} IN ({marcas_ref}) AND {c['codigo']} IN ({marcas_cod})
        """,
        list(refs) + list(codigos),
    )
    df.columns = [col.lower() for col in df.columns]
    df["preco"] = pd.to_numeric(df["preco"], errors="coerce")
    return df


# ──────────────────────────────────────────────────────────────
# TABELAS DO RELATORIO (views SICRO_HIST_VW_*)
# ──────────────────────────────────────────────────────────────
# Coluna que diz a que tabela do relatorio cada linha pertence, quando a view
# junta varias (ex.: SICRO_HIST_VW_TAB_FAIXAS tem T10, T13, T14, T17, T21, T27).
_COLUNAS_TABELA = ("TABELA", "COD_TABELA", "ID_TABELA", "TAB", "TABELA_RR")


def coluna_da_tabela(colunas: list[str]) -> str:
    for nome in _COLUNAS_TABELA:
        if nome in colunas:
            return nome
    return ""


def ler_view(chave: str, referencia: str) -> pd.DataFrame:
    """Linhas de uma view para a referencia (se a view tiver REFERENCIA)."""
    nome = nome_view(chave)
    colunas = colunas_de(nome)
    col_ref = SNOWFLAKE["colunas"]["referencia"]
    if col_ref in colunas:
        return _consulta(f"SELECT * FROM {nome} WHERE {col_ref} = ?", [referencia])
    return _consulta(f"SELECT * FROM {nome}")


def numero_tabela(valor) -> str:
    """'T10', 'Tabela 10', 10 -> 'T10'. Vazio quando nao ha numero."""
    m = re.search(r"(\d+)", str(valor))
    return f"T{int(m.group(1))}" if m else ""


def recortar_tabela(df: pd.DataFrame, codigo_planilha: str) -> tuple[pd.DataFrame, bool]:
    """Linhas da tabela `codigo_planilha` (T10...) dentro do resultado da view.

    Devolve (linhas, separou). `separou` e False quando a view nao tem coluna
    que identifique a tabela: nesse caso volta a view inteira.
    """
    col = coluna_da_tabela(list(df.columns))
    if not col:
        return df, False
    alvo = numero_tabela(codigo_planilha)
    recorte = df[df[col].map(numero_tabela) == alvo]
    return recorte.reset_index(drop=True), True


def ler_lista_relevante(lista: str, referencia: str) -> pd.DataFrame:
    """Codigos de uma lista fixa (T09, T22, T23) na ordem gravada."""
    nome = _nome("tabela_lista_relevante")
    return _consulta(
        f"SELECT CODIGO, ORDEM FROM {nome} WHERE REFERENCIA = ? AND LISTA = ? ORDER BY ORDEM",
        [referencia, lista],
    )


def referencias_com_cadastro() -> list[str]:
    df = _consulta(
        f"SELECT DISTINCT REFERENCIA AS REF FROM {_nome('tabela_cadastro')} ORDER BY REF DESC"
    )
    return df["REF"].astype(str).tolist()


def estrutura_views() -> pd.DataFrame:
    """Colunas de cada view configurada, para conferencia na tela."""
    linhas = []
    for chave, view in SNOWFLAKE["views"].items():
        try:
            colunas = ", ".join(colunas_de(_qualificar(view)))
        except Exception as erro:
            colunas = f"erro: {erro}"
        linhas.append({"view": view, "colunas": colunas})
    return pd.DataFrame(linhas)


# ──────────────────────────────────────────────────────────────
# CARGA (so pela area de Administracao)
# ──────────────────────────────────────────────────────────────
def caminho_stage(referencia: str) -> str:
    return f"@{_nome('stage_entregas')}/{referencia}/"


def arquivos_no_stage(referencia: str) -> list[str]:
    """Arquivos na pasta AAAA-MM/ do stage de entregas."""
    df = _consulta(f"LIST {caminho_stage(referencia)}")
    if df.empty:
        return []
    return [str(n).rsplit("/", 1)[-1] for n in df.iloc[:, 0]]


def enviar_ao_stage(referencia: str, nome_arquivo: str, conteudo) -> None:
    """Grava um arquivo na pasta da referencia no stage. Nao substitui."""
    _exigir().file.put_stream(
        conteudo, caminho_stage(referencia) + nome_arquivo,
        auto_compress=False, overwrite=False,
    )


def ler_do_stage(caminho: str):
    """Fluxo binario de um arquivo no stage (ex.: @...STG/2026-10/planilha.xlsm)."""
    return _exigir().file.get_stream(caminho, decompress=False)


def carregar_referencia_pelo_stage(referencia: str) -> str:
    """Chama a procedure que le o stage, valida e grava a referencia.

    A procedure recusa uma referencia ja carregada; esta funcao checa antes
    para dar a mensagem na tela.
    """
    if referencia_existe(referencia):
        raise ReferenciaJaExiste(f"A referencia {referencia} ja esta na base.")
    df = _consulta(f"CALL {_nome('procedure_carga')}(?)", [referencia])
    return str(df.iloc[0, 0]) if not df.empty else ""


def cadastro_existe(referencia: str) -> bool:
    df = _consulta(
        f"SELECT COUNT(*) AS N FROM {_nome('tabela_cadastro')} WHERE REFERENCIA = ?",
        [referencia],
    )
    return int(df["N"].iloc[0]) > 0


def inserir_cadastro(referencia: str, cadastro: pd.DataFrame, arquivo: str) -> int:
    """Grava o cadastro de uma referencia em SICRO_HIST_CADASTRO. Nao sobrescreve."""
    s = _exigir()
    dados = cadastro.copy()
    dados.insert(0, "REFERENCIA", referencia)
    dados["ARQUIVO_ORIGEM"] = arquivo

    s.sql("BEGIN").collect()
    try:
        if cadastro_existe(referencia):
            raise ReferenciaJaExiste(
                f"O cadastro da referencia {referencia} ja esta na base."
            )
        s.write_pandas(
            dados, SNOWFLAKE["tabela_cadastro"],
            database=SNOWFLAKE["database"], schema=SNOWFLAKE["schema"],
            auto_create_table=False, overwrite=False,
        )
        s.sql("COMMIT").collect()
    except Exception:
        s.sql("ROLLBACK").collect()
        raise
    return int(len(dados))
