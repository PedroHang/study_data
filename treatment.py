import streamlit as st
import pandas as pd
import requests

# Define the API endpoint
API_URL = "https://sheetdb.io/api/v1/pqxbedqqemsvb"

# Function to fetch data from the API
def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching data from SheetDB")
        return []

# Initialize a session state variable to store the DataFrame
if 'dataframe' not in st.session_state:
    st.session_state['dataframe'] = pd.DataFrame()

# Function to update the DataFrame
def update_data():
    data = fetch_data()
    if data:
        st.session_state['dataframe'] = pd.DataFrame(data)

# Load data initially
update_data()

# Streamlit UI
st.title("Data Visualization from SheetDB")

# Button to re-upload the data
if st.button("Re-upload Data"):
    update_data()
    st.success("Data re-uploaded successfully!")

# Display the DataFrame
if not st.session_state['dataframe'].empty:
    st.write("Here is the data fetched from the API:")
    st.dataframe(st.session_state['dataframe'])

    # Example visualization: Display a line chart (assuming the data has numeric columns)
    if st.session_state['dataframe'].select_dtypes(include='number').shape[1] > 0:
        st.subheader("Line Chart of Numeric Data")
        st.line_chart(st.session_state['dataframe'].select_dtypes(include='number'))
else:
    st.warning("No data available.")
