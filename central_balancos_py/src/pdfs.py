import os
import re

import pandas as pd
import requests


def replace_with_underscore(to_replace):
    return re.sub(r'\W', '_', to_replace)


def parse_type(full_name):
    return re.match(r'^.*?\((.*?)\).*$', full_name)


def parse_date(full_date):
    return re.match(r'^(.*?)T.*$', full_date)[1].replace('-', '_')


def build_file_name(row):
    company_name = replace_with_underscore(row['nomeParticipante'])
    type_accronym = parse_type(row['tipoDemonstracao'])
    statement_type = replace_with_underscore(row['tipoDemonstracao']).lower() if not type_accronym else type_accronym[1]
    published_date = parse_date(row['dataPublicacao'])
    return f'{company_name}_{statement_type}_{published_date}.pdf'


def filter_cnpjs(worksheet_path, statements_sheet_name):
    statements = pd.read_excel(worksheet_path, sheet_name=statements_sheet_name).ffill()
    statements['cnpj'] = statements['cnpj'].astype('string')
    if 'cnpjs' in pd.ExcelFile(worksheet_path).sheet_names:
        cnpjs = pd.read_excel(worksheet_path, sheet_name='cnpjs')['cnpj'].values.tolist()
        cnpjs = [re.sub('\D', '', str(cnpj)) for cnpj in cnpjs]
        return statements[statements['cnpj'].isin(cnpjs)]
    return statements


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
