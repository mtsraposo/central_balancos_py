import unittest
from unittest.mock import patch
from central_balancos_py.src import main


class UserInputTests(unittest.TestCase):
    @patch("central_balancos_py.src.main.input")
    def test_prompt_statement_type(self, mock_input):
        mock_input.return_value = '1'
        self.assertEqual('Balanço Patrimonial (BP)', main.prompt_statement_type())

        mock_input.return_value = '2'
        self.assertEqual('Demonstração do Resultado do Exercício (DRE)', main.prompt_statement_type())

        mock_input.return_value = None
        self.assertEqual('', main.prompt_statement_type())
