from unittest.mock import patch

import pytest

from central_balancos_py.src import main

PROJECT_ROOT_PATH = '/Users/example/Downloads/central_balancos_py'


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
