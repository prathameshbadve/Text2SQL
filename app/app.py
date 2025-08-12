import pandas as pd
import streamlit as st
import time

from numpy.random import default_rng as rng
from backend.chat import query_llm
from backend.funcs import run_sql

# Setting page configurations
st.set_page_config(layout="wide")

# Setting the app title
st.title("Text-2-SQL")

# Getting data from session_state, otherwise initializing
if 'msg_hist' not in st.session_state:
    msg_hist = {'user': [], 'assistant': []}
else:
    msg_hist = st.session_state['msg_hist']


# Reset button to clear chat history
clear_btn = st.button('Clear chat', type='primary')
if clear_btn:
    st.session_state.msg_hist = {'user': [], 'assistant': []}
    st.rerun()


with st.container(height=500, border=False):

    # Using columns for page layout
    c1, c2 = st.columns([1, 1], gap='medium', border=True)

    with c1:

        # Chat input box for the user
        prompt = st.chat_input(
            "Say something",
            accept_file=False,
        )

        st.chat_message('assistant').write('Hello! Welcome to Text-2-SQL. How can I help you?')

        # Display chat history
        for i, _ in enumerate(msg_hist['user']):
            st.chat_message('user').write(msg_hist['user'][i])
            st.chat_message('assistant').write(msg_hist['assistant'][i])

        # Logic to run when user submits prompt
        if prompt:
            msg_hist['user'].append(prompt)                             # Add user message to the history
            st.chat_message('user').write(prompt)

            with st.spinner("Thinking...", show_time=True):
                response = query_llm(prompt)

            print(f'Response = {response}')

            msg_hist['assistant'].append(response.message.content)          # Add assistant message to history
            st.chat_message('assistant').write(response.message.content)
            st.session_state.msg_hist = msg_hist                        # Store message history to session_state


    with c2:
        run_sql_button = st.button("Run SQL", type='secondary')

        if run_sql_button:
            df = run_sql()

            st.dataframe(df, hide_index=True)
