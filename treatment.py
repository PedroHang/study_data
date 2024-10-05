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

    # Group by 'Full_Date' and sum the hours
    df_daily = df.groupby("Full_Date")['Hours'].sum().reset_index()

    # Calculate the 7-day rolling standard deviation
    df_daily['Rolling Volatility'] = df_daily['Hours'].rolling(window=7).std()

    # Calculate the weekly average starting from Monday
    df_daily['Full_Date'] = pd.to_datetime(df_daily['Full_Date'])
    df_daily['Week'] = df_daily['Full_Date'].dt.to_period('W').apply(lambda r: r.start_time)  # Get the start date of the week
    df_weekly = df_daily.groupby('Week')['Hours'].mean().reset_index()

    # Format the average hours to 2 decimal points
    df_weekly['Hours'] = df_weekly['Hours'].round(2)

    # Check if df_daily is not empty before plotting
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
            fig.update_traces(line=dict(width=4, color='orange'),  # Set line width and color
                              marker=dict(size=8, symbol='circle'))  # Set marker size and shape
            fig.update_layout(title_font=dict(size=24),  # Title font size
                              xaxis_title_font=dict(size=18),  # X-axis title font size
                              yaxis_title_font=dict(size=18),  # Y-axis title font size
                              legend=dict(title_font=dict(size=16), font=dict(size=14)),  # Legend font size
                              width=1800, height=600)  # Update dimensions

            # Show the Plotly chart in Streamlit
            st.plotly_chart(fig)

        elif plot_option == "Rolling Volatility":
            # Create a Plotly line chart for rolling volatility
            fig_volatility = px.line(df_daily, x='Full_Date', y='Rolling Volatility',
                                     title='7-Day Rolling Volatility',
                                     labels={'Full_Date': 'Date', 'Rolling Volatility': 'Volatility'},
                                     markers=True)

            # Update layout for wider dimensions and improve aesthetics
            fig_volatility.update_traces(line=dict(width=4, color='royalblue'),  # Set line width and color
                                         marker=dict(size=8, symbol='circle'))  # Set marker size and shape
            fig_volatility.update_layout(title_font=dict(size=24),  # Title font size
                                          xaxis_title_font=dict(size=18),  # X-axis title font size
                                          yaxis_title_font=dict(size=18),  # Y-axis title font size
                                          legend=dict(title_font=dict(size=16), font=dict(size=14)),  # Legend font size
                                          width=1800, height=600)  # Update dimensions

            # Show the Plotly chart in Streamlit
            st.plotly_chart(fig_volatility)

        elif plot_option == "Weekly Average":
            # Create a Plotly bar chart for weekly average
            fig_weekly = px.bar(df_weekly, x='Week', y='Hours',
                                 title='Weekly Average Study Hours',
                                 labels={'Week': 'Week Start Date', 'Hours': 'Average Hours'},
                                 text=df_weekly['Hours'].apply(lambda x: f"{x:.2f}"),  # Format text to 2 decimal points
                                 color='Hours',  # Color by average hours
                                 color_continuous_scale=px.colors.sequential.Viridis)  # Color scale

            # Update layout for wider dimensions and improve aesthetics
            fig_weekly.update_traces(marker=dict(line=dict(width=1, color='black')))  # Add outline to bars
            fig_weekly.update_layout(title_font=dict(size=24),  # Title font size
                                      xaxis_title_font=dict(size=18),  # X-axis title font size
                                      yaxis_title_font=dict(size=18),  # Y-axis title font size
                                      legend=dict(title_font=dict(size=16), font=dict(size=14)),  # Legend font size
                                      width=1800, height=600)  # Update dimensions

            # Show the Plotly chart in Streamlit
            st.plotly_chart(fig_weekly)

    else:
        st.warning("No data available for daily hours.")

    # --- New Section for Visualization by Subject ---
    
    st.subheader("Total Hours by Subject")

    # Add a slider to select the last x days
    max_days = 30  # Set maximum number of days for the slider
    days = st.slider("Select Last X Days:", min_value=1, max_value=max_days, value=max_days)

    # Calculate the date range
    end_date = df['Full_Date'].max()  # Get the maximum date from the data
    start_date = end_date - timedelta(days=days)  # Calculate start date based on the slider

    # Filter the DataFrame for the selected date range
    df_filtered = df_daily[(df_daily['Full_Date'] >= start_date) & (df_daily['Full_Date'] <= end_date)]

    # Group by 'Study' and sum the hours for the filtered DataFrame
    df_study = df_filtered.groupby("Study")['Hours'].sum().reset_index()

    # Sort the DataFrame by Hours in descending order
    df_study = df_study.sort_values(by='Hours', ascending=False)

    # Check if df_study is not empty before plotting
    if not df_study.empty:
        # Create a Plotly bar chart for total hours by study with a color palette
        fig_study = px.bar(df_study, x='Study', y='Hours', 
                           title='Total Hours by Study (Last X Days)',
                           labels={'Study': 'Study', 'Hours': 'Total Hours'},
                           text='Hours',  # Display hours on the bars
                           color='Hours',  # Color by hours
                           color_continuous_scale=px.colors.sequential.Viridis)  # Beautiful color palette
        
        # Update layout for wider dimensions
        fig_study.update_layout(width=1800)

        # Show the Plotly chart in Streamlit
        st.plotly_chart(fig_study)
    else:
        st.warning("No data available for study breakdown.")
else:
    st.warning("No data fetched from the API.")
