"""Gera o relatorio Word do Tomo 1 - Materiais a partir do template do DNIT.

O template TEMPLATE_DNIT_Tomo-1_Materiais-SICRO.docx e gerado por
gerar_template_docx.py a partir do Word revisado da referencia anterior. Ele
traz a capa, todos os textos estaticos, as tabelas e as legendas dos 63
graficos na ordem da entrega. Este modulo:

  1. preenche os marcadores {{...}} da capa, dos cabecalhos/rodapes e do
     corpo (referencia atual e anterior, ordinal, numero do relatorio);
  2. escreve, em cada bloco de texto editavel (bookmark TXT_<id>_P<n>), o
     texto decidido pelo analista na tela;
  3. coloca cada grafico conferido no paragrafo de figura que vem logo
     depois da legenda correspondente.

O casamento dos graficos e pela LEGENDA ("Grafico 12 - ..."), nao pela
posicao da imagem no documento: assim um grafico que nao pode ser gerado nao
desloca os demais.

O que este modulo NAO faz ainda: preencher as tabelas. Elas ficam com os
valores do template ate a planilha das tabelas ser mapeada.
"""

from __future__ import annotations

import copy
import os
import re
import shutil
from dataclasses import dataclass, field

from docx.oxml.ns import qn
from docx.shared import Inches

from materiais_catalogo import ESTILO_FIGURA, ESTILO_LEGENDA, ESTILO_LISTA, TEMPLATE
from materiais_charts import figura_para_png

_RE_LEGENDA = re.compile(r"^Gráfico\s+(\d+)\s*[-–]\s*")

# Marcadores do template. A chave e o nome dentro de {{ }}.
MARCADORES_CAPA = (
    "NUM_RELATORIO",
    "REFERENCIA",
    "PROTOCOLO_FGV",
    "MES_ANO_EMISSAO",
    "ANO",
)
MARCADORES_CORPO = (
    "REF_ATUAL_EXTENSO",      # "outubro de 2026"
    "REF_ANTERIOR_EXTENSO",   # "julho de 2026"
    "REF_ATUAL_ARQUIVO",      # "Out.2026", como nos nomes dos arquivos
    "ORDINAL",                # "2" em "2ºRR", "2ºOrigem-Precos"
)
MARCADORES = MARCADORES_CAPA + MARCADORES_CORPO
_RE_MARCADOR = re.compile(r"\{\{([A-Z_]+)\}\}")


@dataclass
class ResultadoRelatorio:
    caminho: str
    graficos_inseridos: list = field(default_factory=list)
    graficos_ausentes: list = field(default_factory=list)
    marcadores_preenchidos: list = field(default_factory=list)
    marcadores_restantes: list = field(default_factory=list)
    blocos_escritos: list = field(default_factory=list)
    blocos_sem_bookmark: list = field(default_factory=list)


# ──────────────────────────────────────────────────────────────
# MARCADORES {{...}}
# ──────────────────────────────────────────────────────────────
def _texto_do_paragrafo(paragrafo) -> str:
    return "".join(t.text or "" for t in paragrafo.iter(qn("w:t")))


def _escrever_no_paragrafo(p, texto: str) -> None:
    """Escreve o texto no primeiro w:t e esvazia os demais.

    Usado quando o marcador esta quebrado em varios runs; o estilo do
    paragrafo sobrevive, a formatacao de caractere dos demais runs nao.
    """
    ts = list(p.iter(qn("w:t")))
    if not ts:
        return
    ts[0].text = texto
    ts[0].set(qn("xml:space"), "preserve")
    for t in ts[1:]:
        t.text = ""


def _substituir_no_paragrafo(p, valores: dict, preenchidos: list, restantes: list) -> None:
    texto = _texto_do_paragrafo(p)
    if "{{" not in texto:
        return

    # 1. run a run, preservando a formatacao de cada run
    for t in p.iter(qn("w:t")):
        if not t.text or "{{" not in t.text:
            continue

        def troca(m):
            chave = m.group(1)
            valor = valores.get(chave)
            if valor:
                preenchidos.append(chave)
                return str(valor)
            restantes.append(chave)
            return m.group(0)

        t.text = _RE_MARCADOR.sub(troca, t.text)

    # 2. marcador partido entre runs: reescreve o paragrafo inteiro
    texto = _texto_do_paragrafo(p)
    if "{{" in texto:
        sobra = set(_RE_MARCADOR.findall(texto))
        novo = texto
        for chave in sobra:
            valor = valores.get(chave)
            if valor:
                novo = novo.replace("{{" + chave + "}}", str(valor))
                preenchidos.append(chave)
            else:
                restantes.append(chave)
        if novo != texto:
            _escrever_no_paragrafo(p, novo)


def _partes_de_cabecalho(documento):
    vistos = set()
    for secao in documento.sections:
        for hf in (secao.header, secao.footer, secao.first_page_header,
                   secao.first_page_footer, secao.even_page_header,
                   secao.even_page_footer):
            parte = hf.part
            if id(parte) in vistos:
                continue
            vistos.add(id(parte))
            yield parte


def preencher_marcadores(documento, valores: dict) -> tuple:
    """Troca {{MARCADOR}} pelo valor em corpo, tabelas, cabecalhos e rodapes.

    Devolve (preenchidos, restantes) com as chaves encontradas.
    """
    preenchidos, restantes = [], []
    for p in documento.element.body.iter(qn("w:p")):
        _substituir_no_paragrafo(p, valores, preenchidos, restantes)
    for parte in _partes_de_cabecalho(documento):
        for p in parte.element.iter(qn("w:p")):
            _substituir_no_paragrafo(p, valores, preenchidos, restantes)
    return preenchidos, restantes


# compatibilidade com o nome antigo
preencher_capa = preencher_marcadores


# ──────────────────────────────────────────────────────────────
# BLOCOS DE TEXTO EDITAVEIS (bookmarks TXT_<id>_P<n>)
# ──────────────────────────────────────────────────────────────
_RE_BOOKMARK = re.compile(r"^TXT_(B\d{3})_P(\d+)$")


def _paragrafos_dos_blocos(documento) -> dict:
    """{id do bloco: [paragrafo xml, ...]} na ordem do documento."""
    blocos: dict = {}
    for p in documento.element.body.iter(qn("w:p")):
        for marca in p.findall(qn("w:bookmarkStart")):
            m = _RE_BOOKMARK.match(marca.get(qn("w:name"), ""))
            if m:
                blocos.setdefault(m.group(1), []).append(p)
    return blocos


def _escrever_texto_no_paragrafo(p, texto: str) -> None:
    """Mantem o primeiro run de texto (com a formatacao) e remove os demais."""
    runs = [r for r in p.findall(qn("w:r")) if r.findall(qn("w:t"))]
    if not runs:
        r = p.makeelement(qn("w:r"), {})
        fim = p.find(qn("w:bookmarkEnd"))
        if fim is not None:
            fim.addprevious(r)
        else:
            p.append(r)
        t = r.makeelement(qn("w:t"), {})
        r.append(t)
        runs = [r]
    for r in runs[1:]:
        p.remove(r)
    ts = runs[0].findall(qn("w:t"))
    ts[0].text = texto
    ts[0].set(qn("xml:space"), "preserve")
    for t in ts[1:]:
        runs[0].remove(t)


def preencher_blocos(documento, textos: dict) -> tuple:
    """Escreve o texto de cada bloco nos paragrafos marcados pelo bookmark.

    `textos` mapeia o id do bloco (B001...) para o texto final; quebras de
    linha separam paragrafos. Sobrando paragrafos no template, sao
    removidos; faltando, o ultimo e duplicado. Devolve (escritos, sem_bookmark).
    """
    por_bloco = _paragrafos_dos_blocos(documento)
    escritos, sem_bookmark = [], []

    for bloco_id, texto in textos.items():
        paragrafos = por_bloco.get(bloco_id)
        if not paragrafos:
            sem_bookmark.append(bloco_id)
            continue
        linhas = [l.strip() for l in (texto or "").split("\n") if l.strip()] or [""]

        while len(paragrafos) < len(linhas):
            clone = copy.deepcopy(paragrafos[-1])
            paragrafos[-1].addnext(clone)
            paragrafos.append(clone)
        for p in paragrafos[len(linhas):]:
            p.getparent().remove(p)
        for p, linha in zip(paragrafos, linhas):
            _escrever_texto_no_paragrafo(p, linha)
        escritos.append(bloco_id)

    return escritos, sem_bookmark


# ──────────────────────────────────────────────────────────────
# FIGURAS
# ──────────────────────────────────────────────────────────────
def _paragrafos_do_corpo(documento):
    from docx.text.paragraph import Paragraph

    for filho in documento.element.body.iterchildren():
        if filho.tag == qn("w:p"):
            yield Paragraph(filho, documento)


def _largura_por_paragrafo(documento) -> dict:
    """Largura util da secao de cada paragrafo do corpo, em polegadas.

    A quebra de secao mora no w:pPr/w:sectPr do ultimo paragrafo da secao;
    a ultima secao mora no w:sectPr do corpo. Importa porque o relatorio
    alterna paginas em retrato e em paisagem.
    """
    secoes = documento.sections
    larguras = []
    for secao in secoes:
        try:
            larguras.append(
                (secao.page_width - secao.left_margin - secao.right_margin) / 914400
            )
        except TypeError:
            larguras.append(6.3)

    mapa, indice = {}, 0
    for paragrafo in _paragrafos_do_corpo(documento):
        mapa[id(paragrafo._p)] = larguras[min(indice, len(larguras) - 1)]
        propriedades = paragrafo._p.find(qn("w:pPr"))
        if propriedades is not None and propriedades.find(qn("w:sectPr")) is not None:
            indice += 1
    return mapa


def _slot_da_figura(paragrafos: list, inicio: int):
    """Paragrafo de figura vazio logo depois da legenda, ou None.

    Duas legendas do template (Graficos 12 e 47) nao tem paragrafo de
    figura; nesse caso quem chama cria um.
    """
    for indice in range(inicio + 1, min(inicio + 4, len(paragrafos))):
        paragrafo = paragrafos[indice]
        if _RE_LEGENDA.match(paragrafo.text.strip()):
            return None
        if paragrafo.style.name == ESTILO_FIGURA and not paragrafo.text.strip():
            return paragrafo
    return None


def _novo_paragrafo_depois(paragrafo, documento):
    from docx.text.paragraph import Paragraph

    elemento = paragrafo._p.makeelement(qn("w:p"), {})
    paragrafo._p.addnext(elemento)
    novo = Paragraph(elemento, documento)
    try:
        novo.style = documento.styles[ESTILO_FIGURA]
    except KeyError:
        pass
    return novo


def _imagem(entrada, dpi: int):
    """Aceita uma figura matplotlib ou um PNG ja pronto."""
    if hasattr(entrada, "savefig"):
        return figura_para_png(entrada, dpi)
    entrada.seek(0)
    return entrada


def inserir_graficos(documento, figuras_por_numero: dict, dpi: int = 200) -> tuple:
    """Coloca cada grafico no slot que segue a sua legenda.

    `figuras_por_numero` mapeia o numero do grafico para uma figura
    matplotlib ou para o PNG ja gerado na conferencia. Devolve
    (inseridos, ausentes).
    """
    larguras = _largura_por_paragrafo(documento)
    paragrafos = [
        p for p in _paragrafos_do_corpo(documento) if p.style.name != ESTILO_LISTA
    ]

    inseridos, vistos = [], set()

    for indice, paragrafo in enumerate(paragrafos):
        if paragrafo.style.name not in ESTILO_LEGENDA:
            continue
        casamento = _RE_LEGENDA.match(paragrafo.text.strip())
        if not casamento:
            continue
        numero = int(casamento.group(1))
        if numero in vistos:
            continue
        vistos.add(numero)

        figura = figuras_por_numero.get(numero)
        if figura is None:
            continue

        slot = _slot_da_figura(paragrafos, indice)
        if slot is None:
            slot = _novo_paragrafo_depois(paragrafo, documento)
            largura = larguras.get(id(paragrafo._p), 6.3)
        else:
            largura = larguras.get(id(slot._p), 6.3)

        for run in slot.runs:
            run.text = ""
        slot.add_run().add_picture(_imagem(figura, dpi), width=Inches(largura))
        inseridos.append(numero)

    ausentes = sorted(set(figuras_por_numero) - set(inseridos))
    return sorted(inseridos), ausentes


# ──────────────────────────────────────────────────────────────
# GERACAO
# ──────────────────────────────────────────────────────────────
def gerar_relatorio(
    figuras_por_numero: dict,
    caminho_saida: str,
    capa: dict = None,
    caminho_template: str = TEMPLATE,
    dpi: int = 200,
    textos: dict = None,
) -> ResultadoRelatorio:
    """Copia o template, preenche marcadores e textos e insere os graficos.

    `capa` traz os valores de todos os marcadores (capa e corpo);
    `textos` traz o texto final de cada bloco editavel, por id.
    """
    from docx import Document

    if not os.path.exists(caminho_template):
        raise FileNotFoundError(f"template não encontrado: {caminho_template}")

    pasta = os.path.dirname(caminho_saida)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    shutil.copyfile(caminho_template, caminho_saida)

    documento = Document(caminho_saida)
    escritos, sem_bookmark = preencher_blocos(documento, textos or {})
    preenchidos, restantes = preencher_marcadores(documento, capa or {})
    inseridos, ausentes = inserir_graficos(documento, figuras_por_numero, dpi)
    documento.save(caminho_saida)

    return ResultadoRelatorio(
        caminho=caminho_saida,
        graficos_inseridos=inseridos,
        graficos_ausentes=ausentes,
        marcadores_preenchidos=sorted(set(preenchidos)),
        marcadores_restantes=sorted(set(restantes)),
        blocos_escritos=escritos,
        blocos_sem_bookmark=sem_bookmark,
    )
