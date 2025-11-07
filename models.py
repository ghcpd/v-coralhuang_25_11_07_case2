from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# initialize db here only for demonstration
db = SQLAlchemy()

class SearchableMixin(object):
    """
    Mixin providing search functionality with a clear, explicit pattern for empty results.
    
    Key patterns:
    - Uses filter(False) (WHERE 0=1) for explicit empty queries, never filter_by(id=0)
    - Always returns (query, total) where query is a SQLAlchemy Query object
    - Handles edge cases: empty ids list, mismatched totals, etc.
    """

    @classmethod
    def empty_search(cls):
        """
        Return an explicit empty query object that will match no rows.
        
        This uses filter(False) which compiles to WHERE 0=1 in SQL, making it
        unambiguous to callers, logging systems, and pagination helpers that
        this query genuinely matches nothing (not a placeholder or hack).
        
        Returns:
            SQLAlchemy Query object guaranteed to return zero results.
        """
        return cls.query.filter(False)

    @classmethod
    def query_index(cls, expression, page=1, per_page=20):
        """
        Execute a search query against the search backend and return matching rows.
        
        This method simulates calling a full-text/Elasticsearch backend that returns
        matching row IDs. It handles the following cases:
        
        1. Normal case: backend returns (ids, total) with len(ids) > 0
           -> Return a query filtered to those ids, preserving backend order via
              CASE WHEN construct
        
        2. Empty case: backend returns ([], 0) meaning no matches
           -> Return cls.empty_search() which is explicit and unambiguous
        
        3. Edge case: backend returns ([], total) where total > 0 (data inconsistency)
           -> Trust the actual ids list and return empty_search() rather than
              creating nonsense filters
        
        Args:
            expression (str): The search query string
            page (int): Page number for pagination (1-indexed)
            per_page (int): Results per page
        
        Returns:
            tuple: (query, total) where:
                - query is a SQLAlchemy Query object (either filtered or empty)
                - total is the count from the search backend (0 or positive int)
        """
        # Simulate calling search backend
        # In production, this would call Elasticsearch, Solr, Whoosh, etc.
        ids = []  # simulate no match from the search engine
        total = 0

        # EXPLICIT EMPTY BRANCH: When search backend returns no results,
        # return an explicit empty query instead of filter_by(id=0)
        if not ids:
            # Trust the actual ids list; even if backend reported total > 0,
            # if we got no ids, return an explicit empty query
            return cls.empty_search(), total

        # NORMAL CASE: backend returned matching ids
        # Preserve the order from the search backend using CASE WHEN
        # (important for relevance scores, ranking, etc.)
        from sqlalchemy import case as sql_case
        
        case_expr = sql_case(
            {id_: idx for idx, id_ in enumerate(ids)},
            value=cls.id
        )
        query = cls.query.filter(cls.id.in_(ids)).order_by(case_expr)
        
        return query, total

    @classmethod
    def search(cls, expression, page=1, per_page=20):
        """
        High-level search wrapper that returns explicit, consistent results.
        
        This method:
        - Calls query_index() to get results from the search backend
        - Applies pagination if needed
        - Returns a consistent (query, total) tuple that callers can safely consume
        
        Args:
            expression (str): The search query string
            page (int): Page number for pagination (1-indexed)
            per_page (int): Results per page
        
        Returns:
            tuple: (query, total) where query is a SQLAlchemy Query (or empty query)
                   and total is the count from the search backend.
        
        Example:
            query, total = Post.search('keyword', page=1, per_page=20)
            
            # Safe to use immediately:
            results = query.all()
            paginated = query.paginate(page, per_page)
            
            # Safe to log/inspect:
            print(query)  # Will show "WHERE 0=1" for empty, not "WHERE id=0"
        """
        query, total = cls.query_index(expression, page, per_page)
        return query, total


class Post(SearchableMixin, db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
