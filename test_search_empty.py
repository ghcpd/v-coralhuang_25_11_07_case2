from models import Post
import pytest


class DummyPostIndex:
    """Helper to monkeypatch Post.query_index responses."""

    def __init__(self, ids, total):
        self._ids = ids
        self._total = total

    def __call__(self, expression, page=1, per_page=20):
        return list(self._ids), int(self._total)


def test_empty_search_returns_empty_query():
    # Simulate backend returning no ids and total == 0
    Post.query_index = DummyPostIndex([], 0)
    query, total = Post.search('no-such-keyword')
    assert total == 0
    # query should be a SQLAlchemy Query; calling .all() yields empty list
    assert hasattr(query, 'all')
    assert query.all() == []


def test_search_with_total_zero_but_ids_present_treated_as_empty():
    # Simulate backend misreporting: total == 0 but ids list non-empty
    Post.query_index = DummyPostIndex([1, 2], 0)
    query, total = Post.search('weird-backend')
    assert total == 0
    assert query.all() == []


def test_search_preserves_index_order():
    # Create an in-memory SQLite DB and add rows to query against
    from flask import Flask
    from models import db, Post as PostModel

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        # create three posts with ids 1,2,3
        p1 = PostModel(id=1, body='a')
        p2 = PostModel(id=2, body='b')
        p3 = PostModel(id=3, body='c')
        db.session.add_all([p1, p2, p3])
        db.session.commit()

        # Simulate index returning ids out of db order: [3,1]
        PostModel.query_index = DummyPostIndex([3, 1], 2)
        query, total = PostModel.search('some-query')
        assert total == 2
        rows = query.all()
        assert [r.id for r in rows] == [3, 1]
