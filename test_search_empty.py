from models import Post


def test_empty_search_returns_empty_list():
    query, total = Post.search('no-such-keyword')
    assert total == 0
    # .all() on the returned query should behave like an empty list
    # If the environment has no DB configured, this assertion may be
    # executed against a mocked Query in other tests.
    assert query.all() == []


def test_empty_search_from_misreported_total(monkeypatch):
    # Simulate an index that reports a positive total but returns no ids.
    def fake_query_index(expression, page, per_page):
        return [], 5

    monkeypatch.setattr(Post, 'query_index', staticmethod(fake_query_index))

    query, total = Post.search('no-such-keyword')
    # Even though the backend claimed total 5, our code should trust
    # the empty ids list and normalize total to 0.
    assert total == 0
    assert query.all() == []


def test_search_with_ids_and_missing_db_rows(monkeypatch):
    # Simulate index returning ids but DB has fewer entries than claimed.
    def fake_query_index(expression, page, per_page):
        return [1, 2, 3], 3

    class FakeQuery:
        def __init__(self, items):
            self._items = items

        def all(self):
            # Simulate DB only having id 1
            return [1]

    def fake_filter(condition):
        return FakeQuery([1])

    monkeypatch.setattr(Post, 'query_index', staticmethod(fake_query_index))
    monkeypatch.setattr(Post, 'query', type('Q', (), {'filter': staticmethod(fake_filter)}))

    query, total = Post.search('some-keyword')
    assert total == 3
    # actual DB results may be fewer than index total, but callers can
    # inspect `total` and `query.all()` to reconcile.
    assert query.all() == [1]
