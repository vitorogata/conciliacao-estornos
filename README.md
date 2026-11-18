# Conciliação de estornos de consignado

Conferência automatizada da divergência entre o estorno registrado pelo
sistema e o crédito que aparece no extrato do cliente.

Reconstrucao em Python de uma rotina que eu fazia manualmente em planilha,
contrato por contrato.

## O problema

Quando um estorno de consignado não chega ao cliente, o caso só aparece se
alguém comparar duas bases linha por linha. Com milhares de contratos
por lote, essa comparação não cabe na rotina e o caso passa.

O script faz a comparação e classifica cada contrato em uma categoria fechada,
para que o time trate apenas o que exige ação.

## Dados

Os dados são **sinteticos**. O `gerar_dados.py` cria duas bases com 300
contratos fictícios, com CPF já mascarado no formato `***.456.789-**`.
Nenhum contrato, CPF ou valor real está neste repositório.

## Como rodar

Requer Python 3.11 ou superior.

    pip install -r requirements.txt
    python gerar_dados.py
    python conciliar.py

O `gerar_dados.py` cria `base_estornos.csv` e `extrato.csv`.
O `conciliar.py` imprime o resumo e grava `divergencias.csv` com o detalhe
de cada contrato.

## Categorias

Toda divergência cai em uma destas cinco categorias:

- `CONFORME`: existe crédito de mesmo valor dentro do período analisado
- `VALOR_DIVERGENTE`: existe crédito no período, mas com valor diferente
- `SEM_CREDITO`: nenhum crédito para o contrato
- `DEBITO_NO_LUGAR`: existe lançamento de mesmo valor, mas registrado como débito
- `FORA_DO_PERIODO`: o crédito existe, em data fora da janela analisada

A categoria é fechada de propósito. Motivo inventado não entra em relatório:
quando nenhuma categoria serve, o contrato fica visível para revisão manual em
vez de receber uma classificação plausivel e errada.

## Resultado

Execução com a semente fixa do `gerar_dados.py`, sobre 300 contratos
sintíticos no período de 01/01/2026 a 31/03/2026:

    Registros analisados: 300
    Conformes: 70.3%
    VALOR_DIVERGENTE  31
    SEM_CREDITO       22
    DEBITO_NO_LUGAR   21
    FORA_DO_PERIODO   15

Ou seja, 89 dos 300 contratos exigem verificação manual, e os outros 211
têm crédito de mesmo valor dentro do período.


## Limitações

- Um estorno por contrato. Contratos com mais de um estorno no período não
  são tratados.
- O período é fixo no código (`inicio` e `fim` no `main` do `conciliar.py`).
- A tolerância de comparação é de um centavo.
- Não há leitura de arquivo de retorno da instituição, somente das duas bases.

## Testes

    python -m unittest -v

Sete testes cobrem a máscara de CPF, as cinco categorias de classificação e o
cálculo do percentual de conformidade.

## Arquivos e Funções


- `gerar_dados.py`  cria as duas bases sintéticas 

- `conciliar.py` classifica os contratos e gera o relatório 

- `test_conciliar.py` testes automatizados 

- `requirements.txt` dependência (pandas) 
