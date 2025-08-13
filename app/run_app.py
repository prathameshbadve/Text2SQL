import streamlit as st

pages = st.navigation(
    [
        st.Page("app,py", title="Main App"),
        st.Page("admin.py", title="Admin")
    ]
)

pages.run()