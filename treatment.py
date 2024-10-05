import streamlit as st
import pandas as pd
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

# Display an editable DataFrame
st.write("Edit Study Hours:")
edited_df = st.data_editor(df, use_container_width=True)

# Button to update the GitHub file
if st.button("Save Changes"):
    # Update the CSV file on GitHub
    if update_csv(edited_df):
        st.success("Changes saved and file updated successfully!")
    else:
        st.error("Failed to update the file on GitHub.")

# Display the current DataFrame
st.write("Current Study Hours:")
st.dataframe(edited_df)
