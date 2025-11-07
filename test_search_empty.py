import pytest
from flask import Flask
from models import Post, db


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app


def test_empty_search_returns_empty_query_object(app):
    # Patch the index to return no ids
    original_query_index = Post.query_index

    def fake_query_index(expression, page=1, per_page=20):
        return [], 0

    Post.query_index = classmethod(lambda cls, expression, page=1, per_page=20: fake_query_index(expression, page, per_page))
    query, total = Post.search('no-such-keyword')
    assert total == 0
    # Should still be a SQLAlchemy Query-like object and return an empty list with .all()
    assert hasattr(query, 'all')
    assert query.all() == []
    # The filter(False) should compile to an explicit WHERE clause (some dialects use 'false')
    assert '0 = 1' in str(query.statement) or 'WHERE false' in str(query.statement) or 'WHERE FALSE' in str(query.statement)

    # restore
    Post.query_index = original_query_index


def test_search_handles_empty_ids_with_positive_total(app):
    original_query_index = Post.query_index

    def fake_query_index(expression, page=1, per_page=20):
        # Backend mistakenly reports 1 match but returns empty ids
        return [], 1

    Post.query_index = classmethod(lambda cls, expression, page=1, per_page=20: fake_query_index(expression, page, per_page))
    query, total = Post.search('no-such-keyword')
    # We prefer to trust the actual ids list (empty), so total should be 0
    assert total == 0
    assert query.all() == []

    Post.query_index = original_query_index


def test_search_returns_ordered_rows_when_ids_provided(app):
    original_query_index = Post.query_index

    with app.app_context():
        # Insert two posts with ids that will be matched in a custom order
        p1 = Post(id=1, body='first')
        p2 = Post(id=2, body='second')
        db.session.add_all([p1, p2])
        db.session.commit()

    def fake_query_index(expression, page=1, per_page=20):
        # Return ids out-of-order; search wrapper should preserve this order
        return [2, 1], 2

    Post.query_index = classmethod(lambda cls, expression, page=1, per_page=20: fake_query_index(expression, page, per_page))
    query, total = Post.search('keyword')

    # total equals number of ids returned by the index (we trust index ids)
    assert total == 2
    results = query.all()
    assert [r.id for r in results] == [2, 1]

    Post.query_index = original_query_index


def test_search_handles_missing_rows(app):
    original_query_index = Post.query_index

    with app.app_context():
        # Only create one row in the DB
        p1 = Post(id=1, body='existing')
        db.session.add(p1)
        db.session.commit()

    def fake_query_index(expression, page=1, per_page=20):
        # Index returns two ids, but one of them is not present in DB
        return [1, 999], 2

    Post.query_index = classmethod(lambda cls, expression, page=1, per_page=20: fake_query_index(expression, page, per_page))
    query, total = Post.search('keyword')

    # total should still reflect the number of ids returned by the index
    assert total == 2
    results = query.all()
    # Only the existing item should be returned
    assert [r.id for r in results] == [1]

    Post.query_index = original_query_index
