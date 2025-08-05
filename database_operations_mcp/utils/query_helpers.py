"""
Query helper utilities for database operations.

Provides safe query building, validation, and formatting utilities.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of database queries."""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    UNKNOWN = "UNKNOWN"

def detect_query_type(query: str) -> QueryType:
    """Detect the type of SQL query."""
    query_clean = query.strip().upper()
    
    if query_clean.startswith('SELECT') or query_clean.startswith('WITH'):
        return QueryType.SELECT
    elif query_clean.startswith('INSERT'):
        return QueryType.INSERT
    elif query_clean.startswith('UPDATE'):
        return QueryType.UPDATE
    elif query_clean.startswith('DELETE'):
        return QueryType.DELETE
    elif query_clean.startswith('CREATE'):
        return QueryType.CREATE
    elif query_clean.startswith('DROP'):
        return QueryType.DROP
    elif query_clean.startswith('ALTER'):
        return QueryType.ALTER
    else:
        return QueryType.UNKNOWN

def is_safe_query(query: str, allow_modifications: bool = False) -> Tuple[bool, Optional[str]]:
    """Check if a query is safe to execute.
    
    Args:
        query: SQL query to validate
        allow_modifications: Whether to allow INSERT/UPDATE/DELETE queries
        
    Returns:
        Tuple of (is_safe, error_message)
    """
    try:
        query_type = detect_query_type(query)
        
        # Check for dangerous operations
        dangerous_patterns = [
            r'\bDROP\s+TABLE\b',
            r'\bDROP\s+DATABASE\b',
            r'\bTRUNCATE\b',
            r'\bDELETE\s+FROM\s+\w+\s*;?\s*$',  # DELETE without WHERE
            r'\bUPDATE\s+\w+\s+SET\s+.*\s*;?\s*$',  # UPDATE without WHERE
            r';\s*DROP\b',  # SQL injection attempt
            r';\s*DELETE\b',  # SQL injection attempt
            r'--',  # SQL comments (potential injection)
            r'/\*.*\*/',  # Block comments
        ]
        
        query_upper = query.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return False, f"Query contains potentially dangerous operation"
        
        # Check query type permissions
        if not allow_modifications:
            if query_type in [QueryType.INSERT, QueryType.UPDATE, QueryType.DELETE, 
                            QueryType.CREATE, QueryType.DROP, QueryType.ALTER]:
                return False, f"Modification queries not allowed: {query_type.value}"
        
        # Additional safety checks
        if len(query) > 10000:
            return False, "Query is too long (>10000 characters)"
        
        # Check for multiple statements (basic check)
        if ';' in query.rstrip(';'):
            return False, "Multiple statements not allowed for safety"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Error validating query safety: {e}")
        return False, f"Query validation error: {str(e)}"

def sanitize_identifier(identifier: str) -> str:
    """Sanitize database identifiers (table names, column names)."""
    # Remove any characters that aren't alphanumeric or underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '', identifier)
    
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = '_' + sanitized
    
    return sanitized

def build_select_query(
    table_name: str,
    columns: Optional[List[str]] = None,
    where_conditions: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    limit: Optional[int] = None,
    database_name: Optional[str] = None
) -> Tuple[str, Dict[str, Any]]:
    """Build a safe SELECT query with parameters.
    
    Returns:
        Tuple of (query_string, parameters_dict)
    """
    # Sanitize table name
    table_name = sanitize_identifier(table_name)
    if database_name:
        database_name = sanitize_identifier(database_name)
        table_ref = f"{database_name}.{table_name}"
    else:
        table_ref = table_name
    
    # Build column list
    if columns:
        column_list = ", ".join(sanitize_identifier(col) for col in columns)
    else:
        column_list = "*"
    
    # Start building query
    query = f"SELECT {column_list} FROM {table_ref}"
    parameters = {}
    
    # Add WHERE conditions
    if where_conditions:
        where_parts = []
        for i, (column, value) in enumerate(where_conditions.items()):
            column_safe = sanitize_identifier(column)
            param_name = f"param_{i}"
            where_parts.append(f"{column_safe} = :{param_name}")
            parameters[param_name] = value
        
        if where_parts:
            query += " WHERE " + " AND ".join(where_parts)
    
    # Add ORDER BY
    if order_by:
        order_by_safe = sanitize_identifier(order_by)
        query += f" ORDER BY {order_by_safe}"
    
    # Add LIMIT
    if limit:
        query += f" LIMIT {int(limit)}"
    
    return query, parameters

def format_query_for_display(query: str, max_length: int = 200) -> str:
    """Format query for display purposes."""
    # Remove extra whitespace
    formatted = re.sub(r'\s+', ' ', query.strip())
    
    # Truncate if too long
    if len(formatted) > max_length:
        formatted = formatted[:max_length-3] + "..."
    
    return formatted

def extract_table_names(query: str) -> List[str]:
    """Extract table names from a SQL query (basic implementation)."""
    tables = []
    
    # Simple regex patterns for common SQL statements
    patterns = [
        r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'DELETE\s+FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)'
    ]
    
    query_upper = query.upper()
    for pattern in patterns:
        matches = re.findall(pattern, query_upper)
        tables.extend(matches)
    
    # Remove duplicates and return
    return list(set(tables))

def add_limit_to_query(query: str, limit: int, database_type: str = "sqlite") -> str:
    """Add LIMIT clause to a query based on database type."""
    if not limit or limit <= 0:
        return query
    
    query_lower = query.lower().strip()
    
    # Check if LIMIT already exists
    if "limit" in query_lower:
        return query
    
    # Add LIMIT based on database type
    if database_type.lower() in ["postgresql", "mysql", "sqlite"]:
        return f"{query.rstrip(';')} LIMIT {limit}"
    elif database_type.lower() == "sqlserver":
        # SQL Server uses TOP
        if query_lower.startswith("select"):
            return query.replace("SELECT", f"SELECT TOP {limit}", 1)
        return query
    else:
        # Default to standard LIMIT
        return f"{query.rstrip(';')} LIMIT {limit}"

def validate_column_name(column_name: str) -> bool:
    """Validate if a column name is safe to use."""
    # Must start with letter or underscore
    if not re.match(r'^[a-zA-Z_]', column_name):
        return False
    
    # Must contain only letters, numbers, and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', column_name):
        return False
    
    # Check length
    if len(column_name) > 64:  # Most databases have this limit
        return False
    
    # Check for SQL reserved words (basic list)
    reserved_words = {
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
        'ALTER', 'TABLE', 'INDEX', 'VIEW', 'TRIGGER', 'PROCEDURE', 'FUNCTION',
        'DATABASE', 'SCHEMA', 'USER', 'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK'
    }
    
    if column_name.upper() in reserved_words:
        return False
    
    return True

def escape_sql_value(value: Any) -> str:
    """Safely escape SQL values for display purposes only."""
    if value is None:
        return "NULL"
    elif isinstance(value, str):
        # Escape single quotes by doubling them
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    else:
        # Convert to string and escape
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"
