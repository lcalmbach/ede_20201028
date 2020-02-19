import streamlit as st
import SessionState

session = SessionState.get(code='some c++ code')
a = st.radio("Edit or show", ['Edit', 'Show'], 1)
if a == 'Edit':
    session.code = st.text_input('Edit code', session.code)
else:
    st.write(session.code)