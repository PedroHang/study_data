import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

# Replace SheetDB API with Google Sheets CSV link
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSTVLP5IFZY9R2CTS4Ld9yFm9ymyAyTcW5IK_aVjmAqWPhrNmg5jWAzPgqd1ziVBqu3QEqL0Y4rpjF2/pub?output=csv"
st.set_page_config(layout="wide")

def fetch_data():
    try:
        # Use Pandas to read the Google Sheets CSV
        df = pd.read_csv(GOOGLE_SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

st.title("My Daily Study Routine")

if st.button("Refresh Data"):
    df = fetch_data()
else:
    df = fetch_data()

if not df.empty:
    # Your existing code for processing and visualizing the data goes here...
    # Process 'Hours' as numeric, handle 'Full_Date', and create visualizations

    # Example: Convert 'Full_Date' and 'Hours'
    df['Hours'] = pd.to_numeric(df['Hours'], errors='coerce')
    df['Full_Date'] = pd.to_datetime(df['Full_Date'])

    # Rest of your Streamlit app code...
else:
    st.write("No data available.")
