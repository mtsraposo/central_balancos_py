import os
import re

import pandas as pd
import requests


def build_file_name(row):
    company_name = re.sub(r'[^\w\d]', '_', row['nomeParticipante'])
    statement_type = 'BP' if re.match(r'^.*(BP).*$', row['tipoDemonstracao']) else 'DRE'
    published_date = re.match(r'^(.*?)T.*$', row['dataPublicacao'])[1].replace('-', '_')
    return f'{company_name}_{statement_type}_{published_date}.pdf'


def filter_cnpjs(worksheet_path, statements_sheet_name):
    cnpjs = list(pd.read_excel(worksheet_path, sheet_name='cnpjs')['cnpj'].values)
    cnpjs = [re.sub('[^\d]', '', str(cnpj)) for cnpj in cnpjs]

    statements = pd.read_excel(worksheet_path, sheet_name=statements_sheet_name).ffill()
    statements['cnpj'] = statements['cnpj'].astype('string')
    return statements[statements['cnpj'].isin(cnpjs)]


def filter_types(statements, statement_type):
    if statement_type != '':
        return statements[statements['tipoDemonstracao'] == statement_type]
    return statements


def filter_dates(statements, publish_date):
    if publish_date != '':
        statements = statements.sort_values(by=['nomeParticipante', 'tipoDemonstracao', 'dataPublicacao'],
                                            ascending=(publish_date == 'latest'))
        return statements.groupby(by=['nomeParticipante', 'tipoDemonstracao']).tail(1)
    return statements


def filter_statements(worksheet_path, statements_sheet_name, statement_type, publish_date):
    statements = filter_cnpjs(worksheet_path, statements_sheet_name)
    statements = filter_types(statements, statement_type)
    statements = filter_dates(statements, publish_date)
    return statements


def fetch_pdfs(statements, pdfs_directory):
    os.makedirs(pdfs_directory, exist_ok=True)
    for _index, row in statements.iterrows():
        response = requests.get(row['pdf'])
        file_name = build_file_name(row)
        with open(os.path.join(pdfs_directory, file_name), 'wb') as f:
            f.write(response.content)


def download_pdfs(pdfs_directory, worksheet_path, statements_sheet_name, statement_type, publish_date):
    statements = filter_statements(worksheet_path, statements_sheet_name, statement_type, publish_date)
    fetch_pdfs(statements, pdfs_directory)
