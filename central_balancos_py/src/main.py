import re
import os

from central_balancos_py.src.extract import extract_company_info
from central_balancos_py.src.pdfs import download_pdfs


def prompt_statement_type():
    user_input = input(f'Would you like to filter by one of these statement types?\n'
                       f'\t1     - Balanço Patrimonial (BP)\n'
                       f'\t2     - Demonstração do Resultado do Exercício (DRE)\n'
                       f'\tEnter - No, download all')
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
                       f'\tEnter - all')
    match user_input:
        case '1':
            return 'latest'
        case '2':
            return 'oldest'
        case _:
            return ''


if __name__ == '__main__':
    statements_sheet_name = 'demonstracoes'
    worksheet_path = os.path.join('data', 'demonstracoes.xlsx')
    pdfs_directory = os.path.join('data', 'pdfs')
    selection = input('================= CENTRAL BALANCOS =================\n\n'
                      'Please choose one of the following options:\n'
                      '\t1 - Extract company statements info\n'
                      '\t2 - Download PDFs\n')
    match selection:
        case '1':
            limit = input('How many companies would you like to extract?\n'
                          'Enter a number or hit Enter to extract all (~8.5k):\n')
            if limit == '':
                extract_company_info(worksheet_path, statements_sheet_name)
            elif re.match('^\d+$', limit):
                extract_company_info(worksheet_path, statements_sheet_name, limit)
            else:
                raise ValueError(f'please input a valid number. "{limit}" provided')
        case '2':
            statement_file_exists = input(
                f"Do you have a worksheet containing statement info "
                f"(generated in option 1 of the previous menu) "
                f"saved in your computer and located at {os.path.join(os.getcwd(), worksheet_path)}? [Y/n] \n")
            if statement_file_exists in ['', 'Y']:
                input(f'Please create a new tab in the statement info worksheet '
                      f"and name it \"cnpjs\". Add the column header \"cnpj\" to cell A1 "
                      f"and fill in the remaining A-column cells with the list of CNPJs "
                      f"you would like to download PDFs from. Hit Enter when you're ready.\n")
                statement_type = prompt_statement_type()
                publish_date = prompt_publish_date()
                print('Downloading PDFs...\n'
                      f'The files will be available at {os.path.join(os.getcwd(), pdfs_directory)} '
                      f'and will follow the naming convention <company_name>_<statement_type>_<publish_date>')
                download_pdfs(pdfs_directory, worksheet_path, statements_sheet_name, statement_type, publish_date)
            else:
                raise KeyError(f'please re-execute the application and select option 1 in the initial menu '
                               f'to generate the financial statement info worksheet and verify that it is saved at '
                               f'{os.path.join(os.getcwd(), worksheet_path)} before proceeding.')

        case _:
            print('please enter a valid option')
