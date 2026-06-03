
import streamlit as st
import numpy as np
import pandas as pd

st.title("Health Dashboard")
st.write("Welcome to you personal health check-in system!")


st.sidebar.title("Settings")
name = st.sidebar.text_input("Your name", value="Student")
st.write(f"Hello, {name}!")



st.subheader("Energy Levels — Last 30 Days")

np.random.seed(42)
days = pd.date_range(end=pd.Timestamp.today(), periods=30)
energy = np.random.randint(4, 10, size=30)

chart_data = pd.DataFrame({"Energy": energy}, index=days)
st.line_chart(chart_data)

st.subheader("Risk Score")

threshold = st.slider("Sensitivity", min_value=1, max_value=10, value=5)
risk_score = int((10 - threshold) * 10)

st.metric(label="Current Risk Score", value=f"{risk_score}%")


st.subheader("Today's Check-in")

mood = st.slider("Mood (1-10)", min_value=1, max_value=10, value=5)
energy_today = st.slider("Energy (1-10)", min_value=1, max_value=10, value=5)
note = st.text_input("Any notes for today?")

if "submissions" not in st.session_state:
    st.session_state.submissions = 0

if st.button("Submit"):
    st.session_state.submissions += 1
    st.success(f"Check-in saved! Mood: {mood}, Energy: {energy_today}, Note: {note}")

if st.session_state.submissions > 0:
    st.write(f"Total check-ins this session: {st.session_state.submissions}")  