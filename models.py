from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import case

# initialize db here only for demonstration
db = SQLAlchemy()

class SearchableMixin(object):
    @classmethod
    def query_index(cls, expression, page=1, per_page=20):
        """
        Simulate a search backend by returning a (ids, total) tuple.

        IMPORTANT: This method mimics a search backend and returns raw ids and a
        reported total. The downstream `search` method is responsible for
        translating these ids into a SQLAlchemy Query object. Returning a
        SQLAlchemy Query from here conflates responsibilities and creates the
        confusing `filter_by(id=0)` pattern when there are no results.
        """
        ids = []  # simulate no match from the search engine
        total = 0
        return ids, total

    @classmethod
    def empty_search(cls):
        """
        Return an explicit and canonical "empty" SQLAlchemy query.

        Using `filter(False)` (which compiles to `WHERE 0=1`) is clearer and
        less error-prone than `filter_by(id=0)` because it cannot match any
        real row regardless of the id space.
        """
        return cls.query.filter(False)

    @classmethod
    def search(cls, expression, page=1, per_page=20):
        """
        High-level search wrapper.

        Contract: Always return `(query, total)` where `query` is a
        SQLAlchemy Query object (never a raw list). In the empty case the
        query is `cls.empty_search()` which is unambiguously an empty result
        set.  `total` is the number of ids returned by the index (len(ids)).
        If the backing search claims a different `total`, we prefer the
        actual ids returned to avoid misrepresentation.
        """
        ids, reported_total = cls.query_index(expression, page, per_page)

        # Prefer the actual number of ids returned by the index. If the
        # index reports a non-zero total but returns no ids, the safest
        # behaviour is to treat it as zero results here.
        total = len(ids)
        if total == 0:
            return cls.empty_search(), 0

        # Build a query for the found ids and preserve the index ordering
        # using a CASE expression to avoid arbitrary DB ordering.
        order_cases = [(cls.id == _id, pos) for pos, _id in enumerate(ids)]
        order_expr = case(*order_cases, else_=len(ids))
        query = cls.query.filter(cls.id.in_(ids)).order_by(order_expr)
        return query, total


class Post(SearchableMixin, db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
