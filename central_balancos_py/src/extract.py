import logging
import os
import time

import pandas as pd
import requests

from central_balancos_py.src.client.error_handler import ErrorHandler
from central_balancos_py.src.client.http import HttpClient

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
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


def fetch_companies(http_client, selected_cnpj):
    url = url_list(1, PAGE_SIZE, selected_cnpj)
    response = http_client.get(url)
    if response is None:
        raise requests.HTTPError('Failed to fetch companies')
    return response.json()['items']


def try_parse_statement(company, http_client):
    logger.info(f"--- Extracting {company['nome']}...")

    url = url_company(company['id'], 1, PAGE_SIZE)
    res = http_client.get(url)
    if res is None:
        logger.error(f"Failed to extract {company['nome']}. Queueing for retry.")
        return

    cnpj = company['cnpj'].replace('[^0-9]', '')
    statements = res.json()['items']
    for statement in statements:
        return extract_row(statement, cnpj)


def retry_delay(retry_count):
    return 2 ** retry_count


def maybe_retry_parse(retry_queue, http_client, retry_count):
    should_retry = len(retry_queue) > 0 and retry_count < MAX_RETRIES
    if should_retry:
        delay = retry_delay(retry_count)
        logger.info(f'Retrying parse in {delay} seconds')
        time.sleep(delay)
        return parse_statements(retry_queue, http_client, retry_count + 1)
    return []


def parse_statements(companies, http_client, retry_count=0):
    rows = []
    retry_queue = []

    for company in companies:
        row = try_parse_statement(company, http_client)
        if row is None:
            retry_queue.append(company)
            continue
        rows.append(row)

    recovered = maybe_retry_parse(retry_queue, http_client, retry_count)
    rows.extend(recovered)

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
    http_client = HttpClient(error_handler=ErrorHandler(logger=logger))
    selected_cnpj = None if selected_cnpj is None else int(selected_cnpj)
    companies = fetch_companies(http_client, selected_cnpj)
    statements = parse_statements(companies, http_client)
    df = to_df(statements)
    to_excel(df, path=worksheet_path, sheet_name=statements_sheet_name)
