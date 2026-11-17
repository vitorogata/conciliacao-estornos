"""Gera duas bases sinteticas para a conciliacao de estornos de consignado.

base_estornos.csv -> o que o sistema registrou como estornado
extrato.csv       -> o que apareceu no extrato do cliente

Nenhum dado real. O CPF e ficticio e ja sai mascarado.
"""

import random
from datetime import date, timedelta

import pandas as pd

from conciliar import mascarar_cpf

SEMENTE = 42
QTD_CONTRATOS = 300
INICIO = date(2026, 1, 1)
FIM = date(2026, 3, 31)
VALORES_BASE = (120.00, 185.50, 240.00, 310.75, 455.20)

CENARIOS = (
    ["CONFORME"] * 70
    + ["VALOR_DIVERGENTE"] * 10
    + ["SEM_CREDITO"] * 8
    + ["DEBITO_NO_LUGAR"] * 6
    + ["FORA_DO_PERIODO"] * 6
)


def _credito(id_contrato: str, valor: float, data: date) -> dict:
    return {
        "id_contrato": id_contrato,
        "tipo_lancamento": "CREDITO",
        "valor": valor,
        "data": data.isoformat(),
    }


def _debito(id_contrato: str, valor: float, data: date) -> dict:
    return {
        "id_contrato": id_contrato,
        "tipo_lancamento": "DEBITO",
        "valor": valor,
        "data": data.isoformat(),
    }


def main() -> None:
    random.seed(SEMENTE)
    estornos = []
    lancamentos = []
    dias_no_periodo = (FIM - INICIO).days

    for numero in range(1, QTD_CONTRATOS + 1):
        id_contrato = f"CT{INICIO.year}{numero:04d}"
        cpf = "".join(str(random.randint(0, 9)) for _ in range(11))
        valor = round(random.choice(VALORES_BASE) * random.randint(1, 3), 2)
        data_estorno = INICIO + timedelta(days=random.randint(0, dias_no_periodo))

        estornos.append(
            {
                "id_contrato": id_contrato,
                "cpf_mascarado": mascarar_cpf(cpf),
                "valor_estorno": valor,
                "data_estorno": data_estorno.isoformat(),
            }
        )

        cenario = random.choice(CENARIOS)

        if cenario == "CONFORME":
            lancamentos.append(_credito(id_contrato, valor, data_estorno))
        elif cenario == "VALOR_DIVERGENTE":
            valor_errado = round(valor * random.uniform(0.5, 0.9), 2)
            lancamentos.append(_credito(id_contrato, valor_errado, data_estorno))
        elif cenario == "DEBITO_NO_LUGAR":
            lancamentos.append(_debito(id_contrato, valor, data_estorno))
        elif cenario == "FORA_DO_PERIODO":
            data_fora = FIM + timedelta(days=random.randint(30, 60))
            lancamentos.append(_credito(id_contrato, valor, data_fora))

    pd.DataFrame(estornos).to_csv("base_estornos.csv", index=False)
    pd.DataFrame(lancamentos).to_csv("extrato.csv", index=False)

    print(f"base_estornos.csv: {len(estornos)} registros")
    print(f"extrato.csv: {len(lancamentos)} lancamentos")


if __name__ == "__main__":
    main()