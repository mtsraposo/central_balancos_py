import requests
import json
import pandas as pd

PAGE_SIZE = 10000


def url_list(page, page_size):
    return "https://centraldebalancos.estaleiro.serpro.gov.br" \
           "/centralbalancos/servicesapi/api/Participante" \
           f"?page={page}&pageSize={page_size}&orderBy=nome"


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


def transpose(rows):
    transposed = {k: [] for k in rows[0].keys()}
    for row in rows:
        for k, v in row.items():
            transposed[k].append(v)
    return transposed


def get_companies():
    response = requests.get(url_list(1, PAGE_SIZE))
    return json.loads(response.content)['items']


def parse_statements(companies):
    rows = []

    for company in companies[0:100]:
        cnpj = company['cnpj'].replace('[^0-9]', '')

        url = url_company(company['id'], 1, PAGE_SIZE)
        res = requests.get(url)
        statements = json.loads(res.content)['items']

        for statement in statements:
            row = extract_row(statement, cnpj)
            rows.append(row)

    return rows


def to_df(rows):
    transposed_dict = transpose(rows)
    return (pd.DataFrame(data=transposed_dict)
            .set_index(['nomeParticipante', 'tipoDemonstracao', 'dataPublicacao']))


def to_excel(df, filename):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    sheet_name = 'demonstracoes'
    df.to_excel(writer, sheet_name=sheet_name)
    worksheet = writer.sheets[sheet_name]
    for idx, col in enumerate(df.reset_index()):
        series = df.reset_index()[col]
        max_len = max((
            series.astype(str).map(len).max(),
            len(str(series.name))
        )) + 1
        worksheet.set_column(idx, idx, max_len)
    writer.save()


if __name__ == '__main__':
    companies = get_companies()
    statements = parse_statements(companies)
    df = to_df(statements)
    to_excel(df, 'demonstracoes.xlsx')
