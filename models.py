from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import case

# initialize db here only for demonstration
db = SQLAlchemy()

class SearchableMixin(object):
    @classmethod
    def query_index(cls, expression, page=1, per_page=20):
        """
        Simulate a search backend calling a search engine.

        This method returns (ids, total) as the index would, *not* a SQLAlchemy Query.
        The higher-level .search() constructs a Query from these ids.
        """
        # Simulated backend: by default, return no match
        ids = []  # simulate no match from the search engine
        total = 0
        return ids, total

    @classmethod
    def empty_search(cls):
        """
        Returns an explicit, unambiguous empty SQLAlchemy Query for this model.

        Using filter(False) results in a WHERE 0=1 clause, which is obvious to
        readers and cannot collide with a real id in the database.
        """
        # SQLAlchemy will compile filter(False) into a 'WHERE 0 = 1' expression
        return cls.query.filter(False)

    @classmethod
    def search(cls, expression, page=1, per_page=20):
        """
        High-level search wrapper.

        This method constructs a SQLAlchemy Query object from the ids list
        returned by the search backend. The return value is always a tuple
        (query, total) where `query` is a SQLAlchemy Query and `total` is an
        integer count. In the empty case, it returns cls.empty_search().
        If the backend reports a total but returns an empty `ids` list, we
        treat the result as empty and set total to 0 to avoid misleading callers.
        """
        ids, reported_total = cls.query_index(expression, page, per_page)

        # Coerce ids to a list (avoid None) and dedupe while preserving order
        ids = list(dict.fromkeys(ids or []))
        total = len(ids)

        if total == 0:
            # Explicit empty query that compiles to WHERE 0=1
            return cls.empty_search(), 0

        # Build a query filtered by the ids, preserving the order returned by the index
        # Preserve index order using a CASE expression mapping id -> position
        index_order_map = {id_value: pos for pos, id_value in enumerate(ids)}
        ordering = case(index_order_map, value=cls.id, else_=len(ids))
        query = cls.query.filter(cls.id.in_(ids)).order_by(ordering)

        return query, total

class Post(SearchableMixin, db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
