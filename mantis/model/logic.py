from enum import Enum

import math
from six import string_types


class Message:
    class Type(Enum):
        ERROR = 0
        SUCCESS = 1

    def __init__(self, t, m):
        self.type = t
        self.text = m


class Serializable(object):
    def serialize(self):
        raise NotImplementedError()


class Page(Serializable):
    def __init__(self, index: int, items: list):
        self.items = items
        if not isinstance(self.items, list):
            self.items = []
        self.index = index

    def serialize(self):
        return {'index': self.index, 'items': serialize(self.items)}


class Pagination:
    def __init__(self, query, page_size=20):
        if page_size <= 0:
            raise AttributeError('page_size needs to be >= 1')
        self.query = query
        self.page_size = page_size
        self.total = query.count()
        if self.page_size is not None and self.page_size > 0:
            self.nb_pages = math.ceil(self.total / self.page_size)
        else:
            self.nb_pages = 1

    def get(self, page: int = 1):
        if page <= 0:
            page = 1
        if self.nb_pages < page:
            page = self.nb_pages
        items = self.query.limit(self.page_size).offset((page - 1) * self.page_size).all()
        return Page(page, items)

    def __getitem__(self, index):
        return self.get(index)

    def __len__(self):
        return self.total


def serialize(e):
    if isinstance(e, (int, float, bool)) or isinstance(e, string_types):
        return e
    if isinstance(e, list):
        return [serialize(v) for v in e]
    if isinstance(e, dict):
        return {k: serialize(v) for k, v in e.items()}
    if isinstance(e, set):
        return serialize(list(e))
    if isinstance(e, Serializable):
        return e.serialize()
    return None
