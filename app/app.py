import pandas as pd
import streamlit as st
import time
import weaviate

from numpy.random import default_rng as rng
from backend.chat import query_llm
from backend.funcs import extract_sql
from backend.db import run_query
from backend.rag import build_sql_prompt, get_schema_context


#### MANAGING STREAMLIT SESSION_STATE
if 'msg_hist' not in st.session_state:
    st.session_state['msg_hist'] = [{'role': 'assistant', 'content': 'Hello! Welcome to Text-2-SQL. How can I help you?'}]

newQuery = False

#### STREAMLIT UI COMPONENTS

# Setting page configurations
st.set_page_config(layout="wide")

# Setting the app title
st.title("Text-2-SQL")

# Reset button to clear chat history
clear_btn = st.button('Clear chat', type='primary')
if clear_btn:
    st.session_state.msg_hist = []
    st.rerun()

# with st.container(height=75, border=True):
#     prompt = 

with st.container(height=500, border=False):

    # Using columns for page layout
    c1, c2 = st.columns([1, 1], gap='medium', border=True)

    with c1:
        # Display chat history
        for message in st.session_state.msg_hist:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

        # Logic to run when user submits prompt
        if prompt := st.chat_input("Say something", accept_file=False):
            
            # Display the new prompt submitted
            st.chat_message('user').write(prompt)
            # Add the message to the session state
            st.session_state.msg_hist.append({'role': 'user', 'content': prompt})

            # Get the most revelant schema from the vector DB
            with weaviate.connect_to_local() as client:
                schema_context = get_schema_context(client, prompt)
            
            # Add system instructions to the LLM along with the extracted context and user prompt.
            modified_prompt = build_sql_prompt(prompt, schema_context=schema_context)

            # Used for logging
            print(f'Modified prompt = {modified_prompt}')

            # Query the LLM
            with st.spinner("Thinking...", show_time=True):
                response = query_llm(modified_prompt)

            # Extract the SQL from the generated response
            try:
                cleaned_query = extract_sql(response.message.content)
                newQuery = True
                print(f'Extracted Query: \n {cleaned_query}')
            except:
                print('Response did not include an SQL query or SQL not enclosed in ```sql ```.')

            # Display the response return by the LLM
            st.chat_message('assistant').write(response.message.content)
            # Store response in message history
            st.session_state.msg_hist.append({'role': 'assistant', 'content': response.message.content})
            


    with c2:

        # st.write("SQL Results here.")

        sql_query = st.chat_input(
            "Write SQL Query here",
            accept_file=False
        )

        if sql_query:
            df = run_query(sql_query)
            st.dataframe(df, hide_index=True)

        # if newQuery:

        #     df = run_query(cleaned_query)
        #     st.dataframe(df, hide_index=True)
