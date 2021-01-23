from cnct.client.constants import CONNECT_ENDPOINT_URL, CONNECT_SPECS_URL
from cnct.client.mixins import HttpxMixin, RequestsMixin
from cnct.client.models import AsyncCollection, AsyncNS, Collection, NS
from cnct.client.help_formatter import DefaultFormatter
from cnct.client.openapi import OpenAPISpecs


class ConnectClientBase:
    """
    Connect ReST API client.
    """
    def __init__(
        self,
        api_key,
        endpoint=None,
        use_specs=True,
        specs_location=None,
        validate_using_specs=True,
        default_headers=None,
        default_limit=100,
    ):
        """
        Create a new instance of the ConnectClient.

        :param api_key: The API key used for authentication.
        :type api_key: str
        :param endpoint: The API endpoint, defaults to CONNECT_ENDPOINT_URL
        :type endpoint: str, optional
        :param specs_location: The Connect OpenAPI specification local path or URL, defaults to CONNECT_SPECS_URL
        :type specs_location: str, optional
        :param default_headers: Http headers to apply to each request, defaults to {}
        :type default_headers: dict, optional
        """
        if default_headers and 'Authorization' in default_headers:
            raise ValueError('`default_headers` cannot contains `Authorization`')

        self.endpoint = endpoint or CONNECT_ENDPOINT_URL
        self.api_key = api_key
        self.default_headers = default_headers or {}
        self._use_specs = use_specs
        self._validate_using_specs = validate_using_specs
        self.specs_location = specs_location or CONNECT_SPECS_URL
        self.specs = None
        if self._use_specs:
            self.specs = OpenAPISpecs(self.specs_location)
        self.response = None
        self._help_formatter = DefaultFormatter(self.specs)

    def __getattr__(self, name):
        """
        Returns a collection object called ``name``.

        :param name: The name of the collection to retrieve.
        :type name: str
        :return: a collection called ``name``.
        :rtype: Collection
        """
        if '_' in name:
            name = name.replace('_', '-')
        return self.collection(name)

    def __call__(self, name):
        return self.ns(name)

    def print_help(self, obj):
        print()
        print(self._help_formatter.format(obj))

    def help(self):
        self.print_help(None)
        return self


class ConnectClientMixin:
    def ns(self, name):
        """
        Returns the namespace called ``name``.

        :param name: The name of the namespace to access.
        :type name: str
        :return: The namespace called ``name``.
        :rtype: NS
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return NS(self, name)

    def collection(self, name):
        """
        Returns the collection called ``name``.

        :param name: The name of the collection to access.
        :type name: str
        :return: The collection called ``name``.
        :rtype: Collection
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return Collection(
            self,
            name,
        )


class AsyncConnectClientMixin:
    def ns(self, name):
        """
        Returns the namespace called ``name``.

        :param name: The name of the namespace to access.
        :type name: str
        :return: The namespace called ``name``.
        :rtype: NS
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return AsyncNS(self, name)

    def collection(self, name):
        """
        Returns the collection called ``name``.

        :param name: The name of the collection to access.
        :type name: str
        :return: The collection called ``name``.
        :rtype: Collection
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        return AsyncCollection(
            self,
            name,
        )


class ConnectClient(ConnectClientBase, ConnectClientMixin, RequestsMixin):
    pass


class AsyncConnectClient(ConnectClientBase, AsyncConnectClientMixin, HttpxMixin):
    pass
