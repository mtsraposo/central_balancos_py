import re
import os
import sys

from extract import extract_company_info
from pdfs import download_pdfs


def prompt_statement_type():
    user_input = input(f'Would you like to filter by one of these statement types?\n'
                       f'\t1     - Balanço Patrimonial (BP)\n'
                       f'\t2     - Demonstração do Resultado do Exercício (DRE)\n'
                       f'\tEnter - No, download all\n')
    match user_input:
        case '1':
            return 'Balanço Patrimonial (BP)'
        case '2':
            return 'Demonstração do Resultado do Exercício (DRE)'
        case _:
            return ''


def prompt_publish_date():
    user_input = input(f'Which publish dates would you like to download?\n'
                       f'\t1     - latest\n'
                       f'\t2     - oldest\n'
                       f'\tEnter - all\n')
    match user_input:
        case '1':
            return 'latest'
        case '2':
            return 'oldest'
        case _:
            return ''


if __name__ == '__main__':
    statements_sheet_name = 'demonstracoes'
    current_dir = os.path.dirname(sys.argv[0])
    worksheet_path = os.path.join(current_dir, 'data', 'demonstracoes.xlsx')
    pdfs_directory = os.path.join(current_dir, 'data', 'pdfs')
    selection = input('================= CENTRAL BALANCOS =================\n\n'
                      'Please choose one of the following options:\n'
                      '\t1 - Extract company statements and generate worksheet\n'
                      '\t2 - Download PDFs\n')
    match selection:
        case '1':
            limit = input('How many companies would you like to extract?\n'
                          'Enter a number or hit Enter to extract all (~8.5k):\n')
            limit = limit if limit != '' else None
            if limit is None or re.match('^\d+$', limit):
                print('Extracting company info...\nThe worksheet will be available at '
                      f'{worksheet_path}.')
                extract_company_info(worksheet_path, statements_sheet_name, limit)
            else:
                raise ValueError(f'please input a valid number. "{limit}" provided')
        case '2':
            statement_file_exists = input(
                f"Do you have a worksheet containing statement info "
                f"(generated in option 1 of the previous menu) "
                f"saved in your computer and located at {worksheet_path}? [Y/n] \n")
            if statement_file_exists in ['', 'Y']:
                input(f'Please create a new tab in the statement info worksheet '
                      f"and name it \"cnpjs\". Add the column header \"cnpj\" to cell A1 "
                      f"and fill in the remaining A-column cells with the list of CNPJs "
                      f"you would like to download PDFs from. Hit Enter when you're ready.\n")
                statement_type = prompt_statement_type()
                publish_date = prompt_publish_date()
                print('Downloading PDFs...\n'
                      f'The files will be available at {pdfs_directory} '
                      f'and will follow the naming convention <company_name>_<statement_type>_<publish_date>')
                download_pdfs(pdfs_directory, worksheet_path, statements_sheet_name, statement_type, publish_date)
            else:
                raise KeyError(f'please re-execute the application and select option 1 in the initial menu '
                               f'to generate the financial statement info worksheet and verify that it is saved at '
                               f'{worksheet_path} before proceeding.')

        case _:
            print('please enter a valid option')
