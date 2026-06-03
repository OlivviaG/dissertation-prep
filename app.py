
import streamlit as st

st.title("Health Dashboard")
st.write("Welcome to you personal health check-in system!")


st.sidebar.title("Settings")
name = st.sidebar.text_input("Your name", value="Student")
st.write(f"Hello, {name}!")