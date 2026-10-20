"""Gera duas planilhas sinteticas com o MESMO layout documentado dos arquivos
reais (II.08.0 e II.09.0), para validar os leitores sem ter os arquivos."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openpyxl import Workbook
from materiais_config import UFS

ITENS = []
# 12 materiais, 3 deles zerados em todas as UFs
for i in range(1, 13):
    ITENS.append((f"M{i:04d}", f"Material de teste {i}", "kg" if i % 4 else "Kg"))
for i in range(1, 4):
    ITENS.append((f"E{9000+i}", f"Equipamento de teste {i}", "un"))
ITENS.append(("A9293", "Caminhao plataforma de teste", "un"))
ITENS.append(("P9801", "Ajudante de teste", "h"))

ZERADOS = {"M0004", "M0009"}

def preco_de(codigo, idx_uf):
    if codigo in ZERADOS:
        return 0.0
    base = 100 + int(codigo[1:]) % 50
    return round(base * (1 + idx_uf * 0.05), 4)

def origem_de(codigo, idx_uf):
    if codigo in ZERADOS:
        return "PRZ"
    if codigo.startswith("P"):
        return "SDP" if idx_uf % 3 else "SPC"
    return ["PFM", "PC", "PCI", "PMP", "PRE"][idx_uf % 5]

# ── II.08.0 — cabecalho na linha 4, legenda nas linhas do fim ──────────
wb = Workbook(); ws = wb.active; ws.title = "Resultado Final"
ws["C2"] = "SICRO"; ws["AD2"] = "DNIT"
ws["C3"] = "Resultado Final - Pesquisa Nacional de Precos - Ref.Julho de 2026"
ws.append([])  # placeholder para alinhar; sobrescrito abaixo
for col, valor in enumerate(["CÓDIGO", "DESCRIÇÃO", "UNIDADE"] + UFS, start=1):
    ws.cell(row=4, column=col, value=valor)
linha = 5
for codigo, desc, uni in ITENS:
    ws.cell(row=linha, column=1, value=codigo)
    ws.cell(row=linha, column=2, value=desc)
    ws.cell(row=linha, column=3, value=uni)
    for j, _uf in enumerate(UFS):
        ws.cell(row=linha, column=4 + j, value=preco_de(codigo, j))
    linha += 1
linha += 1
ws.cell(row=linha, column=1, value="Legenda"); ws.cell(row=linha, column=2, value="Precos zerados")
ws.cell(row=linha + 1, column=2, value="Precos sem necessidade de precificacao")
wb.save("/tmp/fix_resultado_final.xlsx")

# ── II.09.0 — cabecalho na linha 5, nomes de coluna DIFERENTES ─────────
wb = Workbook(); ws = wb.active; ws.title = "ENTREGA"
ws["D1"] = "Planilha de Origem Metodologica de Preco - Ref.Julho de 2026"
for col, valor in enumerate(["CÓDIGO", "DESCRIÇÃO DO ITEM", "UNIDADE DO ITEM"] + UFS, start=1):
    ws.cell(row=5, column=col, value=valor)
linha = 6
for codigo, desc, uni in ITENS:
    ws.cell(row=linha, column=1, value=codigo)
    ws.cell(row=linha, column=2, value=desc)
    ws.cell(row=linha, column=3, value=uni)
    for j, _uf in enumerate(UFS):
        ws.cell(row=linha, column=4 + j, value=origem_de(codigo, j))
    linha += 1
linha += 2
ws.cell(row=linha, column=1, value="PRZ - Preco referencial zerado: representa um insumo sem previsao de pesquisa cujo preco referencial e divulgado com valor igual a zero, um paragrafo bem longo que sem filtro viraria uma linha de dados.")
oculta = wb.create_sheet("Tabela RGB utilizada"); oculta["A1"] = "DMT"; oculta.sheet_state = "hidden"
wb.save("/tmp/fix_origem_precos.xlsx")

print("fixtures gerados:", len(ITENS), "itens,", len(UFS), "UFs")
