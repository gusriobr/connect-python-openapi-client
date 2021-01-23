from cnct.client.utils import get_values, parse_content_range


class AbstractIterable:
    def __init__(self, client, path, query, config, **kwargs):
        self._client = client
        self._path = path
        self._query = query
        self._config = config
        self._kwargs = kwargs

    def get_item(self, item):
        raise NotImplementedError('get_item must be implemented in subclasses.')

    def __iter__(self):
        cr = None
        results = None
        while cr is None or cr.last < cr.count - 1:
            try:
                results, cr = self._execute_request()
            except StopIteration:
                pass

            if not results:
                return

            for item in results:
                yield self.get_item(item)

            if not cr:
                # endpoint doesn't support pagination
                return
            self._config['params']['offset'] += self._config['params']['limit']

    def _execute_request(self):
        results = self._client.get(
            f'{self._path}?{self._query}',
            **self._config,
        )
        content_range = parse_content_range(
            self._client.response.headers.get('Content-Range'),
        )
        return results, content_range


class AsyncAbstractIterable:
    def __init__(self, client, path, query, config, **kwargs):
        self._client = client
        self._path = path
        self._query = query
        self._config = config
        self._kwargs = kwargs

    def get_item(self, item):
        raise NotImplementedError('get_item must be implemented in subclasses.')

    async def __aiter__(self):
        cr = None
        results = None
        while cr is None or cr.last < cr.count - 1:
            try:
                results, cr = await self._execute_request()
            except StopIteration:
                pass

            if not results:
                return

            for item in results:
                yield self.get_item(item)

            if not cr:
                # endpoint doesn't support pagination
                return
            self._config['params']['offset'] += self._config['params']['limit']

    async def _execute_request(self):
        results = await self._client.get(
            f'{self._path}?{self._query}',
            **self._config,
        )
        self._client.response.headers.get('Content-Range')
        content_range = parse_content_range(
            self._client.response.headers.get('Content-Range'),
        )
        return results, content_range


class ResourceIterable(AbstractIterable):
    def get_item(self, item):
        return item


class AsyncResourceIterable(AsyncAbstractIterable):
    def get_item(self, item):
        return item


class ValuesListIterable(AbstractIterable):
    def get_item(self, item):
        return get_values(item, self._kwargs['fields'])


class AsyncValuesListIterable(AsyncAbstractIterable):
    def get_item(self, item):
        return get_values(item, self._kwargs['fields'])
