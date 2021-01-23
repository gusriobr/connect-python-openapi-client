import pytest

import responses

from cnct.client.exceptions import ClientError
from cnct.client.fluent import AsyncConnectClient, ConnectClient
from cnct.client.models import AsyncCollection, AsyncNS, Collection, NS


@pytest.mark.parametrize('clazz', (AsyncConnectClient, ConnectClient))
def test_default_headers(clazz):
    c = clazz(
        'Api Key',
        use_specs=False,
        default_headers={'X-Custom-Header': 'value'},
    )

    assert c.default_headers == {'X-Custom-Header': 'value'}


@pytest.mark.parametrize('clazz', (AsyncConnectClient, ConnectClient))
def test_default_headers_invalid(clazz):
    with pytest.raises(ValueError):
        clazz(
            'Api Key',
            use_specs=False,
            default_headers={'Authorization': 'value'},
        )


@pytest.mark.parametrize(
    ('client_clazz', 'expected_collection_model'),
    (
        (AsyncConnectClient, AsyncCollection),
        (ConnectClient, Collection),
    ),
)
def test_getattr(client_clazz, expected_collection_model):
    c = client_clazz('Api Key', use_specs=False)
    res = c.products
    assert isinstance(res, expected_collection_model)
    assert res.path == 'products'


@pytest.mark.parametrize(
    ('client_clazz', 'expected_collection_model'),
    (
        (AsyncConnectClient, AsyncCollection),
        (ConnectClient, Collection),
    ),
)
def test_getattr_with_dash(client_clazz, expected_collection_model):

    c = client_clazz('Api Key', use_specs=False)

    assert isinstance(c.my_resources, expected_collection_model)
    assert c.my_resources.path == 'my-resources'


@pytest.mark.parametrize(
    ('client_clazz', 'expected_ns_model'),
    (
        (AsyncConnectClient, AsyncNS),
        (ConnectClient, NS),
    ),
)
def test_ns(client_clazz, expected_ns_model):
    c = client_clazz('Api Key', use_specs=False)

    assert isinstance(c.ns('namespace'), expected_ns_model)
    assert c.ns('namespace').path == 'namespace'


@pytest.mark.parametrize('clazz', (AsyncConnectClient, ConnectClient))
def test_ns_invalid_type(clazz):
    c = clazz('Api Key', use_specs=False)
    with pytest.raises(TypeError):
        c.ns(c)


@pytest.mark.parametrize('clazz', (AsyncConnectClient, ConnectClient))
def test_ns_invalid_value(clazz):
    c = clazz('Api Key', use_specs=False)
    with pytest.raises(ValueError):
        c.ns('')


@pytest.mark.parametrize(
    ('client_clazz', 'expected_collection_model'),
    (
        (AsyncConnectClient, AsyncCollection),
        (ConnectClient, Collection),
    ),
)
def test_collection(client_clazz, expected_collection_model):
    c = client_clazz('Api Key', use_specs=False)

    assert isinstance(c.collection('resources'), expected_collection_model)
    assert c.collection('resources').path == 'resources'


@pytest.mark.parametrize('clazz', (AsyncConnectClient, ConnectClient))
def test_collection_invalid_type(clazz):
    c = clazz('Api Key', use_specs=False)
    with pytest.raises(TypeError):
        c.collection(c)


@pytest.mark.parametrize('clazz', (AsyncConnectClient, ConnectClient))
def test_collection_invalid_value(clazz):
    c = clazz('Api Key', use_specs=False)
    with pytest.raises(ValueError):
        c.collection('')


def test_get(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectClient('API_KEY', use_specs=False)

    c.get(url, **kwargs)

    assert mocked.called_once_with('get', url, 200, **kwargs)


@pytest.mark.asyncio
async def test_async_get(async_mocker):
    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }
    with async_mocker.patch.object(AsyncConnectClient, 'execute') as mocked:
        c = AsyncConnectClient('API_KEY', use_specs=False)
        await c.get(url, **kwargs)
    mocked.assert_awaited_once_with('get', url, **kwargs)


def test_create(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'
    payload = {
        'k1': 'v1',
    }
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectClient('API_KEY', use_specs=False)

    c.create(url, payload=payload, **kwargs)

    mocked.assert_called_once_with('post', url, **{
        'arg1': 'val1',
        'json': {
            'k1': 'v1',
        },
    })


@pytest.mark.asyncio
async def test_async_create(async_mocker):

    url = 'https://localhost'
    payload = {
        'k1': 'v1',
    }
    kwargs = {
        'arg1': 'val1',
    }

    with async_mocker.patch.object(AsyncConnectClient, 'execute') as mocked:
        c = AsyncConnectClient('API_KEY', use_specs=False)
        await c.create(url, payload=payload, **kwargs)

    mocked.assert_awaited_once_with('post', url, **{
        'arg1': 'val1',
        'json': {
            'k1': 'v1',
        },
    })


def test_update(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'
    payload = {
        'k1': 'v1',
    }
    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectClient('API_KEY', use_specs=False)

    c.update(url, payload=payload, **kwargs)

    mocked.assert_called_once_with('put', url, **{
        'arg1': 'val1',
        'json': {
            'k1': 'v1',
        },
    })


@pytest.mark.asyncio
async def test_async_update(async_mocker):

    url = 'https://localhost'
    payload = {
        'k1': 'v1',
    }
    kwargs = {
        'arg1': 'val1',
    }

    with async_mocker.patch.object(AsyncConnectClient, 'execute') as mocked:
        c = AsyncConnectClient('API_KEY', use_specs=False)
        await c.update(url, payload=payload, **kwargs)

    mocked.assert_awaited_once_with('put', url, **{
        'arg1': 'val1',
        'json': {
            'k1': 'v1',
        },
    })


def test_delete(mocker):
    mocked = mocker.patch.object(ConnectClient, 'execute')
    url = 'https://localhost'

    kwargs = {
        'arg1': 'val1',
    }

    c = ConnectClient('API_KEY', use_specs=False)

    c.delete(url, **kwargs)

    mocked.assert_called_once_with('delete', url, **kwargs)


@pytest.mark.asyncio
async def test_async_delete(async_mocker):

    url = 'https://localhost'
    kwargs = {
        'arg1': 'val1',
    }

    with async_mocker.patch.object(AsyncConnectClient, 'execute') as mocked:
        c = AsyncConnectClient('API_KEY', use_specs=False)
        await c.delete(url, **kwargs)

    mocked.assert_awaited_once_with('delete', url, **{
        'arg1': 'val1',
    })


def test_execute(mocked_responses):
    expected = [{'id': i} for i in range(10)]
    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        json=expected,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    results = c.execute('get', 'resources')

    assert mocked_responses.calls[0].request.method == 'GET'
    headers = mocked_responses.calls[0].request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')

    assert results == expected


@pytest.mark.asyncio
async def test_async_execute(httpx_mock):
    expected = [{'id': i} for i in range(10)]
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        json=expected,
        status_code=200,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    results = await c.execute('get', 'resources')

    requests = httpx_mock.get_requests()
    assert requests[0].method == 'GET'
    headers = requests[0].headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')

    assert results == expected


def test_execute_default_headers(mocked_responses):
    mocked_responses.add(
        responses.GET,
        'https://localhost/resources',
        json=[],
    )

    c = ConnectClient(
        'API_KEY',
        endpoint='https://localhost',
        use_specs=False,
        default_headers={'X-Custom-Header': 'custom-header-value'},
    )

    c.execute('get', 'resources')

    headers = mocked_responses.calls[0].request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')
    assert 'X-Custom-Header' in headers and headers['X-Custom-Header'] == 'custom-header-value'


@pytest.mark.asyncio
async def test_async_execute_default_headers(httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://localhost/resources',
        json=[],
        status_code=200,
    )

    c = AsyncConnectClient(
        'API_KEY',
        endpoint='https://localhost',
        use_specs=False,
        default_headers={'X-Custom-Header': 'custom-header-value'},
    )

    await c.execute('get', 'resources')

    headers = httpx_mock.get_requests()[0].headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')
    assert 'X-Custom-Header' in headers and headers['X-Custom-Header'] == 'custom-header-value'


def test_execute_with_kwargs(mocked_responses):
    mocked_responses.add(
        responses.POST,
        'https://localhost/resources',
        json=[],
        status=201,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)
    kwargs = {
        'headers': {
            'X-Custom-Header': 'value',
        },
    }

    c.execute('post', 'resources', **kwargs)

    assert mocked_responses.calls[0].request.method == 'POST'

    headers = mocked_responses.calls[0].request.headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')
    assert 'X-Custom-Header' in headers and headers['X-Custom-Header'] == 'value'


@pytest.mark.asyncio
async def test_async_execute_with_kwargs(httpx_mock):
    httpx_mock.add_response(
        method='POST',
        url='https://localhost/resources',
        json=[],
        status_code=201,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)
    kwargs = {
        'headers': {
            'X-Custom-Header': 'value',
        },
    }

    await c.execute('post', 'resources', **kwargs)

    assert httpx_mock.get_requests()[0].method == 'POST'

    headers = httpx_mock.get_requests()[0].headers

    assert 'Authorization' in headers and headers['Authorization'] == 'API_KEY'
    assert 'User-Agent' in headers and headers['User-Agent'].startswith('connect-fluent')
    assert 'X-Custom-Header' in headers and headers['X-Custom-Header'] == 'value'


def test_execute_connect_error(mocked_responses):
    connect_error = {
        'error_code': 'code',
        'errors': ['first', 'second'],
    }

    mocked_responses.add(
        responses.POST,
        'https://localhost/resources',
        json=connect_error,
        status=400,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    with pytest.raises(ClientError) as cv:
        c.execute('post', 'resources')

    assert cv.value.status_code == 400
    assert cv.value.error_code == 'code'
    assert cv.value.errors == ['first', 'second']


@pytest.mark.asyncio
async def test_async_execute_connect_error(httpx_mock):
    connect_error = {
        'error_code': 'code',
        'errors': ['first', 'second'],
    }

    httpx_mock.add_response(
        method='POST',
        url='https://localhost/resources',
        json=connect_error,
        status_code=400,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    with pytest.raises(ClientError) as cv:
        await c.execute('post', 'resources')

    assert cv.value.status_code == 400
    assert cv.value.error_code == 'code'
    assert cv.value.errors == ['first', 'second']


def test_execute_uparseable_connect_error(mocked_responses):

    mocked_responses.add(
        responses.POST,
        'https://localhost/resources',
        body='error text',
        status=400,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    with pytest.raises(ClientError):
        c.execute('post', 'resources')


@pytest.mark.asyncio
async def test_async_execute_uparseable_connect_error(httpx_mock):

    httpx_mock.add_response(
        method='POST',
        url='https://localhost/resources',
        data=b'error text',
        status_code=400,
    )

    c = AsyncConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    with pytest.raises(ClientError):
        await c.execute('post', 'resources')


@pytest.mark.parametrize('encoding', ('utf-8', 'iso-8859-1'))
def test_execute_error_with_reason(mocked_responses, encoding):

    mocked_responses.add(
        responses.POST,
        'https://localhost/resources',
        status=500,
        body='Interñal Server Error'.encode(encoding),
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    with pytest.raises(ClientError):
        c.execute('post', 'resources')


def test_execute_delete(mocked_responses):

    mocked_responses.add(
        responses.DELETE,
        'https://localhost/resources',
        body='error text',
        status=204,
    )

    c = ConnectClient('API_KEY', endpoint='https://localhost', use_specs=False)

    results = c.execute('delete', 'resources')

    assert results is None


# def test_help(mocker, col_factory):
#     print_help = mocker.patch.object(DefaultFormatter, 'print_help')
#     c = ConnectClient('API_KEY', use_specs=False)
#     c1 = c.help()

#     assert print_help.called_once_with(None)
#     assert c == c1
