import logging
import os
import unittest
from unittest import TestCase
from unittest.mock import patch

import pandas as pd
import pytest

import central_balancos_py.src.pdfs as pdfs
from central_balancos_py.src.client.error_handler import ErrorHandler
from central_balancos_py.src.client.http import HttpClient
from tests.support import factory

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

http_client = HttpClient(error_handler=ErrorHandler(logger=logger))

PDFS_DIRECTORY = os.path.join(os.getcwd(), 'tests', 'data', 'pdfs')


def clean_up_pdf_directory():
    if os.path.exists(PDFS_DIRECTORY):
        pdfs_found = os.listdir(PDFS_DIRECTORY)
        if len(pdfs_found) > 10:
            raise RuntimeError("PDF directory path is likely corrupted. More than 10 files found. Aborting teardown...")
        for file in os.listdir(PDFS_DIRECTORY):
            os.remove(os.path.join(PDFS_DIRECTORY, file))
        os.removedirs(PDFS_DIRECTORY)


@pytest.fixture(scope="session", autouse=True)
def on_exit():
    print("Setting up resources...")
    yield
    print("Tearing down resources...")
    clean_up_pdf_directory()


def test_replace_with_underscore():
    test_cases = {'a': 'a', 'b': 'b', 'a@b': 'a_b', 'a-b': 'a_b', 'a+b': 'a_b', 'a.b': 'a_b'}
    for to_replace, expected in test_cases.items():
        assert expected == pdfs.replace_with_underscore(to_replace)


def test_parse_type():
    statements = {'Demonstrações Contábeis Completas (DCC)': 'DCC',
                  'Balanço Patrimonial (BP)': 'BP'}

    for statement, expected in statements.items():
        assert expected == pdfs.parse_type(statement)[1]


def test_parse_date():
    dates = {'2019-11-20T22:55:55.627': '2019_11_20', '2023-06-21T11:24:32.34': '2023_06_21'}

    for date, expected in dates.items():
        assert expected == pdfs.parse_date(date)


def test_build_file_name():
    row = pd.Series({
        'nomeParticipante': 'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.',
        'tipoDemonstracao': 'Balanço Patrimonial (BP)',
        'dataPublicacao': '2023-06-21T11:24:32.34',
        'cnpj': '13385440000156',
        'status': 'Publicado',
        'dataFim': '2022-12-31T00:00:00',
        'pdf': 'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820'
    })

    assert 'ITATIAIA_INVESTIMENTOS_IMOBILIARIOS_E_PARTICIPACOES_S_A__BP_2023_06_21.pdf' == pdfs.build_file_name(row)


def test_filter_cnpjs_no_filter():
    worksheet_path = os.path.join(os.getcwd(), 'tests', 'data', 'demonstracoes.xlsx')
    statements_sheet_name = 'demonstracoes'
    saved_df = pdfs.filter_cnpjs(worksheet_path, statements_sheet_name)
    expected_df = factory.statements_df()

    assert saved_df.equals(expected_df)


def test_filter_cnpjs():
    worksheet_path = os.path.join(os.getcwd(), 'tests', 'data', 'demonstracoes_filtered.xlsx')
    statements_sheet_name = 'demonstracoes'
    saved_df = pdfs.filter_cnpjs(worksheet_path, statements_sheet_name)

    expected_df = pd.DataFrame({
        'nomeParticipante': ['ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.',
                             'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.'],
        'tipoDemonstracao': ['Demonstrações Contábeis Completas (DCC)',
                             'Balanço Patrimonial (BP)'],
        'dataPublicacao': ['2019-11-20T22:55:55.627', '2023-06-21T11:24:32.34'],
        'cnpj': ['13385440000156', '13385440000156'],
        'status': ['Publicado', 'Publicado'],
        'dataFim': ['2018-12-31T00:00:00', '2022-12-31T00:00:00'],
        'pdf': [
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/3003',
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820'
        ]
    })
    expected_df['cnpj'] = expected_df['cnpj'].astype('string')

    assert saved_df.equals(expected_df)


def test_filter_types():
    statements = factory.statements_df()

    assert statements.equals(pdfs.filter_types(statements, ''))

    expected_df = pd.DataFrame({
        'nomeParticipante': ['ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.'],
        'tipoDemonstracao': ['Balanço Patrimonial (BP)'],
        'dataPublicacao': ['2023-06-21T11:24:32.34'],
        'cnpj': ['13385440000156'],
        'status': ['Publicado'],
        'dataFim': ['2022-12-31T00:00:00'],
        'pdf': [
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820']
    })
    expected_df['cnpj'] = expected_df['cnpj'].astype('string')

    filtered_df = pdfs.filter_types(statements, 'Balanço Patrimonial (BP)').reset_index().drop('index', axis=1)

    assert expected_df.equals(filtered_df)


def test_filter_dates():
    statements = factory.statements_df()

    assert statements.equals(pdfs.filter_dates(statements, ''))

    expected_df = pd.DataFrame({
        'nomeParticipante': ['ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.',
                             'APPLE',
                             'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.'],
        'tipoDemonstracao': ['Demonstrações Contábeis Completas (DCC)',
                             'Demonstração do Resultado do Exercício (DRE)',
                             'Balanço Patrimonial (BP)'],
        'dataPublicacao': ['2019-11-20T22:55:55.627', '2022-11-20T22:55:55.627', '2023-06-21T11:24:32.34'],
        'cnpj': ['13385440000156', '12345670000890', '13385440000156'],
        'status': ['Publicado', 'Publicado', 'Publicado'],
        'dataFim': ['2018-12-31T00:00:00', '2022-12-31T00:00:00', '2022-12-31T00:00:00'],
        'pdf': [
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/3003',
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/0001',
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820',
        ]
    })
    expected_df['cnpj'] = expected_df['cnpj'].astype('string').reset_index(drop=True)

    assert expected_df.equals(pdfs.filter_dates(statements, 'latest').reset_index(drop=True))


def test_filter_statements():
    worksheet_path = os.path.join(os.getcwd(), 'tests', 'data', 'demonstracoes.xlsx')
    statements_sheet_name = 'demonstracoes'

    statements = factory.statements_df()

    assert statements.equals(pdfs.filter_statements(worksheet_path, statements_sheet_name))


class TestPDFEndpoint(TestCase):

    @patch('central_balancos_py.src.pdfs.requests.get')
    def test_fetch_pdf_success(self, mock_get):
        url = 'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820'
        sample_pdf_path = os.path.join(os.getcwd(), 'tests', 'data', 'sample.pdf')

        with open(sample_pdf_path, 'rb') as file:
            mock_pdf_data = file.read()
        mock_response = unittest.mock.Mock()
        mock_response.content = mock_pdf_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        content = pdfs.fetch_pdf(url)

        self.assertEqual(content, mock_pdf_data)

    @patch('central_balancos_py.src.pdfs.requests.get')
    def test_fetch_pdfs(self, mock_get):
        statements = pd.DataFrame({
            'nomeParticipante': ['ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.'],
            'tipoDemonstracao': ['Balanço Patrimonial (BP)'],
            'dataPublicacao': ['2023-06-21T11:24:32.34'],
            'cnpj': ['13385440000156'],
            'status': ['Publicado'],
            'dataFim': ['2022-12-31T00:00:00'],
            'pdf': [
                'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820']
        })
        statements['cnpj'] = statements['cnpj'].astype('string')

        sample_pdf_path = os.path.join(os.getcwd(), 'tests', 'data', 'sample.pdf')
        with open(sample_pdf_path, 'rb') as file:
            mock_pdf_data = file.read()
        mock_response = unittest.mock.Mock()
        mock_response.content = mock_pdf_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        pdfs.fetch_pdfs(statements, PDFS_DIRECTORY)
        assert len(os.listdir(PDFS_DIRECTORY)) == 1
        clean_up_pdf_directory()

    @patch('central_balancos_py.src.pdfs.requests.get')
    def test_download_pdfs(self, mock_get):
        sample_pdf_path = os.path.join(os.getcwd(), 'tests', 'data', 'sample.pdf')
        worksheet_path = os.path.join(os.getcwd(), 'tests', 'data', 'demonstracoes_filtered.xlsx')
        statements_sheet_name = 'demonstracoes'
        statement_type = 'Balanço Patrimonial (BP)'

        with open(sample_pdf_path, 'rb') as file:
            mock_pdf_data = file.read()
        mock_response = unittest.mock.Mock()
        mock_response.content = mock_pdf_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        pdfs.download_pdfs(PDFS_DIRECTORY, worksheet_path, statements_sheet_name, statement_type)
        assert len(os.listdir(PDFS_DIRECTORY)) == 1
        clean_up_pdf_directory()
