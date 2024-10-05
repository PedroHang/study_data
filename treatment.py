import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import base64

# Function to load CSV data from GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/PedroHang/study_data/main/df_cleaned.csv"
    df = pd.read_csv(url)
    df.dropna(inplace=True)  # Remove NaN values
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

# Load the data
df = load_data()

# Select a subject from the unique subjects
subjects = df['Study'].unique().tolist()
selected_subject = st.selectbox("Select a Subject:", subjects)

# Input for hours
hours_to_add = st.number_input("Enter Hours to Add (e.g., 2.5):", min_value=0.0, format="%.2f")
selected_date = st.date_input("Select Date:", value=datetime.today())

if st.button("Add Hours"):
    # Load the latest data again
    df = load_data()
    
    # Use the full date directly
    full_date = selected_date  

    # Add the new hours if the entry exists
    if not df[(df['Full_Date'] == full_date) & (df['Study'] == selected_subject)].empty:
        # Increment the existing hours
        df.loc[(df['Full_Date'] == full_date) & (df['Study'] == selected_subject), 'Hours'] += hours_to_add
    else:
        # If it doesn't exist, create a new entry
        new_entry = pd.DataFrame({
            'Study': [selected_subject],
            'Full_Date': [full_date],  # Use the full date including the year
            'Hours': [hours_to_add]
        })
        df = pd.concat([df, new_entry], ignore_index=True)

    # Update the CSV file on GitHub
    if update_csv(df):
        st.success("Hours added and file updated successfully!")
    else:
        st.error("Failed to update the file on GitHub.")

# Display the updated DataFrame
st.write("Current Study Hours:")
st.dataframe(df)
