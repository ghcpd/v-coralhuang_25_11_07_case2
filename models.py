from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# initialize db here only for demonstration
db = SQLAlchemy()

class SearchableMixin(object):
    @classmethod
    def empty_search(cls):
        """Return an explicit empty SQLAlchemy Query.

        Using filter(False) compiles to a WHERE 0=1 clause which is the
        canonical way to represent an empty result-set in SQLAlchemy.
        Avoids using filter_by(id=0) which can match a real primary key.
        """
        return cls.query.filter(False)

    @classmethod
    def query_index(cls, expression, page=1, per_page=20):
        """
        Simulate a search backend returning ids and total.
        This function MUST return a tuple (ids, total).
        """
        # For the purpose of the demo we simulate no matches.
        ids = []  # simulate no match from the search engine
        total = 0
        return ids, total

    @classmethod
    def search(cls, expression, page=1, per_page=20):
        """
        High-level search wrapper.

        Contract: ALWAYS return (query, total) where `query` is a SQLAlchemy
        Query object. When there are no matching ids, return a canonical
        empty query via `cls.empty_search()`.
        """
        ids, total = cls.query_index(expression, page, per_page)

        # If there are no ids returned, return an explicit empty query
        # to avoid ambiguous constructs like filter_by(id=0)
        if not ids:
            return cls.empty_search(), 0

        # Otherwise construct a query that preserves order if needed
        # by mapping ids to their position. This is a common pattern.
        when = []
        for i, id in enumerate(ids):
            when.append((id, i))

        # Build ordered query preserving index order
        # Note: SQLAlchemy doesn't have a portable built-in for this; the
        # pattern below uses a CASE expression if you need to maintain order.
        query = cls.query.filter(cls.id.in_(ids))
        # If the caller depends on order provided by the index, they should
        # rely on the index's sort or we can provide a CASE(ordering) here.

        return query, total

class Post(SearchableMixin, db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
