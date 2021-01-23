from json.decoder import JSONDecodeError

import httpx
from httpx import HTTPError

from cnct.client.exceptions import ClientError
from cnct.client.utils import get_headers


class HttpxMixin:
    async def get(self, url, **kwargs):
        return await self.execute('get', url, **kwargs)

    async def create(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return await self.execute('post', url, **kwargs)

    async def update(self, url, payload=None, **kwargs):
        kwargs = kwargs or {}

        if payload:
            kwargs['json'] = payload

        return await self.execute('put', url, **kwargs)

    async def delete(self, url, **kwargs):
        return await self.execute('delete', url, **kwargs)

    async def execute(self, method, path, **kwargs):
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
            await self._execute_http_call(method, url, kwargs)
            if self.response.status_code == 204:
                return None
            if self.response.headers['Content-Type'] == 'application/json':
                return self.response.json()
            else:
                return self.response.content

        except HTTPError as he:
            api_error = self._get_api_error_details() or {}
            status_code = self.response.status_code if self.response is not None else None
            raise ClientError(status_code=status_code, **api_error) from he

    async def _execute_http_call(self, method, url, kwargs):
        async with httpx.AsyncClient() as client:
            self.response = await client.request(method, url, **kwargs)
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
