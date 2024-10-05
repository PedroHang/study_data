import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime

# Function to load CSV data from GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/PedroHang/study_data/main/df_cleaned.csv"
    df = pd.read_csv(url)
    df.dropna(inplace=True)
    return df

# Function to update the CSV file on GitHub
def update_csv(df):
    url = "https://api.github.com/repos/PedroHang/study_data/contents/df_cleaned.csv"
    token = st.secrets["GITHUB_TOKEN"]
    message = "Update study hours"
    content = df.to_csv(index=False).encode("utf-8")

    # Get the current file SHA to update
    response = requests.get(url, headers={"Authorization": f"token {token}"})
    
    if response.status_code != 200:
        st.error("Failed to get the file: " + response.json().get('message', ''))
        return False

    sha = response.json()["sha"]

    # Create a payload for the PUT request
    payload = {
        "message": message,
        "content": base64.b64encode(content).decode("utf-8"),
        "sha": sha
    }

    # Update the file on GitHub
    response = requests.put(url, headers={"Authorization": f"token {token}"}, json=payload)

    if response.ok:
        st.success("File updated successfully.")
    else:
        st.error(f"Failed to update the file: {response.status_code} - {response.text}")

    return response.ok

# Function to initialize missing dates
def initialize_missing_dates(df):
    df['Full_Date'] = pd.to_datetime(df['Full_Date'], format='%Y-%m-%d', errors='coerce')

    subjects = df['Study'].unique().tolist()
    last_date = df['Full_Date'].max()
    today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))

    date_range = pd.date_range(start=last_date, end=today)

    new_rows = []
    for date in date_range:
        for subject in subjects:
            if not ((df['Full_Date'] == date) & (df['Study'] == subject)).any():
                new_rows.append({'Full_Date': date, 'Study': subject, 'Hours': 0})

    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

    return df

# Function to manually input study hours
def input_study_hours():
    date_input = st.date_input("Enter Date", datetime.now())
    subject_input = st.text_input("Enter Subject")
    hours_input = st.number_input("Enter Hours", min_value=0.0, step=0.5)

    if st.button("Add Hours"):
        return {'Full_Date': date_input, 'Study': subject_input, 'Hours': hours_input}
    return None

# Load the data
df = load_data()

# Initialize missing dates with 0 hours for all subjects
df = initialize_missing_dates(df)

# Display an input form for the user to add new hours
st.write("Add Study Hours")
new_entry = input_study_hours()

if new_entry:
    df = df.append(new_entry, ignore_index=True)
    st.success("New study hours added!")

# Button to save changes back to GitHub
if st.button("Save Changes"):
    if update_csv(df):
        st.success("Changes saved and file updated successfully!")
    else:
        st.error("Failed to update the file on GitHub.")

# Display the current DataFrame
st.write("Current Study Hours")
st.dataframe(df)
