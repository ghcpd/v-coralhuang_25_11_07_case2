import types
from models import Post


def test_empty_search_returns_explicit_empty():
    query, total = Post.search('no-such-keyword')
    # total should be 0 for empty search
    assert total == 0
    # The returned query should be the explicit empty_search query (marker set)
    assert getattr(query, '_is_empty_search', False) is True


def test_search_with_ids_is_not_empty():
    # Monkeypatch the class method to simulate ids returned by the backend.
    original = Post.query_index

    def fake_query_index(cls, expression, page=1, per_page=20):
        ids = [1, 42, 7]
        total = len(ids)
        q = cls.query.filter(cls.id.in_(ids))
        return q, total

    Post.query_index = classmethod(fake_query_index)
    try:
        query, total = Post.search('some-keyword')
        assert total == 3
        assert not getattr(query, '_is_empty_search', False)
    finally:
        Post.query_index = original


def test_search_handles_empty_ids_but_positive_total():
    # If the index returns an empty ids list but reports total>0, we prefer the actual
    # ids list and report zero results rather than pretending to have matches.
    original = Post.query_index

    def fake_query_index_mismatch(cls, expression, page=1, per_page=20):
        # index claims 2 results but returns no ids; we must treat this as empty
        q = cls.query.filter(cls.id.in_([]))
        return q, 2

    Post.query_index = classmethod(fake_query_index_mismatch)
    try:
        query, total = Post.search('buggy-index')
        # Should be treated as empty
        assert total == 0
        assert getattr(query, '_is_empty_search', False) is True
    finally:
        Post.query_index = original
