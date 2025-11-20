"""Prompt used for this code generation task: "Create a simple Streamlit app that 
includes a form with fields for a user's name and age. When the form is submitted, 
display a greeting message that includes the user's name and age."
"""


import streamlit as st

st.title("Greeting Form")

# Create a form context
with st.form(key="greeting_form"):
    name = st.text_input("Enter your name")
    age = st.slider("Select your age", min_value=1, max_value=100, value=25)
    submit_button = st.form_submit_button(label="Say Hello")

if submit_button:
    st.success(f"Hello {name}! You are {age} years old.")
