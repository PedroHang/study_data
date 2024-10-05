import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import base64

# Function to load CSV data from GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/PedroHang/study_data/main/clean_data.csv"
    df = pd.read_csv(url)
    df.dropna(inplace=True)  # Remove NaN values
    return df

# Function to update the CSV file on GitHub
def update_csv(df):
    url = "https://api.github.com/repos/PedroHang/study_data/contents/clean_data.csv"
    token = st.secrets["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"]  # Store your GitHub token in Streamlit secrets
    message = "Update study hours"
    content = df.to_csv(index=False).encode("utf-8")
    
    # Get the current file SHA to update
    response = requests.get(url, headers={"Authorization": f"token {token}"})
    
    if response.status_code != 200:
        print("Failed to get the file: ", response.json())
        return False

    sha = response.json()["sha"]
    
    # Create a payload for the PUT request
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    
    # Update the file on GitHub
    response = requests.put(url, headers={"Authorization": f"token {token}"}, json=payload)

    if response.ok:
        print("File updated successfully.")
    else:
        print("Failed to update the file: ", response.json())

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
    # Update DataFrame with the new hours
    date_str = selected_date.strftime("%m/%d")
    
    # Add the new hours if the entry exists
    if not df[(df['Date'] == date_str) & (df['Study'] == selected_subject)].empty:
        # Add the new hours
        df.loc[(df['Date'] == date_str) & (df['Study'] == selected_subject), 'Hours'] += hours_to_add
    else:
        # If it doesn't exist, create a new entry
        new_entry = pd.DataFrame({
            'Study': [selected_subject],
            'Date': [date_str],
            'Hours': [hours_to_add]
        })
        df = pd.concat([df, new_entry], ignore_index=True)

    # Ensure all subjects for the selected date are set to 0 if not present
    for subject in subjects:
        if subject not in df['Study'][df['Date'] == date_str].values:
            df = df.append({'Study': subject, 'Date': date_str, 'Hours': 0}, ignore_index=True)

    # Update the CSV file on GitHub
    if update_csv(df):
        st.success("Hours added and file updated successfully!")
    else:
        st.error("Failed to update the file on GitHub.")

# Display the updated DataFrame
st.write("Current Study Hours:")
st.dataframe(df)
