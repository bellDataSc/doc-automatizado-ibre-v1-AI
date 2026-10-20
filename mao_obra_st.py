"""Interface da frente Mão de Obra - DNIT - SICRO."""

from dnit_sicro_utils import aviso_pendente, painel_planilhas

TITULO = "Mão de Obra"


def render() -> None:
    arquivos = painel_planilhas("mao_obra", TITULO)
    aviso_pendente(TITULO, arquivos)
