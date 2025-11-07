# flask_searchablemixin_empty_result_bug

Why filter_by(id=0) is discouraged

Using patterns like `filter_by(id=0)` to represent an empty search result is problematic:

- It produces a real-looking SQL filter which can confuse logs and debug output
- If a row with id=0 exists (e.g. in imported legacy data or tests), the branch is no longer empty
- Different developers use differing patterns to construct empty results, causing inconsistency

Recommended pattern

Always return a consistent type from search helpers. When returning a `SQLAlchemy Query` in the empty case, prefer:

    return cls.query.filter(False)

This compiles to `WHERE 0=1` and is unambiguous and safe.

Alternatively, if your contract is to return a list, return `([], 0)` explicitly.
