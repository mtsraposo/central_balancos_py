import os

import pandas as pd

from central_balancos_py.src.pdfs import filter_cnpjs


def test_filter_cnpjs():
    worksheet_path = os.path.join(os.getcwd(), 'tests', 'data', 'demonstracoes.xlsx')
    statements_sheet_name = 'demonstracoes'
    saved_df = filter_cnpjs(worksheet_path, statements_sheet_name)

    expected_df = pd.DataFrame({
        'nomeParticipante': ['ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.',
                             'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.'],
        'tipoDemonstracao': ['Demonstrações Contábeis Completas (DCC)', 'Demonstrações Contábeis Completas (DCC)'],
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
