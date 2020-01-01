import streamlit as st

options = (8, 9)

display = {8: 'male', 9: 'female'}

value = st.selectbox("gender", options, format_func=lambda x: display[x])

st.write(value)