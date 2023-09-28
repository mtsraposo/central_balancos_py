import logging
import os
from unittest.mock import patch

import pandas as pd
import pytest
import requests

import tests.support.factory as factory
from central_balancos_py.src.client.error_handler import ErrorHandler
from central_balancos_py.src.client.http import HttpClient
from central_balancos_py.src.extract import url_company, url_list, extract_row, try_parse_statement, maybe_retry_parse, \
    parse_statements, transpose, to_df, to_excel, fetch_companies, extract_company_info

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

http_client = HttpClient(error_handler=ErrorHandler(logger=logger))

WORKSHEET_PATH = os.path.join(os.getcwd(), 'demonstracoes.xlsx')

@pytest.fixture(scope="session", autouse=True)
def on_exit():
    print("Setting up resources...")
    yield
    print("Tearing down resources...")
    if os.path.exists(WORKSHEET_PATH):
        os.remove(WORKSHEET_PATH)


class MockResponse(requests.Response):
    def __init__(self, json_data, status_code):
        super().__init__()
        self.json_data = json_data
        self.status_code = status_code

    def json(self, **kwargs):
        return self.json_data


def mocked_requests_get(json_data, status_code):
    return MockResponse(json_data, status_code)


def test_url_list():
    page = 1
    page_size = 100
    assert "https://centraldebalancos.estaleiro.serpro.gov.br" \
           "/centralbalancos/servicesapi/api/Participante" \
           f"?page={page}&pageSize={page_size}&orderBy=nome" == url_list(page, page_size, None)

    cnpj = '12345670000189'
    assert "https://centraldebalancos.estaleiro.serpro.gov.br" \
           f"/centralbalancos/servicesapi/api/Participante/{cnpj}" == url_list(None, None, cnpj)


def test_url_company():
    company_id, page, page_size = 1, 1, 1
    assert "https://centraldebalancos.estaleiro.serpro.gov.br" \
           "/centralbalancos/servicesapi/api/Demonstracao" \
           f"/{company_id}/0/0?page={page}&pageSize={page_size}" == url_company(company_id, page, page_size)


def test_fetch_companies_success_all():
    cnpj = None
    status_code = 200
    json_data = {'items': [{'id': 1141, 'cnpj': '09658732000148', 'nome': '10 M GROUP PARTICIPACOES S/A'},
                           {'id': 4151, 'cnpj': '35763406000100', 'nome': '100% LIVRE S.A.'},
                           {'id': 2311, 'cnpj': '07921278000140', 'nome': '18N PARTICIPACOES S/A'},
                           {'id': 1468, 'cnpj': '19625833000176', 'nome': '1DOC TECNOLOGIA S.A'}],
                 'totalCount': 4}
    with patch('central_balancos_py.src.extract.requests.get') as mock_get:
        mock_get.return_value = mocked_requests_get(json_data, status_code)
        items = fetch_companies(http_client, cnpj)
        assert len(items) == 4
        for item in items:
            assert item.keys() == {'id', 'cnpj', 'nome'}


def test_fetch_companies_success_single():
    cnpj = '13385440000156'
    status_code = 200
    json_data = {
        'items': [
            {'id': 635, 'cnpj': '13385440000156', 'nome': 'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.'}
        ],
        'totalCount': 1
    }
    with patch('central_balancos_py.src.extract.requests.get') as mock_get:
        mock_get.return_value = mocked_requests_get(json_data, status_code)
        items = fetch_companies(http_client, cnpj)
        assert len(items) == 1
        for item in items:
            assert item.keys() == {'id', 'cnpj', 'nome'}


def test_fetch_companies_error(caplog):
    cnpj = None
    status_code = 500
    with caplog.at_level(logging.ERROR):
        with patch('central_balancos_py.src.extract.requests.get') as mock_get:
            mock_get.return_value = mocked_requests_get({}, status_code)
            with pytest.raises(requests.HTTPError) as exception:
                fetch_companies(http_client, cnpj)
                assert f"HTTP error with status code {status_code}:" in caplog.text


def test_extract_row():
    assert factory.row() == extract_row(factory.statement(), '13385440000156')


def test_try_parse_statement_success():
    status_code = 200
    json_data = {
        'items': [factory.statement()],
        'totalCount': 1
    }
    with patch('central_balancos_py.src.extract.requests.get') as mock_get:
        mock_get.return_value = mocked_requests_get(json_data, status_code)
        assert factory.row() == try_parse_statement(factory.company(), http_client)


def test_try_parse_statement_error(caplog):
    fake_company = {'id': -1, 'cnpj': '12345670000890', 'nome': 'FANTASY'}
    status_code = 404
    json_data = {}
    with caplog.at_level(logging.ERROR):
        with patch('central_balancos_py.src.extract.requests.get') as mock_get:
            mock_get.return_value = mocked_requests_get(json_data, status_code)
            assert try_parse_statement(fake_company, http_client) is None
            assert f"Failed to extract" in caplog.text


def test_maybe_retry_parse_noop():
    assert [] == maybe_retry_parse([], http_client, 0)


def test_maybe_retry_parse_execution():
    status_code = 200
    json_data = {
        'items': [factory.statement()],
        'totalCount': 1
    }
    with patch('central_balancos_py.src.extract.requests.get') as mock_get:
        mock_get.return_value = mocked_requests_get(json_data, status_code)
        assert [factory.row()] == maybe_retry_parse([factory.company()], http_client, 0)


def test_parse_statements_success():
    status_code = 200
    json_data = {
        'items': [factory.statement(), factory.statement()],
        'totalCount': 2
    }
    companies = [factory.company(), factory.company()]
    rows = [factory.row(), factory.row()]
    with patch('central_balancos_py.src.extract.requests.get') as mock_get:
        mock_get.return_value = mocked_requests_get(json_data, status_code)
        assert rows == parse_statements(companies, http_client)


def test_parse_statements_success_after_retry():
    state = {'retry_count': 0}

    def try_parse_statement_mock(_company, _client):
        if state['retry_count'] == 0:
            state['retry_count'] += 1
            return None
        return factory.row()

    companies = [factory.company(), factory.company()]
    rows = [factory.row(), factory.row()]
    with patch('central_balancos_py.src.extract.try_parse_statement') as mock_parse, patch(
            'central_balancos_py.src.extract.retry_delay') as mock_delay:
        mock_delay.return_value = 0
        mock_parse.side_effect = try_parse_statement_mock
        assert rows == parse_statements(companies, http_client)


def test_parse_statements_error(caplog):
    status_code = 404
    json_data = {
        'items': [],
        'totalCount': 0
    }
    companies = [factory.company(), factory.company()]
    rows = []
    with caplog.at_level(logging.INFO):
        with patch('central_balancos_py.src.extract.requests.get') as mock_get, patch(
                'central_balancos_py.src.extract.retry_delay') as mock_delay:
            mock_get.return_value = mocked_requests_get(json_data, status_code)
            mock_delay.return_value = 0
            assert rows == parse_statements(companies, http_client)
            assert f"Retrying parse" in caplog.text


def test_transpose():
    rows = [factory.row('Google', '12345670000890'), factory.row('Apple', '23456700008901')]
    assert {
               'nomeParticipante': ['Google', 'Apple'],
               'cnpj': ['12345670000890', '23456700008901'],
               'tipoDemonstracao': ['Demonstrações Contábeis Completas (DCC)',
                                    'Demonstrações Contábeis Completas (DCC)'],
               'status': ['Publicado', 'Publicado'],
               'dataFim': ['2022-12-31T00:00:00', '2022-12-31T00:00:00'],
               'dataPublicacao': ['2023-06-21T11:24:32.34', '2023-06-21T11:24:32.34'],
               'pdf': [
                   'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820',
                   'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820']
           } == transpose(rows)


def test_to_df():
    rows = [factory.row('Google', '12345670000890'), factory.row('Apple', '23456700008901')]
    expected = pd.DataFrame({
        'nomeParticipante': ['Apple', 'Google'],
        'tipoDemonstracao': ['Demonstrações Contábeis Completas (DCC)',
                             'Demonstrações Contábeis Completas (DCC)'],
        'dataPublicacao': ['2023-06-21T11:24:32.34', '2023-06-21T11:24:32.34'],
        'cnpj': ['23456700008901', '12345670000890'],
        'status': ['Publicado', 'Publicado'],
        'dataFim': ['2022-12-31T00:00:00', '2022-12-31T00:00:00'],
        'pdf': [
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820',
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820']
    }).set_index(['nomeParticipante', 'tipoDemonstracao', 'dataPublicacao'])
    assert expected.equals(to_df(rows))


def test_to_excel():
    rows = [factory.row('Google', '12345670000890'), factory.row('Apple', '23456700008901')]
    df = to_df(rows)
    sheet_name = 'demonstracoes'

    to_excel(df, WORKSHEET_PATH, sheet_name)

    saved = pd.read_excel(WORKSHEET_PATH, sheet_name=sheet_name)
    saved['cnpj'] = saved['cnpj'].astype('string')
    expected = df.reset_index()
    expected['cnpj'] = saved['cnpj'].astype('string')

    assert saved.equals(expected)

    os.remove(WORKSHEET_PATH)


def test_extract_company_info():
    status_code = 200
    companies_json_data = {
        'items': [
            {'id': 635, 'cnpj': '13385440000156', 'nome': 'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.'}
        ],
        'totalCount': 1
    }
    statements_json_data = {
        'items': [factory.statement()],
        'totalCount': 1
    }

    def multi_mock_requests_get(url, **_kwargs):
        if 'Participante' in url:
            return mocked_requests_get(companies_json_data, status_code)
        return mocked_requests_get(statements_json_data, status_code)

    expected = pd.DataFrame({
        'nomeParticipante': ['ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.'],
        'tipoDemonstracao': ['Demonstrações Contábeis Completas (DCC)'],
        'dataPublicacao': ['2023-06-21T11:24:32.34'],
        'cnpj': ['13385440000156'],
        'status': ['Publicado'],
        'dataFim': ['2022-12-31T00:00:00'],
        'pdf': [
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820'
        ]
    })
    expected['cnpj'] = expected['cnpj'].astype('string')

    with patch('central_balancos_py.src.extract.requests.get') as mock_get:
        mock_get.side_effect = multi_mock_requests_get

        sheet_name = 'demonstracoes'
        extract_company_info(WORKSHEET_PATH, sheet_name)

        saved = pd.read_excel(WORKSHEET_PATH, sheet_name=sheet_name)
        saved['cnpj'] = saved['cnpj'].astype('string')

        assert saved.equals(expected)

    os.remove(WORKSHEET_PATH)
