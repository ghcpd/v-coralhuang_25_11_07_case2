from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import case

# initialize db here only for demonstration
db = SQLAlchemy()

class SearchableMixin(object):
    @classmethod
    def empty_search(cls):
        """
        Return an explicit empty SQLAlchemy query that compiles to a WHERE 0=1
        (or equivalent). This is safer and clearer than using filter_by(id=0).
        We attach a small marker attribute so unit tests can detect the empty branch
        without hitting the database.
        """
        q = cls.query.filter(False)
        # Marker for tests and downstream logic (non-persistent)
        try:
            q._is_empty_search = True
        except Exception:
            pass
        return q

    @classmethod
    def query_index(cls, expression, page=1, per_page=20):
        """
        Simulate a search backend returning ids and a total count.
        The method must return a SQLAlchemy `Query` and an integer total.

        Rules:
        - If the search engine returns no ids (empty list) we return `empty_search()` and total == 0.
        - If it returns ids, create a query filtering by those ids and preserve index order with a CASE expression.
        - Avoid filter_by(id=0) — this can match real rows if id==0 exists.
        """
        # Simulate the remote search service returning an id list and count.
        ids = []  # empty: bug simulated
        total = 0

        # If no matches from the search engine, return an explicit empty query.
        if not ids:
            return cls.empty_search(), 0

        # Otherwise, construct a query for the returned ids and preserve order.
        when_cases = {id_: i for i, id_ in enumerate(ids)}
        order_case = case(when_cases, value=cls.id)

        query = cls.query.filter(cls.id.in_(ids)).order_by(order_case)
        return query, total

    @classmethod
    def search(cls, expression, page=1, per_page=20):
        """
        High-level search wrapper. Returns (query, total) where query is a SQLAlchemy
        query object; for empty results the returned query is `cls.empty_search()`.

        Behavior guarantees:
        - Always returns a Tuple[Query, int]
        - For empty results use `empty_search()` to avoid `id=0` hacks
        - If the search backend misreports total (e.g. total > 0 but ids == []), we prefer
the actual `ids` (empty) and treat it as 0 results.
        """
        query, total = cls.query_index(expression, page, per_page)
        # Defensive: if a query is returned that contains no ids (empty query), translate into empty_search.
        # We detect our own _is_empty_search marker or rely on the query being a false-filter.
        if getattr(query, "_is_empty_search", False):
            return query, 0

        # If the query is a filter-by-ids with an empty list, convert it to empty_search.
        # This covers cases where the index lied about `total` but returned no ids.
        try:
            # _criterion is an internal representation — use defensive try.
            # For many SQLAlchemy versions, a WHERE with a constant false condition will be compiled from `False`.
            # We prefer the explicit marker so this branch is best-effort.
            if str(query) == str(cls.query.filter(False)):
                return cls.empty_search(), 0
        except Exception:
            pass

        return query, total


class Post(SearchableMixin, db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
