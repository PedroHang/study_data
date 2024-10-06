import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

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

# Button to refresh data
if st.button("Refresh Data"):
    data = fetch_data()
    df = pd.DataFrame(data)
else:
    # Fetch and display data only if button is not clicked
    data = fetch_data()
    df = pd.DataFrame(data)

if not df.empty:
    # Convert 'Hours' to numeric and handle errors
    df['Hours'] = pd.to_numeric(df['Hours'], errors='coerce')

    # Format the 'Full_Date' column to datetime
    df['Full_Date'] = pd.to_datetime(df['Full_Date'])

    # Group by 'Full_Date' and sum the hours
    df_daily = df.groupby("Full_Date")['Hours'].sum().reset_index()

    # Calculate the 7-day rolling standard deviation
    df_daily['Rolling Volatility'] = df_daily['Hours'].rolling(window=7).std()

    # Calculate the weekly average starting from Monday
    df_daily['Week'] = df_daily['Full_Date'].dt.to_period('W').apply(lambda r: r.start_time)
    df_weekly = df_daily.groupby('Week')['Hours'].mean().reset_index()

    # --- Longest Study Streak Calculation ---

    # Sort by date and check for consecutive days where hours > 0
    df_daily = df_daily.sort_values(by='Full_Date')
    df_daily['Studied'] = df_daily['Hours'] > 0

    # Calculate difference between consecutive dates
    df_daily['Day_Diff'] = df_daily['Full_Date'].diff().dt.days.fillna(1)

    # Check if the difference between consecutive days is 1 and hours were studied on that day
    df_daily['Is_Consecutive'] = (df_daily['Day_Diff'] == 1) & df_daily['Studied']

    # Create streak groups and calculate the maximum streak
    df_daily['Streak_Group'] = (~df_daily['Is_Consecutive']).cumsum()
    df_streaks = df_daily[df_daily['Studied']].groupby('Streak_Group').size().reset_index(name='Streak_Length')
    max_streak = df_streaks['Streak_Length'].max()

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    # Calculate the total hours studied
    total_hours = df['Hours'].sum()
    days_equivalent = total_hours / 24

    # Calculate the maximum hours for a single day
    max_hours_day = df_daily.loc[df_daily['Hours'].idxmax()]

    # Display the total hours and streak in col1
    col1.metric(label="Total Hours Studied", value=f"{total_hours:.2f} Hours")
    col1.metric(label="Total Study Time in Days", value=f"{days_equivalent:.2f} Days")
    col1.metric(label="Longest Study Streak", value=f"{max_streak} Days")

    # Display the max hours in a single day in col2
    col2.metric(label="Max Hours in a Single Day", value=f"{max_hours_day['Hours']:.2f} Hours", delta=f"{max_hours_day['Full_Date'].strftime('%Y-%m-%d')}")

    # --- Existing chart functionality ---
    if not df_daily.empty:
        # Toggle between Total Hours, Rolling Volatility, and Weekly Average
        plot_option = st.selectbox("Select Plot Type:", ("Total Hours", "Rolling Volatility", "Weekly Average"))

        if plot_option == "Total Hours":
            # Create a Plotly line chart for total hours per day
            fig = px.line(df_daily, x='Full_Date', y='Hours', 
                          title='Total Hours Per Day',
                          labels={'Full_Date': 'Date', 'Hours': 'Total Hours'},
                          markers=True)

            # Update layout for wider dimensions and improve aesthetics
            fig.update_traces(line=dict(width=4, color='orange'),
                              marker=dict(size=8, symbol='circle'))
            fig.update_layout(title_font=dict(size=24),
                              xaxis_title_font=dict(size=18),
                              yaxis_title_font=dict(size=18),
                              legend=dict(title_font=dict(size=16), font=dict(size=14)),
                              width=1800, height=460)

            st.plotly_chart(fig)

        elif plot_option == "Rolling Volatility":
            # Create a Plotly line chart for rolling volatility
            fig_volatility = px.line(df_daily, x='Full_Date', y='Rolling Volatility',
                                     title='7-Day Rolling Volatility',
                                     labels={'Full_Date': 'Date', 'Rolling Volatility': 'Volatility'},
                                     markers=True)

            fig_volatility.update_traces(line=dict(width=4, color='royalblue'),
                                         marker=dict(size=8, symbol='circle'))
            fig_volatility.update_layout(title_font=dict(size=24),
                                          xaxis_title_font=dict(size=18),
                                          yaxis_title_font=dict(size=18),
                                          legend=dict(title_font=dict(size=16), font=dict(size=14)),
                                          width=1800, height=600)

            st.plotly_chart(fig_volatility)

        elif plot_option == "Weekly Average":
            # Create a Plotly bar chart for weekly average
            fig_weekly = px.bar(df_weekly, x='Week', y='Hours',
                                 title='Weekly Average Study Hours',
                                 labels={'Week': 'Week Start Date', 'Hours': 'Average Hours'},
                                 text=df_weekly['Hours'].apply(lambda x: f"{x:.2f}"),
                                 color='Hours',
                                 color_continuous_scale=px.colors.sequential.Viridis)

            fig_weekly.update_traces(marker=dict(line=dict(width=1, color='black')))
            fig_weekly.update_layout(title_font=dict(size=24),
                                      xaxis_title_font=dict(size=18),
                                      yaxis_title_font=dict(size=18),
                                      legend=dict(title_font=dict(size=16), font=dict(size=14)),
                                      width=1800, height=600)

            st.plotly_chart(fig_weekly)
else:
    st.warning("No data available.")
