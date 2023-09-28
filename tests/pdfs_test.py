import os

import pandas as pd

from tests.support import factory

from central_balancos_py.src.pdfs import filter_cnpjs, filter_types, filter_dates


def test_filter_cnpjs_no_filter():
    worksheet_path = os.path.join(os.getcwd(), 'tests', 'data', 'demonstracoes.xlsx')
    statements_sheet_name = 'demonstracoes'
    saved_df = filter_cnpjs(worksheet_path, statements_sheet_name)
    expected_df = factory.statements_df()

    assert saved_df.equals(expected_df)


def test_filter_cnpjs():
    worksheet_path = os.path.join(os.getcwd(), 'tests', 'data', 'demonstracoes_filtered.xlsx')
    statements_sheet_name = 'demonstracoes'
    saved_df = filter_cnpjs(worksheet_path, statements_sheet_name)

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

    assert statements.equals(filter_types(statements, ''))

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

    filtered_df = filter_types(statements, 'Balanço Patrimonial (BP)').reset_index().drop('index', axis=1)

    assert expected_df.equals(filtered_df)


def test_filter_dates():
    statements = factory.statements_df()

    assert statements.equals(filter_dates(statements, ''))

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

    assert expected_df.equals(filter_dates(statements, 'latest').reset_index(drop=True))
