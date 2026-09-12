import os
import re
import sqlite3
import pandas as pd
from core.security import SQLSecurityError, SQLSecurityGuard
from google import genai
from google.genai import types


class GeminiAnalyticsAgent:
    def __init__(self, api_key: str, model: str = "gemini-3.6-flash"):
        self.client = genai.Client(api_key=api_key)
        # Updated to the current active flash model
        self.model = os.environ.get("GEMINI_MODEL", model)

    def _extract_sql(self, text: str) -> str:
        """Helper to extract pure SQL from model markdown blocks."""
        match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else text.strip()

    def text_to_sql(self, user_question: str, schema: str) -> str:
        """Initial SQL generation."""
        prompt = f"""
You are an expert Data Engineer. Write a valid, read-only SQLite query to answer the user's question.
Return ONLY raw SQL code inside a ```sql code block. Do NOT include markdown text outside the block.

SCHEMA:
{schema}

USER QUESTION:
{user_question}
"""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.0),
        )
        return self._extract_sql(response.text)

    def heal_sql(
        self,
        user_question: str,
        schema: str,
        failed_sql: str,
        error_message: str,
    ) -> str:
        """Reflexion step: generates a corrected query using execution error context."""
        prompt = f"""
You previously wrote an invalid SQLite query that failed to execute. Fix the query.

SCHEMA:
{schema}

USER QUESTION:
{user_question}

FAILED SQL QUERY:
{failed_sql}

SQLITE ERROR MESSAGE:
{error_message}

CRITICAL RULES:
1. Return ONLY the corrected SQL wrapped in a ```sql code block.
2. Check table names and column names against the SCHEMA.
3. Ensure syntax adheres strictly to SQLite (e.g., use strftime for dates, proper GROUP BY rules).
"""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.0),
        )
        return self._extract_sql(response.text)

    def execute_with_self_healing(
        self, user_question: str, schema: str, db_path: str, max_retries: int = 3
    ) -> tuple[pd.DataFrame, str, list[dict[str, str]]]:
        """Executes query against SQLite with an autonomous self-healing loop.

        Returns: (result_df, final_sql, logs)
        """
        logs = []
        current_sql = self.text_to_sql(user_question, schema)

        for attempt in range(1, max_retries + 1):
            try:
                # 1. Run security validation
                sanitized_sql = SQLSecurityGuard.validate_query(current_sql)

                # 2. Execute against read-only database
                with sqlite3.connect(
                    f"file:{db_path}?mode=ro", uri=True, timeout=5.0
                ) as conn:
                    df = pd.read_sql_query(sanitized_sql, conn)

                logs.append(
                    {
                        "attempt": attempt,
                        "status": "success",
                        "sql": sanitized_sql,
                        "error": None,
                    }
                )
                return df, sanitized_sql, logs

            except (
                SQLSecurityError,
                sqlite3.Error,
                pd.errors.DatabaseError,
            ) as err:
                err_msg = str(err)
                logs.append(
                    {
                        "attempt": attempt,
                        "status": "failed",
                        "sql": current_sql,
                        "error": err_msg,
                    }
                )

                if attempt < max_retries:
                    current_sql = self.heal_sql(
                        user_question=user_question,
                        schema=schema,
                        failed_sql=current_sql,
                        error_message=(
                            f"SECURITY/EXECUTION ERROR: {err_msg}. "
                            "Ensure the query is strictly a single SELECT statement without mutations."
                        ),
                    )
                else:
                    raise RuntimeError(
                        f"Execution halted after {max_retries} attempts. Last violation: {err_msg}"
                    )

    def generate_executive_insights(self, question: str, data_summary: str) -> str:
        prompt = f"""
You are a Senior Product Analytics Manager. Summarize the following data to answer the stakeholder's question.
Highlight key changes, calculate lifts/drops, and provide 2 prioritized product recommendations.
Format with clean bullet points.

USER QUESTION:
{question}

DATA SUMMARY:
{data_summary}
"""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.2),
        )
        return response.text
