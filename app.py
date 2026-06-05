import streamlit as st
import pandas as pd

from src.database import initialise_db, get_or_create_user, save_checkin, get_checkins, get_all_users

# Initialise the database on startup
initialise_db()

st.title("Health Dashboard")
st.write("Welcome to your personal health check-in system!")

# Sidebar
st.sidebar.title("Settings")

from src.database import get_all_users

existing_users = get_all_users()

if existing_users:
    options = existing_users + ["➕ Add new user"]
    selection = st.sidebar.selectbox("Select user", options)

    if selection == "➕ Add new user":
        name = st.sidebar.text_input("Enter your name")
    else:
        name = selection
else:
    name = st.sidebar.text_input("Your name", value="Student")

if name:
    user_id = get_or_create_user(name)
    st.write(f"Hello, {name}!")

# Load this user's check-ins from the database
df = get_checkins(user_id)

# Energy line chart
st.subheader("Energy Levels — Last 30 Days")
if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    st.line_chart(df["energy_level"])
else:
    st.info("No data yet. Submit your first check-in below!")

# History table
st.subheader("Check-in History")
if not df.empty:
    st.dataframe(df[["energy_level", "stress_level", "heart_rate", "mood_text"]], use_container_width=True)
else:
    st.info("No history yet.")

# Risk score and check-in form
col1, col2 = st.columns(2)

with col1:
    st.subheader("Risk Score")
    threshold = st.slider("Sensitivity", min_value=1, max_value=10, value=5)
    risk_score = int((10 - threshold) * 10)
    st.metric(label="Current Risk Score", value=f"{risk_score}%")

with col2:
    st.subheader("Today's Check-in")
    mood = st.slider("Mood (1-10)", min_value=1, max_value=10, value=5)
    energy_today = st.slider("Energy (1-10)", min_value=1, max_value=10, value=5)
    stress_today = st.slider("Stress (1-10)", min_value=1, max_value=10, value=5)
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=72)
    note = st.text_input("Any notes for today?")

    if "submissions" not in st.session_state:
        st.session_state.submissions = 0

    if st.button("Submit"):
        save_checkin(
            user_id=user_id,
            energy=float(energy_today),
            stress=float(stress_today),
            heart_rate=float(heart_rate),
            mood_text=note
        )
        st.session_state.submissions += 1
        st.success(f"Saved! Mood: {mood}, Energy: {energy_today}")
        st.rerun()

    if st.session_state.submissions > 0:
        st.write(f"Total check-ins this session: {st.session_state.submissions}")




