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
        st.error(f"Failed to fetch data. Status code: {response.status_code}")
        return []

# Streamlit UI
st.title("Daily Hours Visualization")

# Fetch and display data
data = fetch_data()
df = pd.DataFrame(data)

if not df.empty:
    # Convert 'Hours' to numeric and handle errors
    df['Hours'] = pd.to_numeric(df['Hours'], errors='coerce')

    # Group by 'Full_Date' and sum the hours
    df_daily = df.groupby("Full_Date")['Hours'].sum().reset_index()

    # Check if df_daily is not empty before plotting
    if not df_daily.empty:
        # Create a Plotly line chart
        fig = px.line(df_daily, x='Full_Date', y='Hours', 
                      title='Total Hours Per Day',
                      labels={'Full_Date': 'Date', 'Hours': 'Total Hours'},
                      markers=True)
        
        # Update layout for full screen width
        fig.update_layout(
            width=0,          # Set width to auto
            height=600,      # Set height as needed
            autosize=True     # Ensure it adjusts to full width
        )

        # Show the Plotly chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)  # Set use_container_width to True for full width
    else:
        st.warning("No data available for daily hours.")
else:
    st.warning("No data fetched from the API.")
