Why filter_by(id=0) is discouraged
----------------------------------

Using `filter_by(id=0)` to represent an empty search result is fragile and confusing:

- It looks like a real query in logs and UIs.
- If a row with `id == 0` exists (legacy/test data), it stops being empty.
- Different developers use inconsistent patterns leading to fragile callers.

Pattern to use instead
----------------------

Provide a model-level `empty_search()` that returns `cls.query.filter(False)`.
This compiles to `WHERE 0=1`, which is explicit, unambiguous, and cannot match
any real row. The `SearchableMixin.search()` method should always return a
consistent `(query, total)` pair where `query` is a SQLAlchemy `Query` object.
