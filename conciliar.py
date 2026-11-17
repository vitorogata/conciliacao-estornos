"""Conciliacao de estornos de consignado.

Compara a base de estornos registrados pelo sistema com os lancamentos do
extrato e classifica cada divergencia em uma categoria fechada.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

TOLERANCIA = 0.01

CATEGORIAS = (
    "CONFORME",
    "VALOR_DIVERGENTE",
    "SEM_CREDITO",
    "DEBITO_NO_LUGAR",
    "FORA_DO_PERIODO",
)


def mascarar_cpf(cpf: str) -> str:
    """Recebe 11 digitos e devolve no formato ***.456.789-**."""
    digitos = "".join(c for c in str(cpf) if c.isdigit())
    if len(digitos) != 11:
        raise ValueError(f"CPF deve ter 11 digitos, recebi {len(digitos)}")
    return f"***.{digitos[3:6]}.{digitos[6:9]}-**"


def classificar_estorno(
    valor_estorno: float,
    lancamentos: list[dict],
    inicio: date,
    fim: date,
) -> tuple[str, str]:
    """Devolve (categoria, motivo) para um unico estorno."""
    creditos = [l for l in lancamentos if l["tipo_lancamento"] == "CREDITO"]
    debitos = [l for l in lancamentos if l["tipo_lancamento"] == "DEBITO"]

    creditos_na_janela = [c for c in creditos if inicio <= c["data"] <= fim]

    for credito in creditos_na_janela:
        if abs(credito["valor"] - valor_estorno) <= TOLERANCIA:
            return "CONFORME", "credito de mesmo valor no periodo"

    if creditos_na_janela:
        credito = creditos_na_janela[0]
        return (
            "VALOR_DIVERGENTE",
            f"estorno de {valor_estorno:.2f} contra credito de {credito['valor']:.2f}",
        )

    if creditos:
        credito = creditos[0]
        return (
            "FORA_DO_PERIODO",
            f"credito existe em {credito['data'].isoformat()}, fora da janela",
        )

    for debito in debitos:
        if abs(debito["valor"] - valor_estorno) <= TOLERANCIA:
            return (
                "DEBITO_NO_LUGAR",
                f"lancamento de {debito['valor']:.2f} registrado como debito",
            )

    return "SEM_CREDITO", "nenhum credito encontrado para o contrato"


def conciliar(
    estornos: pd.DataFrame,
    extrato: pd.DataFrame,
    inicio: date,
    fim: date,
) -> pd.DataFrame:
    """Cruza as duas bases e devolve uma linha por contrato."""
    por_contrato: dict[str, list[dict]] = {}
    for linha in extrato.itertuples(index=False):
        por_contrato.setdefault(linha.id_contrato, []).append(
            {
                "tipo_lancamento": linha.tipo_lancamento,
                "valor": float(linha.valor),
                "data": linha.data.date(),
            }
        )

    registros = []
    for linha in estornos.itertuples(index=False):
        categoria, motivo = classificar_estorno(
            float(linha.valor_estorno),
            por_contrato.get(linha.id_contrato, []),
            inicio,
            fim,
        )
        registros.append(
            {
                "id_contrato": linha.id_contrato,
                "cpf_mascarado": linha.cpf_mascarado,
                "valor_estorno": float(linha.valor_estorno),
                "categoria": categoria,
                "motivo": motivo,
            }
        )

    return pd.DataFrame(
        registros,
        columns=["id_contrato", "cpf_mascarado", "valor_estorno", "categoria", "motivo"],
    )


def resumir(df: pd.DataFrame) -> tuple[float, dict[str, int]]:
    """Devolve o percentual de conformes e a contagem por categoria."""
    total = len(df)
    if total == 0:
        return 0.0, {}
    contagem = df["categoria"].value_counts().to_dict()
    percentual = 100.0 * contagem.get("CONFORME", 0) / total
    return percentual, contagem


def main() -> None:
    inicio = date(2026, 1, 1)
    fim = date(2026, 3, 31)

    estornos = pd.read_csv("base_estornos.csv")
    extrato = pd.read_csv("extrato.csv", parse_dates=["data"])

    resultado = conciliar(estornos, extrato, inicio, fim)
    percentual, contagem = resumir(resultado)

    print(f"Registros analisados: {len(resultado)}")
    print(f"Conformes: {percentual:.1f}%")
    print("Divergencias por categoria:")
    for categoria in CATEGORIAS:
        if categoria == "CONFORME":
            continue
        print(f"  {categoria:<16} {contagem.get(categoria, 0):>4}")

    resultado.to_csv("divergencias.csv", index=False)
    print("Detalhe salvo em divergencias.csv")


if __name__ == "__main__":
    main()