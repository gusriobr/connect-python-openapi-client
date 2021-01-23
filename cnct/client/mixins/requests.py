from json.decoder import JSONDecodeError

import requests
from requests.exceptions import RequestException

from cnct.client.exceptions import ClientError
from cnct.client.utils import get_headers


class RequestsMixin:
    def get(self, url, **kwargs):
        return self.execute('get', url, **kwargs)

    def create(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return self.execute('post', url, **kwargs)

    def update(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return self.execute('put', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.execute('delete', url, **kwargs)

    def execute(self, method, path, **kwargs):
        if (
            self._use_specs
            and self._validate_using_specs
            and not self.specs.exists(method, path)
        ):
            # TODO more info, specs version, method etc
            raise ClientError(f'The path `{path}` does not exist.')

        url = f'{self.endpoint}/{path}'

        kwargs = kwargs or {}
        if 'headers' in kwargs:
            kwargs['headers'].update(get_headers(self.api_key))
        else:
            kwargs['headers'] = get_headers(self.api_key)

        if self.default_headers:
            kwargs['headers'].update(self.default_headers)

        self.response = None

        try:
            self._execute_http_call(method, url, kwargs)
            if self.response.status_code == 204:
                return None
            if self.response.headers['Content-Type'] == 'application/json':
                return self.response.json()
            else:
                return self.response.content

        except RequestException as re:
            api_error = self._get_api_error_details() or {}
            status_code = self.response.status_code if self.response is not None else None
            raise ClientError(status_code=status_code, **api_error) from re

    def _execute_http_call(self, method, url, kwargs):
        self.response = requests.request(method, url, **kwargs)
        if self.response.status_code >= 400:
            self.response.raise_for_status()

    def _get_api_error_details(self):
        if self.response is not None:
            try:
                error = self.response.json()
                if 'error_code' in error and 'errors' in error:
                    return error
            except JSONDecodeError:
                pass
