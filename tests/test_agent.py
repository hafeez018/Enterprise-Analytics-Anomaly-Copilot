from unittest.mock import MagicMock, patch

from core.gemini_agent import GeminiAnalyticsAgent


def test_text_to_sql_cleaning():
    agent = GeminiAnalyticsAgent(api_key="mock-api-key")

    # Mock LLM output that wraps SQL in markdown blocks
    mock_response = MagicMock()
    mock_response.text = "```sql\nSELECT * FROM users LIMIT 10;\n```"

    with patch.object(
        agent.client.models, "generate_content", return_value=mock_response
    ):
        sql = agent.text_to_sql("Show 10 users", schema="CREATE TABLE users (id INT);")
        assert sql == "SELECT * FROM users LIMIT 10;"


def test_self_healing_resolves_error_on_second_attempt():
    agent = GeminiAnalyticsAgent(api_key="mock-api-key")

    # Simulate first response failing with invalid column, second response succeeding
    bad_response = MagicMock()
    bad_response.text = "```sql\nSELECT invalid_column FROM users;\n```"

    good_response = MagicMock()
    good_response.text = "```sql\nSELECT user_id FROM users;\n```"

    # Route consecutive LLM calls
    with patch.object(
        agent.client.models,
        "generate_content",
        side_effect=[bad_response, good_response],
    ):
        df, final_sql, logs = agent.execute_with_self_healing(
            user_question="Get user IDs",
            schema="CREATE TABLE users (user_id INTEGER PRIMARY KEY);",
            db_path="data/product_metrics.db",
            max_retries=3,
        )

        # Verify self-healing resolved on attempt #2
        assert len(logs) == 2
        assert logs[0]["status"] == "failed"
        assert logs[1]["status"] == "success"
        assert "user_id" in final_sql
