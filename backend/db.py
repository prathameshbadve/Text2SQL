import os
import pandas as pd
import streamlit as st
import json
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

# Loading environement variables
load_dotenv()

# Checking if this dev or prod environment
ENV = os.getenv("ENV")

# Storing DB URL
if ENV == 'dev':
    DATABASE_URL = os.getenv("DEV_DATABASE_URL")
else:
    DATABASE_URL = os.getenv("PROD_DATABASE_URL")

# Raise error if DB URL is not present in .env file
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables.")

# Create connection engine with pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # number of connections in pool
    max_overflow=20,       # extra connections if pool is full
    pool_timeout=30,       # wait time before giving up
    pool_recycle=1800      # refresh connections every 30 min
)

# Function to run SQL queries via the above engine
@st.cache_data(ttl=300, show_spinner=True)
def run_query(query: str, params: dict = None) -> pd.DataFrame:

    """Run a SQL query and return a DataFrame."""
    
    with engine.connect() as conn:
    
        result = conn.execute(text(query), params or {})
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        
        print("Fetched data from DB.")
    
    return df

# Function to get schema of databases
def get_db_schema():

    inspector = inspect(engine)
    
    # Schema data will be populated in this dictionary
    schema_data = {}
    Path("backend/db_metadata").mkdir(parents=True, exist_ok=True)

    for table in inspector.get_table_names():

        columns = inspector.get_columns(table)
        fks = inspector.get_foreign_keys(table)
        pks = inspector.get_pk_constraint(table)

        schema_data[table] = {
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": str(col["default"]),
                }
                for col in columns
            ],
            "primary_key": pks.get("constrained_columns", []),
            "foreign_keys": [
                {
                    "column": fk["constrained_columns"],
                    "references": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                }
                for fk in fks
            ],
        }

    # Save as JSON
    Path("backend/db_metadata/db_schema.json").write_text(json.dumps(schema_data, indent=2))
    print("JSON file created.")


    markdown_lines = ["# Database Schema\n"]

    for table, meta in schema_data.items():
        markdown_lines.append(f"## Table: {table}\n")
        markdown_lines.append("| Column | Type | Nullable | Default |")
        markdown_lines.append("|--------|------|----------|---------|")
        for col in meta["columns"]:
            markdown_lines.append(
                f"| {col['name']} | {col['type']} | {col['nullable']} | {col['default']} |"
            )

        if meta["primary_key"]:
            markdown_lines.append(f"\n**Primary Key:** {', '.join(meta['primary_key'])}")

        if meta["foreign_keys"]:
            markdown_lines.append("\n**Foreign Keys:**")
            for fk in meta["foreign_keys"]:
                markdown_lines.append(
                    f"- {fk['column']} → {fk['references']}({', '.join(fk['referred_columns'])})"
                )

        markdown_lines.append("\n---\n")

    # Save markdown
    Path("backend/db_metadata/db_schema.md").write_text("\n".join(markdown_lines))
    md_file_path = "backend/db_metadata/db_schema.md"
    print(f"Markdown file created at {md_file_path}")

    return md_file_path