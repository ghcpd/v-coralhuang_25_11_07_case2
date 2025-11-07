from models import Post
import pytest


def test_empty_search_returns_empty_list(session):
    # ensure no rows
    query, total = Post.search('no-such-keyword')
    assert total == 0
    assert query.all() == []


def test_index_returns_empty_ids_misreported_total(session):
    # Temporarily monkeypatch Post.query_index to simulate a misreported total
    original = Post.query_index
    Post.query_index = classmethod(lambda cls, expression, page=1, per_page=20: ([], 42))
    try:
        query, total = Post.search('whatever')
        assert total == 0  # we trust len(ids) not the reported total
        assert query.all() == []
    finally:
        Post.query_index = original


def test_search_preserves_index_order_and_ignores_missing_ids(session):
    # Insert two posts with ids 1 and 2. Note: sqlite autoincrement starts at 1.
    p1 = Post(body='first')
    p2 = Post(body='second')
    from models import db
    db.session.add_all([p1, p2])
    db.session.commit()

    # Simulate the index returning ids including a missing id=3 then 1 and 2.
    original = Post.query_index
    Post.query_index = classmethod(lambda cls, expression, page=1, per_page=20: ([3, p1.id, p2.id], 3))
    try:
        query, total = Post.search('dummy')
        # total should be len(ids) (3) but only 2 rows exist in DB; the query should return both rows
        assert total == 3
        result_rows = query.all()
        assert [r.id for r in result_rows] == [p1.id, p2.id]
    finally:
        Post.query_index = original
