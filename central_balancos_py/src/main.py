import re
import os
import sys
import logging

from central_balancos_py.src.extract import extract_company_info
from central_balancos_py.src.pdfs import download_pdfs

green = "\x1b[32m"
reset = "\x1b[0m"
logging.basicConfig(level=logging.INFO,
                    format=f"{green}%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d){reset}")

logger = logging.getLogger(__name__)


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


def is_on_correct_folder(working_directory):
    (dirname, basename) = os.path.split(working_directory)
    return basename == 'central_balancos_py' and os.path.basename(dirname) != 'src'


def resolve_working_directory():
    working_directory = os.getcwd()
    if is_on_correct_folder(working_directory):
        return os.path.join(working_directory, 'central_balancos_py', 'src')
    return os.path.dirname(sys.argv[0])


def config():
    current_dir = resolve_working_directory()
    logger.info(f'Working directory is: {current_dir}')

    worksheet_path = os.path.join(current_dir, 'data', 'demonstracoes.xlsx')
    pdfs_directory = os.path.join(current_dir, 'data', 'pdfs')
    return {
        'statements_sheet_name': 'demonstracoes',
        'worksheet_path': worksheet_path,
        'pdfs_directory': pdfs_directory
    }


def prompt_cnpj():
    selected_cnpj = input(
        'Which company would you like to extract? Please provide a valid CNPJ with only digits\n'
        'Enter a number or hit Enter to extract all (~8.5k):\n'
    )
    selected_cnpj = selected_cnpj if selected_cnpj != '' else None
    valid = selected_cnpj is None or re.match(r'^\d+$', selected_cnpj) is not None
    return selected_cnpj, valid


def maybe_download_pdfs():
    download_now = input(
        '====== Extracted ======\nWould you like to download PDFs for all extracted documents now? [Y/n]')
    if download_now in ['', 'Y']:
        handle_download(env)


def handle_extraction(env):
    selected_cnpj, valid_cnpj = prompt_cnpj()
    if valid_cnpj:
        logger.info('Extracting company info...\nThe worksheet will be available at '
                    f"{env['worksheet_path']}.")
        extract_company_info(
            worksheet_path=env['worksheet_path'],
            statements_sheet_name=env['statements_sheet_name'],
            selected_cnpj=selected_cnpj
        )
        maybe_download_pdfs()
    else:
        raise ValueError(f'please input a valid number. "{selected_cnpj}" provided')


def statement_file_exists(env):
    exists = input(
        f"Do you have a worksheet containing statement info "
        f"(generated in option 1 of the previous menu) "
        f"saved in your computer and located at {env['worksheet_path']}? [Y/n] \n")

    return exists in ['', 'y', 'Y'] and os.path.exists(env['worksheet_path'])


def handle_download(env):
    if statement_file_exists(env):
        input(f'If you would like to download all extracted statements, just hit enter.'
              f'Otherwise, please create a new tab in the statement info worksheet '
              f"and name it \"cnpjs\". Add the column header \"cnpj\" to cell A1 "
              f"and fill in the remaining A-column cells with the list of CNPJs "
              f"you would like to download PDFs from. Hit Enter when you're ready.\n")
        statement_type = prompt_statement_type()
        publish_date = prompt_publish_date()
        logger.info('Downloading PDFs...\n'
                    f"The files will be available at {env['pdfs_directory']} "
                    f'and will follow the naming convention <company_name>_<statement_type>_<publish_date>')
        download_pdfs(pdfs_directory=env['pdfs_directory'],
                      worksheet_path=env['worksheet_path'],
                      statements_sheet_name=env['statements_sheet_name'],
                      statement_type=statement_type,
                      publish_date=publish_date)
    else:
        raise KeyError(f'please re-execute the application and select option 1 in the initial menu '
                       f'to generate the financial statement info worksheet and verify that it is saved at '
                       f"{env['worksheet_path']} before proceeding.")


if __name__ == '__main__':
    env = config()
    selection = input('================= CENTRAL BALANCOS =================\n\n'
                      'Please choose one of the following options:\n'
                      '\t1 - Extract company statements and generate worksheet\n'
                      '\t2 - Download PDFs\n')
    match selection:
        case '1':
            handle_extraction(env)
        case '2':
            handle_download(env)
        case _:
            logger.warning('please enter a valid option (1 or 2)')
