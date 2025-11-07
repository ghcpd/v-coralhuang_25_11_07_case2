# flask_searchablemixin_empty_result_bug

This repository demonstrates and fixes a common pattern where a "no results" search is represented as `cls.query.filter_by(id=0)`. That pattern is brittle and confusing. The corrected approach uses an explicit `empty_search` helper that returns `cls.query.filter(False)`, which compiles to `WHERE 0=1` and is unambiguously empty.

Why `filter_by(id=0)` is discouraged:
- It looks like a real query filter and confuses logging and UIs.
- It breaks pagination, URL generation, and other helpers that assume the filter is meaningful.
- If a record with `id == 0` exists (legacy data, fixtures), the branch is no longer empty.

What this patch changes:
- `SearchableMixin.query_index` now returns `(ids, total)` (the search engine result) instead of a Query.
- `SearchableMixin.search` constructs a SQLAlchemy query from the ids, always returning `(query, total)`.
- Added `SearchableMixin.empty_search()` to construct an explicit empty Query (`filter(False)`).
- Tests added to validate empty behavior and ordering.

Recommendation:
- Prefer the `empty_search()` helper and return consistent types from model helper methods. If you prefer returning lists instead of Query objects, change the public contract and document it clearly.
