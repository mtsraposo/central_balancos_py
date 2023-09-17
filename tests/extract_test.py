import logging
from unittest.mock import patch

import pytest
import requests

from central_balancos_py.src.extract import fetch_companies, url_list


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

    cnpj = 12345670000189
    assert "https://centraldebalancos.estaleiro.serpro.gov.br" \
           f"/centralbalancos/servicesapi/api/Participante/{cnpj}" == url_list(None, None, cnpj)


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
        items = fetch_companies(cnpj)
        assert len(items) == 4
        for item in items:
            assert item.keys() == {'id', 'cnpj', 'nome'}


def test_fetch_companies_success_single():
    cnpj = 13385440000156
    status_code = 200
    json_data = {
        'items': [
            {'id': 635, 'cnpj': '13385440000156', 'nome': 'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.'}
        ],
        'totalCount': 1
    }
    with patch('central_balancos_py.src.extract.requests.get') as mock_get:
        mock_get.return_value = mocked_requests_get(json_data, status_code)
        items = fetch_companies(cnpj)
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
                fetch_companies(cnpj)
                assert f"HTTP error with status code {status_code}:" in caplog.text


def test_extract_company_info():
    pass
