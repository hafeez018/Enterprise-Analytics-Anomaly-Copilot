import os
import sqlite3
import pandas as pd
from core.security import SQLSecurityGuard


class DatabaseManager:
    def __init__(self, db_path: str = "data/product_metrics.db"):
        self.db_path = os.path.abspath(db_path)
        self.readonly_uri = f"file:{self.db_path}?mode=ro"

    def update_database(self, new_db_path: str):
        """Swaps the target database connection dynamically."""
        self.db_path = os.path.abspath(new_db_path)
        self.readonly_uri = f"file:{self.db_path}?mode=ro"

    def get_table_names(self) -> list[str]:
        """Dynamically retrieves all user tables regardless of industry domain."""
        with sqlite3.connect(self.readonly_uri, uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_schema(self) -> str:
        """Extracts complete DDL schema definition for LLM context injection."""
        with sqlite3.connect(self.readonly_uri, uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            )
            schema_ddl = [row[0] for row in cursor.fetchall() if row[0] is not None]
            return "\n\n".join(schema_ddl)

    def query_to_df(self, query: str) -> pd.DataFrame:
        """Validates AST and executes safely under engine-level read-only locks."""
        sanitized_sql = SQLSecurityGuard.validate_query(query)
        with sqlite3.connect(self.readonly_uri, uri=True, timeout=5.0) as conn:
            return pd.read_sql_query(sanitized_sql, conn)
