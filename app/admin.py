import pandas as pd
import streamlit as st

from backend.db import get_db_schema, run_query

get_db_schema_btn = st.button("Create Knowledge Base of new DB.")

if get_db_schema_btn:
    get_db_schema()