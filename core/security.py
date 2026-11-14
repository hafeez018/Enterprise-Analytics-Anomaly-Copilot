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

    # Statement types that should never appear anywhere in the AST
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

    # Exact forbidden table names
    FORBIDDEN_TABLES = {
        "sqlite_master",
        "sqlite_schema",
        "sqlite_temp_master",
        "sqlite_sequence",
    }

    # Forbidden prefixes / function names (catch sqlite_* tables and pragma_* functions)
    FORBIDDEN_PREFIXES = ("sqlite_", "pragma_")
    FORBIDDEN_FUNCTIONS = {"load_extension"}

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

        # 2. Block stacked queries
        if len(parsed_statements) != 1:
            raise SQLSecurityError(
                f"Multi-statement execution rejected ({len(parsed_statements)} statements found). Only single queries allowed."
            )

        statement = parsed_statements[0]
        if statement is None:
            raise SQLSecurityError("Empty query provided.")

        # 3. Top-level node must be a read-only query
        if not isinstance(statement, cls.ALLOWED_ROOT_TYPES):
            raise SQLSecurityError(
                f"Forbidden statement type '{type(statement).__name__}'. Only read-only SELECT/UNION queries allowed."
            )

        # 4. Deep-scan AST for embedded mutations
        for forbidden in cls.FORBIDDEN_EXPRESSIONS:
            if statement.find(forbidden):
                raise SQLSecurityError(
                    f"Dangerous operation detected: {forbidden.__name__}"
                )

        # 5. Block system catalog access (tables)
        for table in statement.find_all(exp.Table):
            name = (table.name or "").lower()
            if name in cls.FORBIDDEN_TABLES or name.startswith(cls.FORBIDDEN_PREFIXES):
                raise SQLSecurityError(
                    f"Access to internal system catalog table '{table.name}' is forbidden."
                )

        # 6. Block dangerous functions (pragma_table_info(...), load_extension(...))
        for func in statement.find_all(exp.Anonymous):
            fname = str(func.name).lower()
            if fname in cls.FORBIDDEN_FUNCTIONS or fname.startswith(
                cls.FORBIDDEN_PREFIXES
            ):
                raise SQLSecurityError(
                    f"Access to internal system catalog function '{func.name}' is forbidden."
                )

        # 7. Enforce a maximum LIMIT on the outer query
        if not statement.args.get("limit"):
            statement = statement.limit(max_limit)

        return statement.sql(dialect="sqlite")
