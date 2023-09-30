import os

from tests.constants import PDFS_DIRECTORY


def clean_up_pdf_directory():
    if os.path.exists(PDFS_DIRECTORY):
        pdfs_found = os.listdir(PDFS_DIRECTORY)
        if len(pdfs_found) > 10:
            raise RuntimeError("PDF directory path is likely corrupted. More than 10 files found. Aborting teardown...")
        for file in os.listdir(PDFS_DIRECTORY):
            os.remove(os.path.join(PDFS_DIRECTORY, file))
        os.removedirs(PDFS_DIRECTORY)
