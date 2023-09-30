from unittest.mock import patch

import pytest

from central_balancos_py.src import main


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
