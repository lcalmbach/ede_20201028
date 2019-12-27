import streamlit as st

display = ("male", "female")

options = [0,1]

value = st.selectbox("gender", options, format_func=lambda x: display[x])

st.write(value)