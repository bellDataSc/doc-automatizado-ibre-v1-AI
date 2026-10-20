"""Gera o template .docx e o catalogo de textos a partir do Word revisado.

Uso:
    python gerar_template_docx.py --origem "<Word revisado .docx>" \
        --referencia 2026-07 --anterior 2026-04

Entrada: o relatorio publicado de uma referencia, na versao revisada pela
equipe, em que:
  - AMARELO = texto que muda a cada referencia;
  - ROSA/ROXO = texto que permanece entre referencias;
  - os comentarios dizem o que fazer com cada tabela e grafico.

Saidas:
  1. template/TEMPLATE_DNIT_Tomo-1_Materiais-SICRO.docx
     - todo o texto do relatorio e mantido (o estatico vai assim para o Word);
     - grifos e comentarios removidos;
     - imagens dos graficos removidas (o app insere as novas sob as legendas);
     - datas e nomes de arquivo da referencia trocados por marcadores {{...}};
     - cada bloco de texto editavel recebe um bookmark TXT_<id>, que o
       materiais_writer usa para escrever o texto revisado pelo analista;
     - as TABELAS ficam com os valores da referencia de origem. Elas serao
       sobrescritas quando a planilha das tabelas for mapeada; ate la o app
       avisa que a tabela mantem os valores do template.
  2. materiais/textos/blocos_<referencia>.json
     - o texto de cada bloco editavel, por secao e legenda mais proxima. E o
       "texto da referencia anterior" que a tela mostra ao analista.

Preserva: secoes e sectPr, orientacao e margens, cabecalhos/rodapes, logos,
estilos, numeracao automatica (campos SEQ), sumario e listas (campos TOC),
quebras de pagina e a sequencia de titulos/legendas/Fonte.
"""

import argparse
import json
import os
import re
import shutil
import zipfile
from collections import Counter

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

AQUI = os.path.dirname(os.path.abspath(__file__))
DST_PADRAO = os.path.join(AQUI, "template", "TEMPLATE_DNIT_Tomo-1_Materiais-SICRO.docx")
PASTA_TEXTOS = os.path.join(AQUI, "materiais", "textos")

MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]
MES_ABREV = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# --- estilos de texto de conteudo: candidatos a bloco editavel ---
CONTEUDO = {
    "20_Desenvolvimento-IBRE/SAPR",
    "Desenvolvimento",
    "21_Marcador 1-IBRE/SAPR",
    "37_Citacao-IBRE/SAPR",
    "07_RR-Corpo-Resumo-IBRE/SAPR",
}
# --- estilos que ancoram imagem de grafico: manter paragrafo, remover imagem ---
FIGURA = {"33_Figura-Grafico-IBRE/SAPR", "34_Fonte-Tab-Fig-Graf-IBRE/SAPR"}
# --- estilos da capa/folha de rosto: aplicar marcadores ---
CAPA = {"04_Folha-Rosto-IBRE/SAPR", "03_Detalhes-Capa-IBRE/SAPR"}
TITULOS = ("16_", "17_", "18_", "19_")
LEGENDAS = ("28_Titulo-Tab-Fig-Graf-IBRE/SAPR", "Caption")

# Fracao minima de texto grifado em amarelo para o paragrafo ser EDITAVEL.
# Abaixo disso o amarelo e um campo dentro de texto fixo (data, contagem).
FRACAO_EDITAVEL = 0.6

RE_LEGENDA = re.compile(r"^(Tabela|Gráfico)\s+(\d+)\s*[-–]\s*(.*)$")
stats = Counter()


# ------------------------------------------------------------------ marcadores
def marcadores_da_referencia(ref: str, anterior: str) -> list:
    """Regex -> marcador, derivados das duas referencias (AAAA-MM)."""
    def partes(r):
        ano, mes = r.split("-")
        return int(ano), int(mes)

    a_ano, a_mes = partes(ref)
    p_ano, p_mes = partes(anterior)
    atual_ext = f"{MESES[a_mes - 1]} de {a_ano}"
    ant_ext = f"{MESES[p_mes - 1]} de {p_ano}"
    atual_arq = f"{MES_ABREV[a_mes - 1]}.{a_ano}"
    return [
        # capa, cabecalhos e rodapes
        (re.compile(r"Nº\s*\d{2}-\d{2}/\d{4}"), "Nº {{NUM_RELATORIO}}"),
        (re.compile(r"VDRI\s*/\s*\d+\s*/\s*\d{4}"), "{{PROTOCOLO_FGV}}"),
        (re.compile(r"REFERÊNCIA\s+[A-ZÀ-Ú]+/\d{4}"), "REFERÊNCIA {{REFERENCIA}}"),
        (re.compile(r"Referência\s+[A-ZÀ-Ú][a-zà-ú]+/\d{4}"), "Referência {{REFERENCIA}}"),
        # nomes de arquivo: DNIT_II.09.0_2ºOrigem-Precos-SICRO-Ref-Jul.2026
        (re.compile(r"\d+º(?=RR_|Origem|Resultado|Relatório)"), "{{ORDINAL}}º"),
        (re.compile(r"RR_\d{2}-\d{2}\.\d{4}"), "RR_{{NUM_RELATORIO}}"),
        (re.compile(re.escape(atual_arq)), "{{REF_ATUAL_ARQUIVO}}"),
        # datas por extenso no corpo
        (re.compile(atual_ext, re.IGNORECASE), "{{REF_ATUAL_EXTENSO}}"),
        (re.compile(ant_ext, re.IGNORECASE), "{{REF_ANTERIOR_EXTENSO}}"),
    ]


MARC_EXATO = [
    (re.compile(r"^\s*[A-ZÀ-Ú][a-zà-ú]+ de \d{4}\s*$"), "{{MES_ANO_EMISSAO}}"),
    (re.compile(r"^\s*\d{4}\s*$"), "{{ANO}}"),
]


# ------------------------------------------------------------------ utilidades
def texto_paragrafo(p):
    return "".join(t.text or "" for t in p.iter(qn("w:t")))


def eh_amarelo(r):
    rpr = r.find(qn("w:rPr"))
    if rpr is None:
        return False
    h = rpr.find(qn("w:highlight"))
    return h is not None and h.get(qn("w:val")) == "yellow"


def chars_amarelos(p):
    return sum(len(texto_paragrafo(r)) for r in p.findall(qn("w:r")) if eh_amarelo(r))


def substituir_em_runs(p, regras) -> int:
    """Aplica as regras run a run, preservando a formatacao de cada run."""
    n = 0
    for r in p.findall(qn("w:r")):
        ts = r.findall(qn("w:t"))
        if not ts:
            continue
        txt = "".join(t.text or "" for t in ts)
        novo = txt
        for rx, sub in regras:
            novo = rx.sub(sub, novo)
        if novo != txt:
            ts[0].text = novo
            ts[0].set(qn("xml:space"), "preserve")
            for t in ts[1:]:
                t.text = ""
            n += 1
    return n


def fundir_runs(p):
    """Junta runs vizinhos com a mesma formatacao.

    O Word fragmenta o texto em runs por palavra depois de revisoes; sem a
    fusao, "julho de 2026" fica em tres runs e nenhuma regex o encontra.
    """
    anterior = None
    for r in list(p.findall(qn("w:r"))):
        filhos = [c.tag.split("}")[1] for c in r if c.tag != qn("w:rPr")]
        so_texto = filhos and all(t == "t" for t in filhos)
        rpr = r.find(qn("w:rPr"))
        chave = etree.tostring(rpr) if rpr is not None else b""
        if so_texto and anterior is not None and anterior[1] == chave:
            t_ant = anterior[0].findall(qn("w:t"))[-1]
            t_ant.text = (t_ant.text or "") + "".join(t.text or "" for t in r.findall(qn("w:t")))
            t_ant.set(qn("xml:space"), "preserve")
            p.remove(r)
            continue
        anterior = (r, chave) if so_texto else None


def definir_texto_xml(p, novo):
    ts = list(p.iter(qn("w:t")))
    if not ts:
        return False
    ts[0].text = novo
    ts[0].set(qn("xml:space"), "preserve")
    for t in ts[1:]:
        t.text = ""
    return True


def remover_imagens(p):
    n = 0
    for r in list(p.findall(qn("w:r"))):
        if r.findall(".//" + qn("w:drawing")) or r.findall(".//" + qn("w:pict")):
            p.remove(r)
            n += 1
    return n


def remover_grifos(raiz):
    n = 0
    for h in list(raiz.iter(qn("w:highlight"))):
        h.getparent().remove(h)
        n += 1
    return n


def remover_comentarios(doc):
    """Tira as marcas de comentario do corpo e as partes de comentario do pacote."""
    corpo = doc.element
    n = 0
    for tag in ("w:commentRangeStart", "w:commentRangeEnd"):
        for el in list(corpo.iter(qn(tag))):
            el.getparent().remove(el)
            n += 1
    for ref in list(corpo.iter(qn("w:commentReference"))):
        run = ref.getparent()
        run.getparent().remove(run)
        n += 1
    for rid, rel in list(doc.part.rels.items()):
        if "comments" in rel.reltype:
            del doc.part.rels[rid]
    return n


def bookmark(p, nome: str, bid: int):
    """Envolve o conteudo do paragrafo num bookmark com o nome dado."""
    inicio = OxmlElement("w:bookmarkStart")
    inicio.set(qn("w:id"), str(bid))
    inicio.set(qn("w:name"), nome)
    fim = OxmlElement("w:bookmarkEnd")
    fim.set(qn("w:id"), str(bid))
    ppr = p.find(qn("w:pPr"))
    if ppr is not None:
        ppr.addnext(inicio)
    else:
        p.insert(0, inicio)
    p.append(fim)


# ------------------------------------------------------------------ principal
def gerar(origem: str, destino: str, referencia: str, anterior: str, catalogo: str):
    shutil.copyfile(origem, destino)
    doc = Document(destino)
    body = doc.element.body
    regras = marcadores_da_referencia(referencia, anterior)

    stats["comentarios_removidos"] = remover_comentarios(doc)

    # nome do estilo a partir do w:pStyle (o id dos elementos lxml nao e estavel)
    nome_estilo = {st.style_id: st.name for st in doc.styles}
    padrao = doc.styles.default(1)
    padrao = padrao.name if padrao is not None else "Normal"

    def estilo(p):
        ppr = p.find(qn("w:pPr"))
        ps = ppr.find(qn("w:pStyle")) if ppr is not None else None
        return nome_estilo.get(ps.get(qn("w:val")), padrao) if ps is not None else padrao

    blocos = []          # catalogo de blocos editaveis
    campos = Counter()   # fragmentos amarelos encontrados no texto fixo
    secao, legenda = "", ""
    bloco_aberto = None
    bid = 9000

    for p in body.iterchildren():
        if p.tag != qn("w:p"):
            bloco_aberto = None
            continue
        est = estilo(p)
        fundir_runs(p)
        txt = texto_paragrafo(p)

        if est.startswith(TITULOS):
            secao = txt.strip()
            bloco_aberto = None
        elif est in LEGENDAS and RE_LEGENDA.match(txt.strip()):
            legenda = txt.strip()
            bloco_aberto = None

        if est in FIGURA:
            stats["imagens_removidas"] += remover_imagens(p)
            bloco_aberto = None
            continue

        if est in CAPA:
            novo = txt
            for rx, sub in regras:
                novo = rx.sub(sub, novo)
            for rx, sub in MARC_EXATO:
                if rx.match(novo):
                    novo = sub
            if novo != txt and definir_texto_xml(p, novo):
                stats["capa_marcadores"] += 1
            continue

        amarelo = chars_amarelos(p)
        if amarelo == 0:
            bloco_aberto = None
            continue

        editavel = est in CONTEUDO and amarelo >= FRACAO_EDITAVEL * max(len(txt), 1)
        if not editavel:
            # campo dentro de texto fixo: registrar o fragmento antes de marcar
            for r in p.findall(qn("w:r")):
                if eh_amarelo(r):
                    frag = texto_paragrafo(r).strip()
                    if frag:
                        campos[frag] += 1

        stats["runs_com_marcador"] += substituir_em_runs(p, regras)
        txt = texto_paragrafo(p)

        if not editavel:
            bloco_aberto = None
            continue

        # paragrafos editaveis consecutivos, na mesma secao/legenda, formam um bloco
        if bloco_aberto is None:
            bloco_aberto = {
                "id": f"B{len(blocos) + 1:03d}",
                "secao": secao,
                "legenda": legenda,
                "estilo": est,
                "paragrafos": [],
            }
            blocos.append(bloco_aberto)
        indice = len(bloco_aberto["paragrafos"]) + 1
        bid += 1
        bookmark(p, f"TXT_{bloco_aberto['id']}_P{indice}", bid)
        bloco_aberto["paragrafos"].append(txt)
        stats["paragrafos_editaveis"] += 1

    stats["blocos_editaveis"] = len(blocos)
    stats["grifos_removidos"] = remover_grifos(doc.element)

    # cabecalhos e rodapes: marcadores (texto fica em caixas de texto)
    CAMPO = (qn("w:fldChar"), qn("w:instrText"), qn("w:fldSimple"))
    vistos = set()
    for sec in doc.sections:
        for hf in (sec.header, sec.footer, sec.first_page_header, sec.first_page_footer,
                   sec.even_page_header, sec.even_page_footer):
            parte = hf.part
            if id(parte) in vistos:
                continue
            vistos.add(id(parte))
            stats["grifos_removidos"] += remover_grifos(parte.element)
            for p in parte.element.iter(qn("w:p")):
                if any(p.findall(".//" + tag) for tag in CAMPO):
                    continue
                txt = texto_paragrafo(p)
                if not txt.strip():
                    continue
                novo = txt
                for rx, sub in regras[:4]:
                    novo = rx.sub(sub, novo)
                if novo != txt and definir_texto_xml(p, novo):
                    stats["cabecalho_rodape_marcadores"] += 1

    doc.save(destino)
    stats["midias_orfas_descartadas"], stats["midias_mantidas"] = limpar_midia(destino)

    os.makedirs(os.path.dirname(catalogo), exist_ok=True)
    with open(catalogo, "w", encoding="utf-8") as f:
        json.dump(
            {
                "referencia": referencia,
                "referencia_anterior": anterior,
                "origem": os.path.basename(origem),
                "blocos": blocos,
                "campos_em_texto_fixo": dict(campos.most_common()),
            },
            f, ensure_ascii=False, indent=2,
        )


# ---------- midia orfa ----------
RELS_IMG = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def ids_referenciados(xml_bytes):
    raiz = etree.fromstring(xml_bytes)
    usados = set()
    for el in raiz.iter():
        for attr, val in el.attrib.items():
            if attr.startswith("{" + R_NS + "}") and val:
                usados.add(val)
    return usados


def limpar_midia(caminho):
    """python-docx nao descarta as imagens que deixaram de ser referenciadas."""
    with zipfile.ZipFile(caminho) as z:
        partes = {n: z.read(n) for n in z.namelist()}

    alvos_mantidos = set()
    rels_novos = {}
    for nome, dados in partes.items():
        if not nome.endswith(".rels") or nome == "_rels/.rels":
            continue
        dono = nome.replace("_rels/", "").replace(".rels", "")
        if dono not in partes:
            continue
        usados = ids_referenciados(partes[dono])
        raiz = etree.fromstring(dados)
        mudou = False
        for rel in list(raiz):
            if rel.get("Type") != RELS_IMG:
                continue
            if rel.get("Id") in usados:
                alvos_mantidos.add(rel.get("Target").split("/")[-1])
            else:
                raiz.remove(rel)
                mudou = True
        if mudou:
            rels_novos[nome] = etree.tostring(
                raiz, xml_declaration=True, encoding="UTF-8", standalone=True
            )

    descartadas = [
        n for n in partes
        if n.startswith("word/media/") and n.split("/")[-1] not in alvos_mantidos
    ]
    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, dados in partes.items():
            if nome in descartadas:
                continue
            z.writestr(nome, rels_novos.get(nome, dados))
    return len(descartadas), len(alvos_mantidos)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--origem", required=True, help="Word revisado (.docx) com grifos")
    ap.add_argument("--destino", default=DST_PADRAO)
    ap.add_argument("--referencia", required=True, help="referencia do Word, AAAA-MM")
    ap.add_argument("--anterior", required=True, help="referencia anterior, AAAA-MM")
    ap.add_argument("--catalogo", default=None, help="json de saida dos blocos")
    args = ap.parse_args()
    catalogo = args.catalogo or os.path.join(PASTA_TEXTOS, f"blocos_{args.referencia}.json")

    gerar(args.origem, args.destino, args.referencia, args.anterior, catalogo)

    print("TEMPLATE GERADO:", args.destino)
    print("CATALOGO GERADO:", catalogo)
    for k in sorted(stats):
        print(f"  {k:<32} {stats[k]}")
