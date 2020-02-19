import streamlit as st
import uuid

ELEMENTS = ["foo", "bar", "hello", "world"]

def bar(sel, key):
    selected = st.selectbox("Yo Yo:", ELEMENTS, index=sel, key=key)
    return selected


st.write("# ABC")

boxes = [0, 1, 2, 1, 1, 0]
results = [0, 0, 0, 0, 0, 0]
for i in range(4):
    results[i] = bar(boxes[i], 'sel' + str(i))
    st.write(results[i])
