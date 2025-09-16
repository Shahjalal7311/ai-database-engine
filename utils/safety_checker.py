from config.settings import settings
import re

class QuerySafetyChecker:
    @staticmethod
    def is_query_safe(query: str) -> bool:
        """Check if SQL query is safe to execute"""
        query_upper = query.upper()
        for keyword in settings.FORBIDDEN_KEYWORDS:
            if keyword in query_upper:
                return False
        if not query_upper.strip().startswith('SELECT'):
            return False
        if not QuerySafetyChecker.only_allowed_tables(query_upper):
            return False
        
        return True
    
    @staticmethod
    def only_allowed_tables(query: str) -> bool:
        """Check if query only references allowed tables"""
        patterns = [
            r'FROM\s+(\w+|`\w+`|\"\w+\"|\[\w+\])',
            r'JOIN\s+(\w+|`\w+`|\"\w+\"|\[\w+\])',
            r'UPDATE\s+(\w+|`\w+`|\"\w+\"|\[\w+\])',
            r'INTO\s+(\w+|`\w+`|\"\w+\"|\[\w+\])'
        ]
        
        tables_used = []
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                table_name = match.strip('`"[]') 
                tables_used.append(table_name.lower())
        for table in tables_used:
            if table not in [t.lower() for t in settings.ALLOWED_TABLES]:
                return False
        
        return True
    
    @staticmethod
    def add_safety_limits(query: str) -> str:
        """Add LIMIT clause to prevent large result sets"""
        query_upper = query.upper()
        
        if 'LIMIT' not in query_upper and 'SELECT' in query_upper:
            query += f" LIMIT {settings.MAX_ROWS}"
        return query