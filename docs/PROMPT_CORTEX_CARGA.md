# Prompt para o Cortex Code: base histórica do SICRO (Materiais)

Copie o bloco abaixo no Cortex Code, no ambiente Snowflake onde o app vai rodar, com as planilhas disponíveis num stage ou na pasta de trabalho. Rode em duas rodadas: primeiro as referências históricas (fase A); depois, quando a planilha das tabelas estiver mapeada, a fase B.

Ao final, cole aqui a resposta dele (nomes finais de schema, tabelas, colunas, tipos e chaves) para eu preencher `dnit_sicro_config.SNOWFLAKE`.

---

```
Você vai estruturar a base histórica das referências do SICRO (contrato DNIT, FGV IBRE) para um app Streamlit in Snowflake. Trabalhe em etapas e NÃO crie nem altere nada antes de concluir a etapa 1 e me mostrar o resultado.

## Regras fixas
- Toda linha gravada carrega a REFERÊNCIA a que pertence, no formato AAAA-MM (ex.: 2026-07). A referência é a chave de tudo.
- Uma referência nunca é gravada duas vezes. Antes de qualquer carga, verifique se ela já existe; se existir, pare e me avise. Não use CREATE OR REPLACE nem TRUNCATE em tabela que já tenha dados.
- Não invente colunas, regras ou classificações. O que não estiver nos arquivos fica de fora e você me pergunta.
- Preserve os códigos dos insumos como texto (M0003, E0123...), os preços com 4 casas decimais e a sigla de origem como texto.
- Ao terminar, devolva um resumo com os NOMES FINAIS de database, schema, tabelas, colunas, tipos, chaves/constraints e contagens por referência. Esse resumo é o que o app vai usar.

## Etapa 1: inspecionar (sem criar nada)
1. Liste o que já existe na conta que possa servir: databases/schemas com "SICRO", "SAPR", "DNIT", "IBRE" ou "REFERENCIA" no nome; tabelas com colunas de código de insumo, UF e preço; stages com planilhas. Me diga se já há uma base histórica que deva ser reaproveitada em vez de criar outra.
2. Abra cada planilha disponível e descreva: nome do arquivo, abas, linha de cabeçalho, colunas, nº de linhas, e de qual referência ela é (pelo nome do arquivo e pelo título interno). Os arquivos de entrega de cada referência são:
   - DNIT_II.08.0_<n>ºResultado-Final-SICRO-Ref-<Mes>.<Ano>.xlsx: aba "Resultado Final", cabeçalho na linha 4; colunas CÓDIGO, DESCRIÇÃO, UNIDADE e 27 colunas de UF com o preço.
   - DNIT_II.09.0_<n>ºOrigem-Precos-SICRO-Ref-<Mes>.<Ano>.xlsx: aba "ENTREGA", cabeçalho na linha 5; mesmas colunas, com a sigla de origem do preço em vez do valor; legenda das siglas no rodapé.
   - DNIT_II.10.0 (descrições e fatores) e DNIT_II.11.0 (relação líder-liderado, aba "Liderança_SICROBR", cabeçalho na linha 5), quando existirem.
   Se o layout de alguma referência diferir, me mostre a diferença antes de seguir.
3. Confira, por referência, se o II.08.0 e o II.09.0 têm os mesmos códigos na mesma ordem e as mesmas 27 UFs. Reporte divergências.
4. Me apresente a proposta de estrutura (nomes de schema, tabelas, colunas, tipos, chaves) e espere meu OK.

## Etapa 2: criar a estrutura (depois do meu OK)
Proposta de partida, ajuste ao que encontrou na etapa 1:
- Um schema próprio para o projeto (sugestão: SICRO_RELATORIOS, ou um schema novo no database que o AGENTE SAPR já usa, se existir).
- Tabela de controle, 1 linha por referência: REFERENCIA (AAAA-MM, chave primária), DATA_CARGA, CARREGADO_POR, ARQUIVOS_ORIGEM, LINHAS. Crie a chave primária/unicidade em REFERENCIA.
- Tabela de preços em formato longo, 1 linha por (REFERENCIA, CODIGO, UF): REFERENCIA, CODIGO, DESCRICAO, UNIDADE, UF, PRECO NUMBER(18,4), ORIGEM (sigla). Chave (REFERENCIA, CODIGO, UF). Cerca de 2.395 códigos × 27 UFs = ~64.665 linhas por referência.
- Tabela de liderança, 1 linha por (REFERENCIA, CODIGO): CODIGO_LIDER, PAPEL (líder/liderado), quando o II.11.0 existir.
- Tabela de dimensão de UF (UF, REGIAO, ORDEM) na ordem das colunas das planilhas: Norte (AC, AM, AP, PA, RO, RR, TO), Nordeste (AL, BA, CE, MA, PB, PE, PI, RN, SE), Sudeste (ES, MG, RJ, SP), Sul (PR, RS, SC), Centro-Oeste (DF, GO, MS, MT). Confirme a ordem com as planilhas.
- Tabela das siglas de origem com a descrição oficial do rodapé do II.09.0.
- Uma stored procedure de carga que recebe a referência, confere se ela já existe na tabela de controle, e só então insere preços (+ liderança) e a linha de controle, tudo na mesma transação. Se a referência existir, a procedure falha sem gravar nada. A role do app grava somente por essa procedure.

## Etapa 3: carregar as referências históricas
- Carregue cada referência disponível pela procedure, da mais antiga para a mais recente. Tente carregar uma referência repetida de propósito e me mostre que ela foi recusada.
- Para cada referência, reporte: nº de códigos, nº de UFs, nº de linhas, nº de células com ORIGEM = 'PRZ' e quantas delas têm PRECO = 0 (devem ser iguais). Para 2026-07 o esperado é 2.395 códigos, 27 UFs e 68 itens de Materiais com PRZ em todas as UFs.
- Crie uma view com a variação entre referências consecutivas por (CODIGO, UF): PRECO atual ÷ PRECO anterior − 1, só quando há preço nas duas.

## Etapa 4 (fase B, só quando eu enviar): planilha das tabelas do relatório
Quando eu enviar a planilha "02_GRAFICOS-E-TABELAS", NÃO carregue ainda. Primeiro: liste cada aba, o cabeçalho, as colunas e as fórmulas que ela usa, e me diga quais abas podem ser recalculadas a partir da tabela de preços e quais trazem dados que não existem na base (frete, varejo, cotações, listas fixas). Só depois do meu OK crie as tabelas correspondentes, sempre com a coluna REFERENCIA e a mesma regra de não duplicar.

## Ao final de cada etapa
Devolva, em texto, os nomes finais (database.schema.tabela), as colunas com tipo, as chaves e as contagens. Não resuma com "criado com sucesso": eu preciso dos nomes exatos para configurar o aplicativo.
```
