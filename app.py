
import streamlit as st
import numpy as np
import pandas as pd
import os 

from src.file_handler import save_entry

st.title("Health Dashboard")        # gives the title of the dashboard
st.write("Welcome to you personal health check-in system!") # gives a welcome message to the user


st.sidebar.title("Settings")    # makes a sidebar with the title "Settings"
name = st.sidebar.text_input("Your name", value="Student") # creates a text input in the sidebar for the user to enter their name, with a default value of "Student"
st.write(f"Hello, {name}!") # usees the name variable to greet the user on the main page



st.subheader("Energy Levels — Last 30 Days") # title 

if os.path.exists("data/checkin.csv"): # if the checkin.csv file exists, read the energy levels from it and display them in a line chart
    df = pd.read_csv("data/checkin.csv") # read the csv file into a dataframe
    df["timestamp"] = pd.to_datetime(df["timestamp"]) # convert the timestamp column to datetime format
    df = df.set_index("timestamp") # set the timestamp column as the index of the dataframe
    st.line_chart(df["energy"]) # display a line chart of the energy levels over time
else:
    st.info("No data available. Please submit a first check-in below!")



st.subheader("Today's Check-in")  # title 

mood = st.slider("Mood (1-10)", min_value=1, max_value=10, value=5) # slider for mood 
energy_today = st.slider("Energy (1-10)", min_value=1, max_value=10, value=5) # slider for energy level
note = st.text_input("Any notes for today?") # text input for notes 

if "submissions" not in st.session_state: # if submission not in session state, initialize it to 0
    st.session_state.submissions = 0

if st.button("Submit"): # if the submit button is pressed, save the entry and update the submission count
    st.session_state.submissions += 1
    save_entry(mood, energy_today, note) # save the entry to the csv file
    st.success(f"Check-in saved! Mood: {mood}, Energy: {energy_today}, Note: {note}")

if st.session_state.submissions > 0: # if there have been any submissions, display the total count
    st.write(f"Total check-ins this session: {st.session_state.submissions}")  