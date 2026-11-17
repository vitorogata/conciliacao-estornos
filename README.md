# Conciliacao de estornos de consignado

Conferencia automatizada da divergencia entre o estorno registrado pelo
sistema e o credito que aparece no extrato do cliente.

Reconstrucao em Python de uma rotina que eu fazia manualmente em planilha,
contrato por contrato.

## O problema

Quando um estorno de consignado nao chega ao cliente, o caso so aparece se
alguem comparar duas bases linha por linha. Com algumas centenas de contratos
por lote, essa comparacao nao cabe na rotina e o caso passa.

O script faz a comparacao e classifica cada contrato em uma categoria fechada,
para que o time trate apenas o que exige acao.

## Dados

Os dados sao **sinteticos**. O `gerar_dados.py` cria duas bases com 300
contratos ficticios, com CPF ja mascarado no formato `***.456.789-**`.
Nenhum contrato, CPF ou valor real esta neste repositorio.

## Como rodar

Requer Python 3.11 ou superior.

    pip install -r requirements.txt
    python gerar_dados.py
    python conciliar.py

O `gerar_dados.py` cria `base_estornos.csv` e `extrato.csv`.
O `conciliar.py` imprime o resumo e grava `divergencias.csv` com o detalhe
de cada contrato.

## Categorias

Toda divergencia cai em uma destas cinco categorias:

- `CONFORME`: existe credito de mesmo valor dentro do periodo analisado
- `VALOR_DIVERGENTE`: existe credito no periodo, mas com valor diferente
- `SEM_CREDITO`: nenhum credito para o contrato
- `DEBITO_NO_LUGAR`: existe lancamento de mesmo valor, mas registrado como debito
- `FORA_DO_PERIODO`: o credito existe, em data fora da janela analisada

A categoria e fechada de proposito. Motivo inventado nao entra em relatorio:
quando nenhuma categoria serve, o contrato fica visivel para revisao manual em
vez de receber uma classificacao plausivel e errada.

## Resultado

Execucao com a semente fixa do `gerar_dados.py`, sobre 300 contratos
sinteticos no periodo de 01/01/2026 a 31/03/2026:

    Registros analisados: 300
    Conformes: 70.3%
    VALOR_DIVERGENTE  31
    SEM_CREDITO       22
    DEBITO_NO_LUGAR   21
    FORA_DO_PERIODO   15

Ou seja, 89 dos 300 contratos exigem verificacao manual, e os outros 211
tem credito de mesmo valor dentro do periodo.


## Limitacoes

- Um estorno por contrato. Contratos com mais de um estorno no periodo nao
  sao tratados.
- O periodo e fixo no codigo (`inicio` e `fim` no `main` do `conciliar.py`).
- A tolerancia de comparacao e de um centavo.
- Nao ha leitura de arquivo de retorno da instituicao, so das duas bases.

## Testes

    python -m unittest -v

Sete testes cobrem a mascara de CPF, as cinco categorias de classificacao e o
calculo do percentual de conformidade.

## Arquivos

|
 Arquivo 
|
 Funcao 
|
|
---
|
---
|
|
`gerar_dados.py`
|
 cria as duas bases sinteticas 
|
|
`conciliar.py`
|
 classifica os contratos e gera o relatorio 
|
|
`test_conciliar.py`
|
 testes automatizados 
|
|
`requirements.txt`
|
 dependencia (pandas) 
|