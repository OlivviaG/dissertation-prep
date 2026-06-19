import streamlit as st
import pandas as pd

from src.database import initialise_db, get_or_create_user, save_checkin, get_checkins, get_all_users
from src.nlp import analyse_sentiment_transformer, analyse_sentiment_VADER
from src.time_series import generate_fake_data, compute_rolling_stats, flag_anomalies, plot_user_baseline
from src.anomaly_detection import compute_zscore, flag_anomalies_zscore, run_isolation_forest
import plotly.graph_objects as go
import requests

# Initialise the database on startup
initialise_db()

st.title("Health Dashboard")
st.write("Welcome to your personal health check-in system!")

# Sidebar
st.sidebar.title("Settings")


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
    st.dataframe(df[["energy_level", "stress_level", "heart_rate", "mood_text",
                     "vader_compound", "transformer_label"]], use_container_width=True)
else:
    st.info("No history yet.")

# Risk score and check-in form
col1, col2 = st.columns(2)

with col1:
    st.subheader("Risk Score")
    risk_response = requests.get(f"http://127.0.0.1:8000/users/{user_id}/risk")
    
    risk = risk_response.json()
    risk_score = risk['risk_score']
    status = risk['status']

    if risk_score is None: 
        st.text("No data to calculated risk score")
    else: 
        st.metric(label="Current Risk Score", value=f"{risk_score}%")
        if status == "normal":
            st.success(f"Status: {status}")
        elif status == "mild concern":
            st.warning(f"Status: {status}")
        else:
            st.error(f"Status: {status}")
        

with col2:
    st.subheader("Today's Check-in")
    mood = st.slider("Mood (1-10)", min_value=1, max_value=10, value=5)
    energy_today = st.slider("Energy (1-10)", min_value=1, max_value=10, value=5)
    stress_today = st.slider("Stress (1-10)", min_value=1, max_value=10, value=5)
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=72)
    note = st.text_input("Any notes for today?")

    if "submissions" not in st.session_state:
        st.session_state.submissions = 0

# This is the button section 


    if st.button("Submit"):
        response = requests.post(                   # Calls the API and tries that. 
            "http://127.0.0.1:8000/checkin",
            json={
                "user_id": user_id,
                "energy_level": energy_today,
                "stress_level": stress_today,
                "heart_rate": heart_rate,
                "mood_text": note,
            },
        )
        result = response.json()
        st.session_state.submissions += 1
        st.rerun()
    
    # Latest sentiment verdict — runs every rerun, reads from the DB
    history = get_checkins(user_id)
    if not history.empty:
        latest = history.iloc[-1]
        if pd.notna(latest["vader_compound"]):
            c = latest["vader_compound"]
            detail = f"VADER: {c:.2f} | Transformer: {latest['transformer_label']} ({latest['transformer_score']:.2f})"
            if c >= 0.05:
                st.success(f"Sentiment: Positive — {detail}")
            elif c <= -0.05:
                st.error(f"Sentiment: Negative — {detail}")
            else:
                st.warning(f"Sentiment: Neutral — {detail}")
        else:
            st.info("No mood text on the latest check-in — no sentiment recorded.")

    


st.subheader("Personal Baseline Analysis")

selected_user = st.selectbox("Select synthetic user", ["User A", "User B", "User C"])

profiles = {
    "User A": dict(mean=65, std=3),
    "User B": dict(mean=80, std=12),
    "User C": dict(mean=72, std=7, anomaly_start=45, anomaly_mean=95)
}

profile = profiles[selected_user]
df_ts = generate_fake_data(**profile)
df_ts = compute_rolling_stats(df_ts)
df_ts = flag_anomalies(df_ts)

fig = plot_user_baseline(df_ts, user_name=selected_user)
st.plotly_chart(fig, use_container_width=True)

anomaly_count = df_ts['is_anomaly'].sum()
st.metric("Anomalies Detected", int(anomaly_count))



st.subheader("Anomaly Detection Comparison")

selected_user_anomaly = st.selectbox(
    "Select user for anomaly detection",
    ["User A", "User B", "User C"],
    key="anomaly_user_selector"
)

profiles = {
    "User A": dict(mean=65, std=3),
    "User B": dict(mean=80, std=12),
    "User C": dict(mean=72, std=7, anomaly_start=45, anomaly_mean=95)
}

profile = profiles[selected_user_anomaly]
df_ad = generate_fake_data(**profile)
df_ad = compute_rolling_stats(df_ad)
df_ad = compute_zscore(df_ad)
df_ad = flag_anomalies_zscore(df_ad)
df_ad, _ = run_isolation_forest(df_ad, features=['heart_rate'])

col1, col2 = st.columns(2)
with col1:
    st.metric("Z-Score Anomalies", int(df_ad['is_anomaly_zscore'].sum()))
with col2:
    st.metric("Isolation Forest Anomalies", int(df_ad['isolation_forest_anomaly'].sum()))


fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_ad['timestamp'],
    y=df_ad['heart_rate'],
    mode='lines',
    line=dict(color='gray', width=1),
    name='Heart Rate'
))

zscore_points = df_ad[df_ad['is_anomaly_zscore'] == True]
fig.add_trace(go.Scatter(
    x=zscore_points['timestamp'],
    y=zscore_points['heart_rate'],
    mode='markers',
    marker=dict(color='blue', size=10, symbol='circle'),
    name='Z-Score Anomaly'
))

if_points = df_ad[df_ad['isolation_forest_anomaly'] == True]
fig.add_trace(go.Scatter(
    x=if_points['timestamp'],
    y=if_points['heart_rate'],
    mode='markers',
    marker=dict(color='red', size=10, symbol='x'),
    name='Isolation Forest Anomaly'
))

fig.update_layout(
    title=f"{selected_user_anomaly} — Anomaly Detection Comparison",
    xaxis_title="Date",
    yaxis_title="Heart Rate (bpm)"
)

st.plotly_chart(fig, use_container_width=True)