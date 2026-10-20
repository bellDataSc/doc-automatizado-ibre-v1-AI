import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from materiais_readers import (ler_resultado_final, ler_origem_precos, cruzar,
                               itens_por_prefixo, distribuicao_origens,
                               itens_zerados, amplitude)

preco = ler_resultado_final("/tmp/fix_resultado_final.xlsx")
origem = ler_origem_precos("/tmp/fix_origem_precos.xlsx")

print("── Resultado Final")
print("  itens:", preco.total_itens, "| UFs:", len(preco.colunas_uf))
print("  titulo:", preco.titulo)
print("  avisos:", preco.avisos or "nenhum")
print("── Origem de Precos")
print("  itens:", origem.total_itens, "| UFs:", len(origem.colunas_uf))
print("  titulo:", origem.titulo)
print("  avisos:", origem.avisos or "nenhum")

base = cruzar(preco, origem)
print("── Cruzamento")
print("  avisos:", base.avisos or "nenhum")
print("  itens de Materiais:", base.total_itens, "| celulas:", base.total_celulas)
assert base.total_celulas == base.total_itens * 27, "celulas != itens x 27"

print("── Itens por prefixo")
print(itens_por_prefixo(preco).to_string(index=False))

print("── Distribuicao de origens (Materiais)")
print(distribuicao_origens(base).to_string(index=False))

z = itens_zerados(base)
print("── Zerados:", len(z), list(z["codigo"]))
assert set(z["codigo"]) == {"M0004", "M0009"}, "zerados errados"

amp = amplitude(base)
com_amp = amp[amp["amplitude_pct"].notna()]
print("── Amplitude: apurada para", len(com_amp), "de", len(amp), "itens")
print(amp[["codigo", "preco_min", "preco_max", "amplitude_pct"]].head(4).to_string(index=False))
esperado = (1 + 26*0.05 - 1) / 1 * 100
print("  esperado p/ item nao zerado: %.4f%%" % esperado)
assert abs(float(com_amp["amplitude_pct"].iloc[0]) - esperado) < 1e-6, "formula de amplitude"
assert set(amp.loc[amp["amplitude_pct"].isna(), "codigo"]) == {"M0004", "M0009"}

print("\nTODAS AS VERIFICACOES PASSARAM")
