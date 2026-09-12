import pytest

from core.security import SQLSecurityError, SQLSecurityGuard


@pytest.mark.parametrize(
    "dangerous_sql",
    [
        "DROP TABLE users;",
        "DELETE FROM orders WHERE user_id = 1;",
        "UPDATE users SET plan = 'Pro';",
        "INSERT INTO users VALUES (1, '2026-09-01', 'iOS', 'Free');",
        "ALTER TABLE events ADD COLUMN test TEXT;",
        "SELECT * FROM users; DROP TABLE orders;",
        "SELECT 1; SELECT 2;",
    ],
)
def test_blocks_mutations_and_stacked_queries(dangerous_sql: str):
    with pytest.raises(SQLSecurityError):
        SQLSecurityGuard.validate_query(dangerous_sql)


@pytest.mark.parametrize(
    "catalog_sql",
    [
        "SELECT * FROM sqlite_master;",
        "SELECT sql FROM sqlite_schema WHERE type='table';",
        "SELECT * FROM sqlite_temp_master;",
    ],
)
def test_blocks_system_catalog_exfiltration(catalog_sql: str):
    with pytest.raises(SQLSecurityError, match="Access to internal system catalog"):
        SQLSecurityGuard.validate_query(catalog_sql)


@pytest.mark.parametrize(
    "safe_analytical_sql",
    [
        "SELECT user_id, drop_rate FROM conversion_funnels;",
        "SELECT * FROM events WHERE event_name = 'drop_pin';",
        "SELECT message FROM tickets WHERE message = 'Please delete my account';",
        "SELECT device, COUNT(*) FROM users GROUP BY device;",
    ],
)
def test_avoids_false_positives_on_safe_analytical_queries(safe_analytical_sql: str):
    # AST parser must recognize keywords inside column names or string literals as safe
    sanitized = SQLSecurityGuard.validate_query(safe_analytical_sql)
    assert sanitized is not None
    assert "LIMIT" in sanitized.upper()


def test_enforces_limit_boundary():
    query = "SELECT user_id FROM users"
    sanitized = SQLSecurityGuard.validate_query(query, max_limit=500)
    assert "LIMIT 500" in sanitized.upper()
