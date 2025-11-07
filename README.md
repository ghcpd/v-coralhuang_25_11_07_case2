# SearchableMixin: explicit empty results

This small repo demonstrates why returning `filter_by(id=0)` from a `SearchableMixin` is dangerous:

- `filter_by(id=0)` looks like a real query in logs, UIs and pagination helpers and may match a real row if an entry with id==0 exists.
- Downstream code may treat the query as a real set of results which can cause confusing UI behavior.

Preferred pattern:

- Use a canonical `empty_search()` that returns `cls.query.filter(False)` — it compiles to a deterministic false condition (WHERE 0=1) and is explicit.
- Keep the return contract consistent. In this repo `search(...)` always returns `(query, total)`. For empty results `query` is `cls.empty_search()`.

This avoids ad-hoc hacks and makes code more robust for pagination, serializers, and tooling.
