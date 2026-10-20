"""Interface da frente Equipamentos - DNIT - SICRO."""

from dnit_sicro_utils import aviso_pendente, painel_planilhas

TITULO = "Equipamentos"


def render() -> None:
    arquivos = painel_planilhas("equipamentos", TITULO)
    aviso_pendente(TITULO, arquivos)
