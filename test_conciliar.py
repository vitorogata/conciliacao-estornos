"""Testes da conciliacao de estornos."""

import unittest
from datetime import date

import pandas as pd

from conciliar import classificar_estorno, mascarar_cpf, resumir

INICIO = date(2026, 1, 1)
FIM = date(2026, 3, 31)


class TestMascaraCpf(unittest.TestCase):
    def test_mascara_mantem_apenas_o_meio(self):
        self.assertEqual(mascarar_cpf("12345678901"), "***.456.789-**")


class TestClassificacao(unittest.TestCase):
    def test_conforme(self):
        categoria, _ = classificar_estorno(
            240.00,
            [{"tipo_lancamento": "CREDITO", "valor": 240.00, "data": date(2026, 2, 10)}],
            INICIO,
            FIM,
        )
        self.assertEqual(categoria, "CONFORME")

    def test_valor_divergente(self):
        categoria, _ = classificar_estorno(
            240.00,
            [{"tipo_lancamento": "CREDITO", "valor": 120.00, "data": date(2026, 2, 10)}],
            INICIO,
            FIM,
        )
        self.assertEqual(categoria, "VALOR_DIVERGENTE")

    def test_sem_credito(self):
        categoria, _ = classificar_estorno(240.00, [], INICIO, FIM)
        self.assertEqual(categoria, "SEM_CREDITO")

    def test_debito_no_lugar(self):
        categoria, _ = classificar_estorno(
            240.00,
            [{"tipo_lancamento": "DEBITO", "valor": 240.00, "data": date(2026, 2, 10)}],
            INICIO,
            FIM,
        )
        self.assertEqual(categoria, "DEBITO_NO_LUGAR")

    def test_fora_do_periodo(self):
        categoria, _ = classificar_estorno(
            240.00,
            [{"tipo_lancamento": "CREDITO", "valor": 240.00, "data": date(2026, 5, 20)}],
            INICIO,
            FIM,
        )
        self.assertEqual(categoria, "FORA_DO_PERIODO")


class TestResumo(unittest.TestCase):
    def test_percentual_conforme(self):
        df = pd.DataFrame(
            {"categoria": ["CONFORME", "CONFORME", "SEM_CREDITO", "VALOR_DIVERGENTE"]}
        )
        percentual, contagem = resumir(df)
        self.assertAlmostEqual(percentual, 50.0)
        self.assertEqual(contagem["SEM_CREDITO"], 1)


if __name__ == "__main__":
    unittest.main()