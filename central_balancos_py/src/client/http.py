import requests


class HttpClient:
    def __init__(self, error_handler):
        self.error_handler = error_handler

    def get(self, url, params=None):
        decorated_get = self.error_handler(self._get)
        return decorated_get(url, params)

    def _get(self, url, params):
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response


__ALL__ = ['HttpClient']
