import streamlit as st
import pandas as pd
import requests
import plotly.express as px

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
        # Convert to DataFrame and convert all numeric columns to float
        df = pd.DataFrame(data)
        for col in df.select_dtypes(include='number').columns:
            df[col] = df[col].astype(float)
        st.session_state['dataframe'] = df

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

    # Example: Total hours for each day over time
    if 'date' in st.session_state['dataframe'].columns and st.session_state['dataframe'].select_dtypes(include='number').shape[1] > 0:
        # Convert 'date' column to datetime format
        st.session_state['dataframe']['date'] = pd.to_datetime(st.session_state['dataframe']['date'])

        # Group by date and sum the total hours
        total_hours = st.session_state['dataframe'].groupby('date').sum().reset_index()

        # Display the total_hours DataFrame for debugging
        st.write("Total Hours DataFrame:")
        st.dataframe(total_hours)

        # Check if total_hours DataFrame is not empty before plotting
        if not total_hours.empty:
            # Create a Plotly graph
            fig = px.line(total_hours, x='date', y=total_hours.columns[1:], title='Total Hours for Each Day Over Time')
            st.plotly_chart(fig)
        else:
            st.warning("No total hours available for plotting.")
else:
    st.warning("No data available.")
