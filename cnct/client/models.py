from keyword import iskeyword

from cnct.client.exceptions import NotFoundError
from cnct.client.utils import parse_content_range, resolve_attribute
from cnct.help import print_help
from cnct.rql import R


class NS:
    """
    A namespace is a group of related collections.
    """
    def __init__(self, client, path, specs=None):
        self.client = client
        self.path = path
        self.specs = specs

    def __getattr__(self, name):
        if not self.specs:
            return self.collection(name)
        if name in self.specs.collections:
            return self.collection(name)
        raise AttributeError(f'Unable to resolve {name}.')

    def __dir__(self):
        default = sorted(super().__dir__() + list(self.__dict__.keys()))
        if not self.specs:
            return default
        cl = self.specs.collections.keys()
        return default + [
            name for name in cl
            if name.isidentifier() and not iskeyword(name)
        ]

    def collection(self, name):
        """
        Returns the collection called `name`.

        :param name: The name of the collection.
        :type name: str
        :raises: :exc:`~cnct.client.exceptions.NotFoundError` The collection does not exist.
        :return: The collection called `name`.
        :rtype: Collection
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        if not self.specs:
            return Collection(
                self.client,
                f'{self.path}/{name}',
            )
        if name in self.specs.collections:
            return Collection(
                self.client,
                f'{self.path}/{name}',
                self.specs.collections.get(name),
            )
        raise NotFoundError(f'The collection {name} does not exist.')

    def help(self):
        """
        Output the namespace documentation to the console.

        :return: self
        :rtype: NS
        """
        print_help(self.specs)
        return self


class Collection:
    """
    A collection is a group of operations on a domain entity.
    """
    def __init__(self, client, path, specs=None):
        self.client = client
        self.path = path
        self.specs = specs

    def __iter__(self):
        raise TypeError('A collection object is not iterable.')

    def __getitem__(self, item_id):
        return self.item(item_id)

    def all(self):
        return Search(
            self.client,
            self.path,
            specs=self.specs.operations.get('search') if self.specs else None,
        )

    def filter(self, *args, **kwargs):
        query = R()
        for arg in args:
            if isinstance(arg, str):
                query &= R(_expr=arg)
                continue
            if isinstance(arg, R):
                query &= arg
                continue
            raise TypeError(f'arguments must be string or R not {type(arg)}')

        if kwargs:
            query &= R(**kwargs)

        return Search(
            self.client,
            self.path,
            specs=self.specs.operations.get('search') if self.specs else None,
            query=query,
        )

    def search(self, term):
        """
        Return a Search object that represents
        a list or search operation on a collection.

        :param query: RQL query expression, defaults to None
        :type query: str, optional
        :return: a Search object.
        :rtype: Search
        """
        return Search(
            self.client,
            self.path,
            self.specs.operations.get('search') if self.specs else None,
            search=term,
        )

    def create(self, payload=None, **kwargs):
        """
        Create a new collection item.

        :param payload: JSON payload of the object to create, defaults to None
        :type payload: dict, optional
        :return: The newly created item.
        :rtype: dict
        """
        return self.client.create(
            self.path,
            payload=payload,
            **kwargs,
        )

    def item(self, item_id):
        """
        Returns an Item object

        :param item_id: [description]
        :type item_id: [type]
        :return: [description]
        :rtype: [type]
        """
        return Item(
            self.client,
            f'{self.path}/{item_id}',
            self.specs.item_specs if self.specs else None,
        )

    def help(self):
        print_help(self.specs)
        return self


class Item:
    """Represent a generic item."""
    def __init__(self, client, path, specs=None):
        self.client = client
        self.path = path
        self.specs = specs

    def __getattr__(self, name):
        if not self.specs:
            raise AttributeError(
                'No specs available. Use the `collection` '
                'or `action` methods instead.'
            )
        if name in self.specs.collections:
            return self.collection(name)
        if name in self.specs.actions:
            return self.action(name)
        raise AttributeError('Unable to resolve {}.'.format(name))

    def __dir__(self):
        if not self.specs:
            return super().__dir__()
        ac = list(self.specs.actions.keys())
        cl = list(self.specs.collections.keys())
        additional_names = [
            name for name in cl + ac
            if name.isidentifier() and not iskeyword(name)
        ]
        return sorted(super().__dir__() + additional_names)

    def collection(self, name):
        """
        Returns the collection called `name`.

        :param name: The name of the collection.
        :type name: str
        :raises: :exc:`~cnct.client.exceptions.NotFoundError` The collection does not exist.
        :return: The collection called `name`.
        :rtype: Collection
        """
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        if not self.specs:
            return Collection(
                self.client,
                f'{self.path}/{name}',
            )
        if name in self.specs.collections:
            return Collection(
                self.client,
                f'{self.path}/{name}',
                self.specs.collections.get(name),
            )
        raise NotFoundError(f'The collection {name} does not exist.')

    def action(self, name):
        """Get an action for the current item."""
        if not isinstance(name, str):
            raise TypeError('`name` must be a string.')

        if not name:
            raise ValueError('`name` must not be blank.')

        if not self.specs:
            return Action(
                self.client,
                f'{self.path}/{name}',
            )
        if name in self.specs.actions:
            return Action(
                self.client,
                f'{self.path}/{name}',
                self.specs.actions.get(name),
            )
        raise NotFoundError(f'The action {name} does not exist.')

    def get(self, **kwargs):
        return self.client.get(self.path, **kwargs)

    def update(self, payload=None, **kwargs):
        return self.client.update(
            self.path,
            payload=payload,
            **kwargs,
        )

    def delete(self, **kwargs):
        return self.client.delete(
            self.path,
            **kwargs,
        )

    def values(self, *fields):
        results = {}
        item = self.get()
        for field in fields:
            results[field] = resolve_attribute(field, item)
        return results

    def help(self):
        print_help(self.specs)
        return self


class Action:
    def __init__(self, client, path, specs=None):
        self.client = client
        self.path = path
        self.specs = specs

    def get(self, **kwargs):
        return self.client.get(self.path, **kwargs)

    def post(self, payload=None, **kwargs):
        if payload:
            kwargs['json'] = payload
        return self.client.execute(
            'post',
            self.path,
            200,
            **kwargs,
        )

    def put(self, payload=None, **kwargs):
        if payload:
            kwargs['json'] = payload
        return self.client.execute(
            'put',
            self.path,
            200,
            **kwargs,
        )

    def delete(self, **kwargs):
        return self.client.delete(
            self.path,
            **kwargs,
        )

    def help(self):
        print_help(self.specs)
        return self


class Search:
    def __init__(
        self,
        client,
        path,
        specs=None,
        query=None,
        search=None
    ):
        self.client = client
        self.path = path
        self.specs = specs
        self.query = query or R()
        self.results = None
        self._result_iterator = None
        self._limit = 100
        self._offset = 0
        self._slice = False
        self.content_range = None
        self._fields = None
        self._search = search
        self._select = []
        self._ordering = []
        self._config = {}

    def __len__(self):
        if not self.results:
            self._perform()
        return len(self.results)

    def __iter__(self):
        if not self.results:
            self._perform()
        return self

    def __next__(self):
        try:
            item = next(self._result_iterator)
            if self._fields:
                return self._get_values(item)
            return item
        except StopIteration:
            if self._slice:
                self._offset = 0
                raise
            if self.content_range.last == self.content_range.count - 1:
                self._offset = 0
                raise
            self._offset += self._limit
            self._perform()
            item = next(self._result_iterator)
            if self._fields:
                return self._get_values(item)
            return item

    def __bool__(self):
        self._perform()
        return bool(self.results)

    def __getitem__(self, key):
        if not isinstance(key, (int, slice)):
            raise TypeError('Search indices must be integers or slices.')

        assert (not isinstance(key, slice) and (key >= 0)) or (
            isinstance(key, slice)
            and (key.start is None or key.start >= 0)
            and (key.stop is None or key.stop >= 0)
        ), "Negative indexing is not supported."

        assert (not isinstance(key, slice) and (key >= 0)) or (
            isinstance(key, slice)
            and (key.step is None or key.step == 0)
        ), "Indexing with step is not supported."

        if self.results:
            return self.results[key]
        if isinstance(key, int):
            self._perform()
            return self.results[key]

        self._offset = key.start
        self._limit = key.stop - key.start
        self._slice = True
        return self

    def configure(self, **kwargs):
        self._config = kwargs or {}
        return self

    def order_by(self, *fields):
        self._ordering.extend(fields)
        return self

    def select(self, *fields):
        self._select.extend(fields)
        return self

    def filter(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, str):
                self.query &= R(_expr=arg)
                continue
            if isinstance(arg, R):
                self.query &= arg
                continue
            raise TypeError(f'arguments must be string or R not {type(arg)}')

        if kwargs:
            self.query &= R(**kwargs)

        return self

    def count(self):
        if not self.results:
            self._perform()
        return self.content_range.count

    def first(self):
        if not self.results:
            self._perform()
        return self.results[0] if self.results else None

    def values_list(self, *fields):
        self._fields = fields
        if self.results:
            return [
                self._get_values(item)
                for item in self.results
            ]
        return self

    def _get_values(self, item):
        return {
            field: resolve_attribute(field, item)
            for field in self._fields
        }

    def _build_qs(self):
        qs = ''
        if self._select:
            qs += f'&select({",".join(self._select)})'
        if self.query:
            qs += f'&{str(self.query)}'
        if self._ordering:
            qs += f'&ordering({",".join(self._ordering)})'
        return qs[1:] if qs else ''

    def _perform(self):
        url = f'{self.path}'
        qs = self._build_qs()
        if qs:
            url = f'{url}?{qs}'

        self._config.setdefault('params', {})

        self._config['params'].update({
            'limit': self._limit,
            'offset': self._offset,
        })

        if self._search:
            self._config['params']['search'] = self._search

        self.results = self.client.get(url, **self._config)
        self.content_range = parse_content_range(
            self.client.response.headers['Content-Range'],
        )
        self._result_iterator = iter(self.results)

    def help(self):
        print_help(self.specs)
        return self
