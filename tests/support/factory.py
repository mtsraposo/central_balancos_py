import pandas as pd


def company():
    return {'id': 635, 'cnpj': '13385440000156', 'nome': 'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.'}


def statement():
    return {'id': 77820, 'cnpj': '13385440000156',
            'nomeParticipante': 'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.',
            'tipoDemonstracao': 'Demonstrações Contábeis Completas (DCC)', 'categoria': 'DEMONSTRACAODIVERSA',
            'origem': 'Participante-Upload', 'dataInicio': '2022-01-01T00:00:00', 'dataFim': '2022-12-31T00:00:00',
            'statusId': 0, 'status': 'Publicado', 'isPublicada': True, 'consolidada': False,
            'titulo': 'DEMONSTRAÇÕES FINANCEIRAS DE 2022',
            'descricao': 'DEMONSTRAÇÕES FINANCEIRAS REFERENTES AO EXERCÍCIO SOCIAL FINDO EM 31/12/2022',
            'dataPublicacao': '2023-06-21T11:24:32.34', 'dataModificacao': '0001-01-01T00:00:00',
            'dataEnvio': '0001-01-01T00:00:00', 'tipoArquivo': 'PDF', 'ordem': 0, 'htmlXbrl': None, 'qrCode': None,
            'hasAnexos': False, 'assinantes': None, 'podeEditar': False, 'filaProcessamentoId': None,
            'nome1': None, 'nome2': None}


def row(name=None, cnpj=None):
    return {
        'nomeParticipante': name or 'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.',
        'cnpj': cnpj or '13385440000156',
        'tipoDemonstracao': 'Demonstrações Contábeis Completas (DCC)',
        'status': 'Publicado',
        'dataFim': '2022-12-31T00:00:00',
        'dataPublicacao': '2023-06-21T11:24:32.34',
        'pdf': 'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820'
    }

def statement_df():
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
    return expected

def statements_df():
    expected_df = pd.DataFrame({
        'nomeParticipante': ['ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.',
                             'ITATIAIA INVESTIMENTOS IMOBILIARIOS E PARTICIPACOES S.A.',
                             'APPLE'],
        'tipoDemonstracao': ['Demonstrações Contábeis Completas (DCC)',
                             'Balanço Patrimonial (BP)',
                             'Demonstração do Resultado do Exercício (DRE)'],
        'dataPublicacao': ['2019-11-20T22:55:55.627', '2023-06-21T11:24:32.34', '2022-11-20T22:55:55.627'],
        'cnpj': ['13385440000156', '13385440000156', '12345670000890'],
        'status': ['Publicado', 'Publicado', 'Publicado'],
        'dataFim': ['2018-12-31T00:00:00', '2022-12-31T00:00:00', '2022-12-31T00:00:00'],
        'pdf': [
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/3003',
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/77820',
            'https://centraldebalancos.estaleiro.serpro.gov.br/centralbalancos/servicesapi/api/Demonstracao/pdf/0001'
        ]
    })
    expected_df['cnpj'] = expected_df['cnpj'].astype('string')
    return expected_df


__ALL__ = ['company', 'statement', 'row']
