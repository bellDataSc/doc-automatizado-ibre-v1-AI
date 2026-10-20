"""Gera o relatorio Word do Tomo 1 - Materiais a partir do template do DNIT.

O template TEMPLATE_DNIT_Tomo-1_Materiais-SICRO.docx ja traz a capa, os
titulos, as 63 tabelas e as legendas dos 63 graficos na ordem da entrega.
Este modulo:

  1. preenche os marcadores da capa ({{REFERENCIA}} e os outros quatro);
  2. coloca cada grafico conferido no paragrafo de figura que vem logo
     depois da legenda correspondente.

O casamento e pela LEGENDA ("Grafico 12 - ..."), nao pela posicao da imagem
no documento: assim um grafico que nao pode ser gerado nao desloca os demais.

O que este modulo NAO faz: preencher as tabelas. As 33 tabelas do relatorio
dependem de dados que nao estao nas duas planilhas de entrada (referencia
anterior, classificacao ampla/restrita, familia, lider/liderado, relevantes,
frete, CCU, cotacoes, varejo). Elas ficam como estao no template.
"""

from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass, field

from docx.oxml.ns import qn
from docx.shared import Inches

from materiais_catalogo import ESTILO_FIGURA, ESTILO_LEGENDA, ESTILO_LISTA, TEMPLATE
from materiais_charts import figura_para_png

_RE_LEGENDA = re.compile(r"^Gráfico\s+(\d+)\s*[-–]\s*")

# Marcadores da capa. A chave e o nome dentro de {{ }}.
MARCADORES_CAPA = (
    "NUM_RELATORIO",
    "REFERENCIA",
    "PROTOCOLO_FGV",
    "MES_ANO_EMISSAO",
    "ANO",
)


@dataclass
class ResultadoRelatorio:
    caminho: str
    graficos_inseridos: list = field(default_factory=list)
    graficos_ausentes: list = field(default_factory=list)
    marcadores_preenchidos: list = field(default_factory=list)
    marcadores_restantes: list = field(default_factory=list)


# ──────────────────────────────────────────────────────────────
# CAPA
# ──────────────────────────────────────────────────────────────
def _texto_do_paragrafo(paragrafo) -> str:
    return "".join(run.text for run in paragrafo.runs)


def _escrever_no_paragrafo(paragrafo, texto: str) -> None:
    """Escreve o texto no primeiro run e esvazia os demais.

    Os marcadores da capa podem estar quebrados em varios runs; juntar e
    reescrever e a unica forma segura de substituir sem perder o estilo do
    paragrafo.
    """
    if not paragrafo.runs:
        paragrafo.add_run(texto)
        return
    paragrafo.runs[0].text = texto
    for run in paragrafo.runs[1:]:
        run.text = ""


def preencher_capa(documento, valores: dict) -> tuple:
    """Troca {{MARCADOR}} pelo valor informado. Devolve (preenchidos, restantes)."""
    preenchidos, restantes = [], []

    for paragrafo in documento.paragraphs:
        texto = _texto_do_paragrafo(paragrafo)
        if "{{" not in texto:
            continue
        novo = texto
        for chave in MARCADORES_CAPA:
            marcador = "{{" + chave + "}}"
            if marcador not in novo:
                continue
            valor = valores.get(chave)
            if valor:
                novo = novo.replace(marcador, str(valor))
                preenchidos.append(chave)
            else:
                restantes.append(chave)
        if novo != texto:
            _escrever_no_paragrafo(paragrafo, novo)

    return preenchidos, restantes


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
) -> ResultadoRelatorio:
    """Copia o template, preenche a capa e insere os graficos conferidos."""
    from docx import Document

    if not os.path.exists(caminho_template):
        raise FileNotFoundError(f"template não encontrado: {caminho_template}")

    pasta = os.path.dirname(caminho_saida)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    shutil.copyfile(caminho_template, caminho_saida)

    documento = Document(caminho_saida)
    preenchidos, restantes = preencher_capa(documento, capa or {})
    inseridos, ausentes = inserir_graficos(documento, figuras_por_numero, dpi)
    documento.save(caminho_saida)

    return ResultadoRelatorio(
        caminho=caminho_saida,
        graficos_inseridos=inseridos,
        graficos_ausentes=ausentes,
        marcadores_preenchidos=sorted(set(preenchidos)),
        marcadores_restantes=sorted(set(restantes)),
    )
