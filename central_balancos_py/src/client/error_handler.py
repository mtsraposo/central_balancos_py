import requests


class ErrorHandler:

    def __init__(self, logger):
        self.logger = logger

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as http_err:
                self.logger.error(f"HTTP error with status code {http_err.response.status_code}: {http_err}")
            except requests.exceptions.ConnectionError as conn_err:
                self.logger.error(f'Connection error occurred: {conn_err}')
            except requests.exceptions.Timeout as timeout_err:
                self.logger.error(f'Timeout error occurred: {timeout_err}')
            except requests.exceptions.RequestException as req_err:
                self.logger.error(f'Request error occurred: {req_err}')
            except Exception as e:
                self.logger.error(f'An unexpected error occurred: {e}')

        return wrapper


__ALL__ = ['ErrorHandler']
