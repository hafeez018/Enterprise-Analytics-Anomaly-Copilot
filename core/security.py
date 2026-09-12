import sqlglot
from sqlglot import exp


class SQLSecurityError(Exception):
    """Raised when an unapproved or dangerous SQL structure is detected."""


class SQLSecurityGuard:
    # Whitelisted top-level expression types
    ALLOWED_ROOT_TYPES = (
        exp.Select,
        exp.Union,
    )

    # Blacklisted statement types that should never appear anywhere in the AST
    FORBIDDEN_EXPRESSIONS = (
        exp.Drop,
        exp.Delete,
        exp.Insert,
        exp.Update,
        exp.Alter,
        exp.Create,
        exp.Command,
        exp.Pragma,
    )

    # Forbidden Tables
    FORBIDDEN_TABLES = {
        "sqlite_master",
        "sqlite_schema",
        "sqlite_temp_master",
        "sqlite_sequence",
    }

    @classmethod
    def validate_query(cls, sql_query: str, max_limit: int = 1000) -> str:
        """
        Parses, validates, and sanitizes a query.
        Returns the safe SQL string or raises SQLSecurityError.
        """
        clean_sql = sql_query.strip().rstrip(";")

        # 1. Parse into AST
        try:
            parsed_statements = sqlglot.parse(clean_sql, read="sqlite")
        except Exception as e:
            raise SQLSecurityError(f"SQL Syntax parsing failed: {e}")

        # 2. Block stacked queries (e.g. 'SELECT 1; DROP TABLE users')
        if len(parsed_statements) != 1:
            raise SQLSecurityError(
                f"Multi-statement execution rejected ({len(parsed_statements)} statements found). Only single queries allowed."
            )

        statement = parsed_statements[0]
        if statement is None:
            raise SQLSecurityError("Empty query provided.")

        # 3. Verify top-level node is a read-only query (Select or Union)
        if not isinstance(statement, cls.ALLOWED_ROOT_TYPES):
            raise SQLSecurityError(
                f"Forbidden statement type '{type(statement).__name__}'. Only read-only SELECT/UNION queries allowed."
            )

        # 4. Deep-scan AST for any embedded mutations (e.g., inside CTEs or subqueries)
        for forbidden in cls.FORBIDDEN_EXPRESSIONS:
            if statement.find(forbidden):
                raise SQLSecurityError(
                    f"Dangerous operation detected: {forbidden.__name__}"
                )

        # 5. Guardrail: Enforce a maximum LIMIT to prevent memory exhaustion
        if not statement.find(exp.Limit):
            statement = statement.limit(max_limit)

        return statement.sql(dialect="sqlite")

        # 6. Scan all table identifiers in the AST
        for table in statement.find_all(exp.Table):
            if table.name.lower() in FORBIDDEN_TABLES:
                raise SQLSecurityError(
                    f"Access to internal system catalog table '{table.name}' is forbidden."
                )
