import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime, timedelta
import streamlit_dataframe_editor as sde

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
    response = requests.get(url, headers={"Authorization": f"token {token}"})

    if response.status_code != 200:
        st.error(f"Failed to get the file: {response.json().get('message', '')}")
        return False

    sha = response.json()["sha"]
    payload = {
        "message": message,
        "content": base64.b64encode(content).decode("utf-8"),
        "sha": sha
    }

    response = requests.put(url, headers={"Authorization": f"token {token}"}, json=payload)
    if response.ok:
        st.success("File updated successfully.")
    else:
        st.error(f"Failed to update the file: {response.status_code} - {response.text}")

    return response.ok

# Initialize session state to hold edited dataframe
st.session_state = sde.initialize_session_state(st.session_state)

# Load the data
df = load_data()

# Sort the dataframe by date
df['Full_Date'] = pd.to_datetime(df['Full_Date'], format='%Y-%m-%d')
df = df.sort_values(by='Full_Date', ascending=False)

# Editable DataFrame
st.session_state['dataframe_editor'] = sde.DataframeEditor(df_name='study_data', default_df_contents=df)
st.session_state['dataframe_editor'].dataframe_editor()

# Button to save the changes
if st.button("Save Changes"):
    # Update the CSV file on GitHub
    if update_csv(st.session_state['study_data']):
        st.success("Changes saved and file updated successfully!")
    else:
        st.error("Failed to update the file on GitHub.")
    
# Finalize session state to store edits
st.session_state = sde.finalize_session_state(st.session_state)
