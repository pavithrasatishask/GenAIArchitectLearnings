import streamlit as st 

st.title("My First Streamlit App")
name = st.text_input("Enter your name")

if st.button("Say Hello"):
    if name:
        st.success(f"Hello {name}! Welcome to Streamlit.")
    else:
        st.warning("Please enter your name.")