"""Acesso ao Snowflake: leitura das referencias historicas e carga controlada.

Regras:
  - No Streamlit in Snowflake a sessao vem de `get_active_session()`, sem
    credencial no codigo. Fora dele, usa a conexao nomeada em
    SNOWFLAKE["connection_name"] (connections.toml).
  - Nada aqui conhece a tela: as funcoes recebem e devolvem DataFrames.
  - A gravacao (`inserir_referencia`) e usada SO pela area de Administracao.
    Ela recusa a carga quando a referencia ja existe; nunca sobrescreve.
  - Os nomes de schema, tabelas e colunas vem de dnit_sicro_config.SNOWFLAKE
    e so sao preenchidos depois que o Cortex Code criar a estrutura.
"""

from __future__ import annotations

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


def _nome(tabela: str) -> str:
    return f'{SNOWFLAKE["database"]}.{SNOWFLAKE["schema"]}.{SNOWFLAKE[tabela]}'


def sessao():
    """Sessao Snowpark ativa (SiS) ou local; None quando nao ha como conectar."""
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception:
        pass
    try:
        from snowflake.snowpark import Session
        return Session.builder.config(
            "connection_name", SNOWFLAKE["connection_name"]
        ).create()
    except Exception:
        return None


def _exigir():
    if not configurado():
        raise SnowflakeNaoConfigurado(
            "Nomes de schema/tabelas do Snowflake ainda nao preenchidos em "
            "dnit_sicro_config.SNOWFLAKE."
        )
    s = sessao()
    if s is None:
        raise SnowflakeNaoConfigurado("Nao foi possivel abrir uma sessao Snowflake.")
    return s


# ──────────────────────────────────────────────────────────────
# LEITURA
# ──────────────────────────────────────────────────────────────
def listar_referencias() -> list[str]:
    """Referencias carregadas (AAAA-MM), da mais recente para a mais antiga."""
    s = _exigir()
    col = SNOWFLAKE["colunas"]["referencia"]
    df = s.sql(
        f"SELECT DISTINCT {col} AS REF FROM {_nome('tabela_referencias')} ORDER BY REF DESC"
    ).to_pandas()
    return df["REF"].astype(str).tolist()


def referencia_existe(referencia: str) -> bool:
    s = _exigir()
    col = SNOWFLAKE["colunas"]["referencia"]
    df = s.sql(
        f"SELECT COUNT(*) AS N FROM {_nome('tabela_referencias')} WHERE {col} = ?",
        params=[referencia],
    ).to_pandas()
    return int(df["N"].iloc[0]) > 0


def carregar_precos(referencia: str) -> pd.DataFrame:
    """Base longa de uma referencia, nas mesmas colunas de BaseMateriais.longo."""
    s = _exigir()
    c = SNOWFLAKE["colunas"]
    df = s.sql(
        f"""
        SELECT {c['codigo']} AS codigo, {c['descricao']} AS descricao,
               {c['unidade']} AS unidade, {c['uf']} AS uf,
               {c['preco']} AS preco, {c['origem']} AS origem
        FROM {_nome('tabela_precos')}
        WHERE {c['referencia']} = ?
        """,
        params=[referencia],
    ).to_pandas()
    df.columns = [col.lower() for col in df.columns]
    return df


# ──────────────────────────────────────────────────────────────
# CARGA (so pela area de Administracao)
# ──────────────────────────────────────────────────────────────
def inserir_referencia(referencia: str, longo: pd.DataFrame, usuario: str = "") -> int:
    """Grava uma referencia nova. Recusa se ela ja existir. Devolve linhas gravadas.

    A checagem e a gravacao ficam na mesma transacao. A protecao definitiva
    contra duplicidade e a chave/constraint criada no banco pelo Cortex Code;
    aqui e a primeira barreira, na aplicacao.
    """
    s = _exigir()
    c = SNOWFLAKE["colunas"]

    dados = longo.rename(columns={
        "codigo": c["codigo"], "descricao": c["descricao"], "unidade": c["unidade"],
        "uf": c["uf"], "preco": c["preco"], "origem": c["origem"],
    }).copy()
    dados.insert(0, c["referencia"], referencia)

    s.sql("BEGIN").collect()
    try:
        if referencia_existe(referencia):
            raise ReferenciaJaExiste(f"A referencia {referencia} ja esta na base.")
        s.write_pandas(
            dados, SNOWFLAKE["tabela_precos"],
            database=SNOWFLAKE["database"], schema=SNOWFLAKE["schema"],
            auto_create_table=False, overwrite=False,
        )
        s.sql(
            f"INSERT INTO {_nome('tabela_referencias')} ({c['referencia']}, CARREGADO_POR, LINHAS) "
            "SELECT ?, ?, ?",
            params=[referencia, usuario, int(len(dados))],
        ).collect()
        s.sql("COMMIT").collect()
    except Exception:
        s.sql("ROLLBACK").collect()
        raise
    return int(len(dados))
