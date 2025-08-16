import pandas as pd
import re

def extract_sql(response_text):
    
    # Extract SQL between triple backticks
    match = re.search(r"```sql\s*(.*?)\s*```", response_text, re.DOTALL)
    if not match:
        raise ValueError("No SQL query found in LLM response")

    sql_query = match.group(1).strip()

    # Convert EXTRACT syntax to SQLite's strftime
    # Convert MONTH
    sql_query = re.sub(
        r"EXTRACT\s*\(\s*MONTH\s+FROM\s+([^)]+)\)",
        r"strftime('%m', \1)",
        sql_query,
        flags=re.IGNORECASE
    )

    # Convert YEAR
    sql_query = re.sub(
        r"EXTRACT\s*\(\s*YEAR\s+FROM\s+([^)]+)\)",
        r"strftime('%Y', \1)",
        sql_query,
        flags=re.IGNORECASE
    )

    # Ensure numeric comparison works in SQLite
    sql_query = sql_query.replace("= 7", "= '07'")  # months need zero-padded strings
    sql_query = sql_query.replace("= 2025", "= '2025'")  # years as strings

    # # Run in SQLite
    # conn = sqlite3.connect("my_database.db")
    # df = pd.read_sql_query(sql_query, conn)
    # conn.close()

    return sql_query