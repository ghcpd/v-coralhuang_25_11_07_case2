from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# initialize db here only for demonstration
db = SQLAlchemy()

class SearchableMixin(object):
    """Mixin to adapt a search backend to SQLAlchemy models.

    Contract: methods return (query, total) where `query` is always a
    SQLAlchemy `Query` object. For explicit empty search results we
    provide `empty_search()` which returns `cls.query.filter(False)`.
    This emits `WHERE 0=1` and is unambiguous to callers and tools.
    """

    @classmethod
    def empty_search(cls):
        """Return an explicit empty Query for this model.

        Using `filter(False)` compiles to `WHERE 0=1` and cannot be
        accidentally satisfied by a real row (unlike `id=0`).
        """
        return cls.query.filter(False)

    @classmethod
    def query_index(cls, expression, page=1, per_page=20):
        """
        Simulate communicating with a search backend.

        This function should return (ids, total) where `ids` is a list
        of matching primary keys in the index order and `total` is the
        declared total number of matches from the search engine. For
        demonstration we simulate responses in the calling tests by
        monkeypatching this method or overriding in a subclass.
        """
        raise NotImplementedError("query_index should be provided by tests or subclass")

    @classmethod
    def search(cls, expression, page=1, per_page=20):
        """
        High-level search wrapper.

        Returns a tuple `(query, total)` where `query` is always a
        SQLAlchemy `Query` object. If the search backend reports
        `total == 0` or returns an empty `ids` list, an explicit
        empty query from `empty_search()` is returned.

        This implementation also preserves the index order when
        specific `ids` are returned by the backend.
        """
        # Expecting query_index to return (ids, total)
        result = cls.query_index(expression, page, per_page)
        if result is None:
            # Treat None as a search failure -> surface as empty but
            # callers could distinguish this by checking logs/metrics.
            return cls.empty_search(), 0

        ids, total = result

        # If total == 0 OR ids is empty -> explicit empty query
        if not ids or total == 0:
            return cls.empty_search(), 0

        # Otherwise, build a query filtering by the returned ids and
        # preserving the index order using SQLAlchemy's `case`.
        # Note: We assume primary key attribute is `id`.
        from sqlalchemy import case

        ordering = case({id_: index for index, id_ in enumerate(ids)}, value=cls.id)
        query = cls.query.filter(cls.id.in_(ids)).order_by(ordering)
        return query, total


class Post(SearchableMixin, db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
