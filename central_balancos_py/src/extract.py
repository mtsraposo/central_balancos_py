import json
import logging
import os

import pandas as pd
import requests

from central_balancos_py.src.client.error_handler import ErrorHandler
from central_balancos_py.src.client.http import HttpClient

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

ERROR_MESSAGE = {
    403: 'WAF limit exceeded.',
    409: 'cancelReplace order partially succeeded.',
    418: 'IP auto-banned.',
    429: 'rate limit exceeded.',
    500: 'Internal server error.\n' +
         'It is important to NOT treat this as a failure operation;\n' +
         'the execution status is UNKNOWN and could have been a success.'
}


def handle_http_error(http_err: requests.exceptions.RequestException):
    status_code = http_err.response.status_code
    message = f"HTTP error with status code {status_code}:{ERROR_MESSAGE.get(status_code, '')}"
    logger.error(f'{message}\nError: {http_err}')


PAGE_SIZE = 10000


def url_list(page, page_size, selected_cnpj):
    if selected_cnpj is None:
        return "https://centraldebalancos.estaleiro.serpro.gov.br" \
               "/centralbalancos/servicesapi/api/Participante" \
               f"?page={page}&pageSize={page_size}&orderBy=nome"
    return "https://centraldebalancos.estaleiro.serpro.gov.br" \
           f"/centralbalancos/servicesapi/api/Participante/{selected_cnpj}"


def url_company(company_id, page, page_size):
    return "https://centraldebalancos.estaleiro.serpro.gov.br" \
           "/centralbalancos/servicesapi/api/Demonstracao" \
           f"/{company_id}/0/0?page={page}&pageSize={page_size}"


def url_pdf(company_id):
    return "https://centraldebalancos.estaleiro.serpro.gov.br" \
           f"/centralbalancos/servicesapi/api/Demonstracao/pdf/{company_id}"


def extract_row(statement, cnpj):
    return {
        'nomeParticipante': statement['nomeParticipante'],
        'cnpj': cnpj,
        'tipoDemonstracao': statement['tipoDemonstracao'],
        'status': statement['status'],
        'dataFim': statement['dataFim'],
        'dataPublicacao': statement['dataPublicacao'],
        'pdf': url_pdf(statement['id'])
    }


def fetch_companies(selected_cnpj):
    client = HttpClient(error_handler=ErrorHandler(logger=logger))
    response = client.get(url_list(1, PAGE_SIZE, selected_cnpj))
    if response is None:
        raise requests.HTTPError('Failed to fetch companies')
    return response.json()['items']


def parse_statements(companies):
    rows = []

    for company in companies:
        logger.info(f"--- Extracting {company['nome']}...")
        cnpj = company['cnpj'].replace('[^0-9]', '')

        url = url_company(company['id'], 1, PAGE_SIZE)
        res = requests.get(url)
        statements = json.loads(res.content)['items']

        for statement in statements:
            row = extract_row(statement, cnpj)
            rows.append(row)

    return rows


def transpose(rows):
    transposed = {k: [] for k in rows[0].keys()}
    for row in rows:
        for k, v in row.items():
            transposed[k].append(v)
    return transposed


def to_df(rows):
    transposed_dict = transpose(rows)
    return (pd.DataFrame(data=transposed_dict)
            .astype({'cnpj': 'str'})
            .set_index(['nomeParticipante', 'tipoDemonstracao', 'dataPublicacao'])
            .sort_values(by=['nomeParticipante', 'tipoDemonstracao', 'dataPublicacao']))


def auto_adjust_columns(df, writer, sheet_name):
    worksheet = writer.sheets[sheet_name]
    for idx, col in enumerate(df.reset_index()):
        series = df.reset_index()[col]
        max_len = max((
            series.astype(str).map(len).max(),
            len(str(series.name))
        )) + 1
        worksheet.set_column(idx, idx, max_len)


def to_excel(df, path, sheet_name):
    folder = os.path.join(os.path.dirname(path))
    os.makedirs(folder, exist_ok=True)

    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name)
        auto_adjust_columns(df, writer, sheet_name)


def extract_company_info(worksheet_path, statements_sheet_name, selected_cnpj=None):
    selected_cnpj = None if selected_cnpj is None else int(selected_cnpj)
    companies = fetch_companies(selected_cnpj)
    statements = parse_statements(companies)
    df = to_df(statements)
    to_excel(df, path=worksheet_path, sheet_name=statements_sheet_name)
