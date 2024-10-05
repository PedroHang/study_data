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

    # Calculate the 7-day rolling standard deviation and weekly rolling average
    df_daily['Rolling Volatility'] = df_daily['Hours'].rolling(window=7).std()
    df_daily['Weekly Average'] = df_daily['Hours'].rolling(window=7).mean()  # Weekly rolling average

    # Check if df_daily is not empty before plotting
    if not df_daily.empty:
        # Toggle between Total Hours and Rolling Volatility
        plot_option = st.selectbox("Select Plot Type:", ("Total Hours", "Rolling Volatility"))

        if plot_option == "Total Hours":
            # Create a Plotly line chart for total hours per day
            fig = px.line(df_daily, x='Full_Date', y='Hours', 
                          title='Total Hours Per Day',
                          labels={'Full_Date': 'Date', 'Hours': 'Total Hours'},
                          markers=True)

            # Add the weekly rolling average line
            fig.add_scatter(x=df_daily['Full_Date'], y=df_daily['Weekly Average'],
                             mode='lines', name='Weekly Average', line=dict(width=2, color='green'))

            # Update layout for wider dimensions and improve aesthetics
            fig.update_traces(line=dict(width=4, color='royalblue'),  # Set line width and color for total hours
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
            fig_volatility.update_traces(line=dict(width=4, color='orange'),  # Set line width and color
                                         marker=dict(size=8, symbol='circle'))  # Set marker size and shape
            fig_volatility.update_layout(title_font=dict(size=24),  # Title font size
                                          xaxis_title_font=dict(size=18),  # X-axis title font size
                                          yaxis_title_font=dict(size=18),  # Y-axis title font size
                                          legend=dict(title_font=dict(size=16), font=dict(size=14)),  # Legend font size
                                          width=1800, height=600)  # Update dimensions

            # Show the Plotly chart in Streamlit
            st.plotly_chart(fig_volatility)
    else:
        st.warning("No data available for daily hours.")

    # --- New Section for Visualization by Study ---

    st.subheader("Total Hours by Study")

    # Group by 'Study' and sum the hours
    df_study = df.groupby("Study")['Hours'].sum().reset_index()

    # Sort the DataFrame by Hours in descending order
    df_study = df_study.sort_values(by='Hours', ascending=False)

    # Check if df_study is not empty before plotting
    if not df_study.empty:
        # Create a Plotly bar chart for total hours by study with a color palette
        fig_study = px.bar(df_study, x='Study', y='Hours', 
                           title='Total Hours by Study',
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
