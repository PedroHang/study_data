import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Define the API endpoint
API_URL = "https://sheetdb.io/api/v1/pqxbedqqemsvb"
st.set_page_config(layout="wide")

# Function to fetch data from the API
def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")
        return []

# Streamlit UI
st.title("My Daily Study Routine")

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
        # Create a Plotly line chart for total hours per day
        fig = px.line(df_daily, x='Full_Date', y='Hours', 
                      title='Total Hours Per Day',
                      labels={'Full_Date': 'Date', 'Hours': 'Total Hours'},
                      markers=True)
        
        # Update layout for wider dimensions
        fig.update_layout(width=1800)

        # Show the Plotly chart in Streamlit
        st.plotly_chart(fig)
    else:
        st.warning("No data available for daily hours.")

    # --- New Section for Visualization by Study ---

    st.subheader("Total Hours by Study")

    # Group by 'Study' and sum the hours
    df_study = df.groupby("Study")['Hours'].sum().reset_index()

    # Check if df_study is not empty before plotting
    if not df_study.empty:
        # Create a Plotly bar chart for total hours by study
        fig_study = px.bar(df_study, x='Study', y='Hours', 
                           title='Total Hours by Study',
                           labels={'Study': 'Study', 'Hours': 'Total Hours'},
                           text='Hours')  # Display hours on the bars
        
        # Update layout for wider dimensions
        fig_study.update_layout(width=1800)

        # Show the Plotly chart in Streamlit
        st.plotly_chart(fig_study)
    else:
        st.warning("No data available for study breakdown.")
else:
    st.warning("No data fetched from the API.")
