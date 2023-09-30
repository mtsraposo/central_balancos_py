import os
from unittest.mock import patch, Mock

import pytest

from central_balancos_py.src import main
from tests.constants import PDFS_DIRECTORY, PROJECT_ROOT_PATH, SAMPLE_PDF_PATH, WORKSHEET_PATH
from tests.util import clean_up_pdf_directory


@pytest.mark.parametrize(
    "user_input, expected_result",
    [
        ('1', 'Balanço Patrimonial (BP)'),
        ('2', 'Demonstração do Resultado do Exercício (DRE)'),
        (None, ''),
    ]
)
@patch("central_balancos_py.src.main.input")
def test_prompt_statement_type(mock_input, user_input, expected_result):
    mock_input.return_value = user_input
    assert expected_result == main.prompt_statement_type()


@pytest.mark.parametrize(
    "user_input, expected_result",
    [
        ('1', 'latest'),
        ('2', 'oldest'),
        (None, ''),
    ]
)
@patch("central_balancos_py.src.main.input")
def test_prompt_publish_date(mock_input, user_input, expected_result):
    mock_input.return_value = user_input
    assert expected_result == main.prompt_publish_date()


@pytest.mark.parametrize(
    "working_directory, expected_result",
    [
        ('/Users/example/Downloads/central_balancos_py/central_balancos_py', True),
        ('/Users/example/Downloads/central_balancos_py/central_balancos_py/src/central_balancos_py', False),
        ('/Users/example/Downloads/kali.dmg', False)
    ]
)
def test_is_on_correct_folder(working_directory, expected_result):
    assert expected_result == main.is_on_correct_folder(working_directory)


@pytest.mark.parametrize(
    "working_directory, argv, expected_result",
    [
        (PROJECT_ROOT_PATH, ['cmd'], f'{PROJECT_ROOT_PATH}/central_balancos_py/src'),
        (f'{PROJECT_ROOT_PATH}/central_balancos_py/src/central_balancos_py', [PROJECT_ROOT_PATH],
         '/Users/example/Downloads')
    ]
)
@patch("central_balancos_py.src.main.os.getcwd")
@patch("central_balancos_py.src.main.sys.argv")
def test_resolve_working_directory(mock_argv, mock_cwd, argv, working_directory, expected_result):
    mock_argv.__getitem__.side_effect = argv
    mock_cwd.return_value = working_directory

    assert expected_result == main.resolve_working_directory()


@pytest.mark.parametrize(
    "working_directory, argv, expected_result",
    [
        (PROJECT_ROOT_PATH, ['cmd'], {
            'statements_sheet_name': 'demonstracoes',
            'worksheet_path': f'{PROJECT_ROOT_PATH}/central_balancos_py/src/data/demonstracoes.xlsx',
            'pdfs_directory': f'{PROJECT_ROOT_PATH}/central_balancos_py/src/data/pdfs'
        }),
        (f'{PROJECT_ROOT_PATH}/central_balancos_py/src/central_balancos_py', [PROJECT_ROOT_PATH],
         {
             'statements_sheet_name': 'demonstracoes',
             'worksheet_path': '/Users/example/Downloads/data/demonstracoes.xlsx',
             'pdfs_directory': '/Users/example/Downloads/data/pdfs'
         })
    ]
)
@patch("central_balancos_py.src.main.os.getcwd")
@patch("central_balancos_py.src.main.sys.argv")
def test_config(mock_argv, mock_cwd, argv, working_directory, expected_result):
    mock_argv.__getitem__.side_effect = argv
    mock_cwd.return_value = working_directory

    assert expected_result == main.config()


@pytest.mark.parametrize(
    "user_input, expected_result",
    [
        ('12345670000189', ('12345670000189', True)),
        ('', (None, True)),
        ('abc', ('abc', False)),
    ]
)
@patch("central_balancos_py.src.main.input")
def test_prompt_cnpj(mock_input, user_input, expected_result):
    mock_input.return_value = user_input
    assert expected_result == main.prompt_cnpj()


@pytest.mark.parametrize(
    "user_input, env, expected_result",
    [
        ('Y', {'worksheet_path': WORKSHEET_PATH}, True),
        ('Y', {'worksheet_path': ''}, False),
        ('y', {'worksheet_path': WORKSHEET_PATH}, True),
        ('y', {'worksheet_path': ''}, False),
        ('', {'worksheet_path': WORKSHEET_PATH}, True),
        ('', {'worksheet_path': ''}, False),
        ('n', {'worksheet_path': WORKSHEET_PATH}, False),
        ('n', {'worksheet_path': ''}, False),
    ]
)
@patch("central_balancos_py.src.main.input")
def test_statement_file_exists(mock_input, user_input, env, expected_result):
    mock_input.return_value = user_input
    assert expected_result == main.statement_file_exists(env)


@pytest.mark.parametrize(
    "user_input, expected_result",
    [
        ('', None),
        ('a', None)
    ]
)
@patch("central_balancos_py.src.main.input")
def test_prompt_download_instructions(mock_input, user_input, expected_result):
    mock_input.return_value = user_input
    assert expected_result == main.prompt_download_instructions()

@patch("central_balancos_py.src.main.input")
@patch('central_balancos_py.src.pdfs.requests.get')
def test_handle_download(mock_get, mock_input):
    mock_input.return_value = ''
    env = {'worksheet_path': WORKSHEET_PATH,
           'statements_sheet_name': 'demonstracoes',
           'pdfs_directory': PDFS_DIRECTORY}

    with open(SAMPLE_PDF_PATH, 'rb') as file:
        mock_pdf_data = file.read()
    mock_response = Mock()
    mock_response.content = mock_pdf_data
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    main.handle_download(env)
    assert len(os.listdir(PDFS_DIRECTORY)) == 3
    clean_up_pdf_directory()
