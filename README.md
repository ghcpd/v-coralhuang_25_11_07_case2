# SearchableMixin empty-result fix

Why `filter_by(id=0)` is discouraged

- `filter_by(id=0)` masquerades as a real query, confusing logs, pagination, and UIs.
- If a row with `id==0` exists (legacy data or tests), it will no longer represent an empty result.
- Different developers use different patterns (filter_by/id==0, empty list, etc.) leading to inconsistent behavior.

What to use instead

- Use an explicit `empty_search()` helper that returns `cls.query.filter(False)`.
- Keep a stable return contract for `search()` — it always returns `(query, total)` where `query` is a SQLAlchemy Query (or an explicitly empty query). This makes downstream code simpler and safer.

Additional notes

- The mixin now prefers the actual list of ids returned by an index; if the index returns an empty id list it will be treated as zero results even if the search engine misreports `total`.
- Use ordering via CASE expressions to preserve the search index order when returning rows from the DB.
