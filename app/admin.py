import pandas as pd
import streamlit as st
import weaviate
import sys

from sentence_transformers import SentenceTransformer
from backend.db import get_db_schema, run_query
from backend.create_kb import parse_db_schema_markdown, create_embeddings, \
                        setup_weaviate_collection, batch_insert_embeddings, test_query, \
                        incremental_upsert, auto_delete_missing_tables

collection_name = 'DBSchema'

if 'md_file_path' in st.session_state:
    md_file_path = st.session_state['md_file_path']

get_db_schema_btn = st.button("Create DB Schema files of new DB.")
if get_db_schema_btn:
    md_file_path = get_db_schema()
    st.session_state['md_file_path'] = md_file_path

upload_embeddings = st.button("Upload vector embeddings.")
if upload_embeddings:

    # Parse tables metadata from markdown file
    parsed_tables = parse_db_schema_markdown(md_file_path)
    table_names = [t["tableName"] for t in parsed_tables]

    # Create embeddings model
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # Setup weaviate collection
    try:
        with weaviate.connect_to_local() as client:
            print('✅ Connected to Weaviate.')
            setup_weaviate_collection(client, collection_name)

            # Auto-delete before upsert
            auto_delete_missing_tables(client, collection_name, table_names)

            # Insert data
            incremental_upsert(client, collection_name, parsed_tables, model)

    except Exception as e:
        sys.exit(f"❌ Could not connect to Weaviate: {e}")


vector_query = st.chat_input(
    "Insert vector DB Query here.",
    accept_file=False,
)

if vector_query:
    with weaviate.connect_to_local() as client:
        test_query(client, collection_name, vector_query)