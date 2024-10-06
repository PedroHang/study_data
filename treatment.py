import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

API_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSTVLP5IFZY9R2CTS4Ld9yFm9ymyAyTcW5IK_aVjmAqWPhrNmg5jWAzPgqd1ziVBqu3QEqL0Y4rpjF2/pub?output=csv"
st.set_page_config(layout="wide")

def fetch_data():
    try:
        # Read the Google Sheets CSV directly into a DataFrame
        df = pd.read_csv(API_URL)
        return df
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()


st.title("My Daily Study Routine")

if st.button("Refresh Data"):
    data = fetch_data()
    df = pd.DataFrame(data)
else:
    data = fetch_data()
    df = pd.DataFrame(data)

if not df.empty:
    df['Hours'] = pd.to_numeric(df['Hours'], errors='coerce')
    df['Full_Date'] = pd.to_datetime(df['Full_Date'])

    df_daily = df.groupby("Full_Date")['Hours'].sum().reset_index()
    df_daily['Rolling Volatility'] = df_daily['Hours'].rolling(window=7).std()
    df_daily['Week'] = df_daily['Full_Date'].dt.to_period('W').apply(lambda r: r.start_time)
    df_weekly = df_daily.groupby('Week')['Hours'].mean().reset_index()
    df_weekly['Hours'] = df_weekly['Hours'].round(2)

    # Donut chart for today's study hours by subject
    today = datetime.now().date()
    df_today = df[df['Full_Date'].dt.date == today]

    if not df_today.empty:
        fig_today = px.pie(df_today, values='Hours', names='Study', title='Today\'s Study Hours by Subject',
                           hole=0.4, color='Hours')
        fig_today.update_traces(textinfo='label+value')  # Show label and actual hours
        fig_today.update_layout(title_font=dict(size=24),
                                width=600, height=400)
        
        # Create columns for the donut chart and the total hours card
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(fig_today)

        with col2:
            total_hours_today = df_today['Hours'].sum()
            st.markdown(f"<h3 style='text-align: center; font-size: 18px;'>Total Hours Studied Today</h3>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; font-size: 75px; color: orange; margin-top: 60px'>{total_hours_today:.2f} Hours</h1>", unsafe_allow_html=True)

    if not df_daily.empty:
        plot_option = st.selectbox("Select Plot Type:", ("Total Hours", "Rolling Volatility", "Weekly Average"))

        if plot_option == "Total Hours":
            fig = px.line(df_daily, x='Full_Date', y='Hours', 
                          title='Total Hours Per Day',
                          labels={'Full_Date': 'Date', 'Hours': 'Total Hours'},
                          markers=True)
            fig.update_traces(line=dict(width=4, color='orange'),
                              marker=dict(size=8, symbol='circle'))
            fig.update_layout(title_font=dict(size=24),
                              xaxis_title_font=dict(size=18),
                              yaxis_title_font=dict(size=18),
                              legend=dict(title_font=dict(size=16), font=dict(size=14)),
                              width=1800, height=460)
            st.plotly_chart(fig)

        elif plot_option == "Rolling Volatility":
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

    st.subheader("Total Hours by Subject")
    df_study = df.groupby("Study")['Hours'].sum().reset_index()
    df_study = df_study.sort_values(by='Hours', ascending=False)

    if not df_study.empty:
        fig_study = px.bar(df_study, x='Study', y='Hours', 
                           title='Total Hours by Study',
                           labels={'Study': 'Study', 'Hours': 'Total Hours'},
                           text='Hours',
                           color='Hours',
                           color_continuous_scale=px.colors.sequential.Viridis)
        fig_study.update_layout(width=1800)
        st.plotly_chart(fig_study)

    last_15_days = datetime.now() - timedelta(days=15)
    df_recent = df[df['Full_Date'] >= last_15_days]
    df_study_recent = df_recent.groupby("Study")['Hours'].sum().reset_index()
    top_studies = df_study_recent.sort_values(by='Hours', ascending=False).head(3)

    st.subheader("Top 3 Subjects Studied in the Last 15 Days")
    for index, row in top_studies.iterrows():
        st.metric(label=row['Study'], value=f"{row['Hours']:.2f} Hours")

    total_hours = df['Hours'].sum()
    days_equivalent = total_hours / 24
    max_hours_day = df_daily.loc[df_daily['Hours'].idxmax()]
    record_hours = max_hours_day['Hours']
    record_date = max_hours_day['Full_Date'].strftime("%Y-%m-%d")

    st.markdown("<h3 style='color: lightblue; font-family: Arial; margin-top: 40px'>- Total Hours Studied -</h3>", unsafe_allow_html=True)

    df_daily = df_daily.sort_values(by='Full_Date')
    df_daily['Studied'] = df_daily['Hours'] > 0
    df_daily['Day_Diff'] = df_daily['Full_Date'].diff().dt.days.fillna(1)
    df_daily['Is_Consecutive'] = (df_daily['Day_Diff'] == 1) & df_daily['Studied']
    df_daily['Streak_Group'] = (~df_daily['Is_Consecutive']).cumsum()
    df_streaks = df_daily[df_daily['Studied']].groupby('Streak_Group').size().reset_index(name='Streak_Length')
    max_streak = df_streaks['Streak_Length'].max()

    last_zero_day = df_daily[df_daily['Hours'] == 0]['Full_Date'].max()
    current_streak = (datetime.now().date() - last_zero_day.date()).days if not pd.isnull(last_zero_day) else 0

    distinct_study_days = df_daily['Full_Date'][df_daily['Studied']].nunique()
    days_without_study = df_daily[~df_daily['Studied']]['Full_Date'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Total Hours", value=f"{total_hours:.2f} Hours")
        st.metric(label="Longest Study Streak", value=f"{max_streak} Days")

    with col2:
        st.metric(label="Total time (in days)", value=f"{days_equivalent:.2f} Days")
        st.metric(label="Current Study Streak", value=f"{current_streak} Days")

    with col3:
        st.metric(label="Record Day", value=f"{record_hours:.2f} Hours", delta=f"On {record_date}")
        st.metric(label="Distinct Days Studied", value=f"{distinct_study_days} Days")

    with col4:
        st.metric(label="Started on", value="2024-05-12")
        st.metric(label="No study days", value=f"{days_without_study} Days")


    ######################################

    st.markdown(f"<h3 style='text-align: center; font-size: 45px; margin-top: 60px;'>Insights</h3>", unsafe_allow_html=True)


    # Add a new column for the day of the week
    df['Day_of_Week'] = df['Full_Date'].dt.day_name()  # Get the name of the day

    # Calculate total hours for each day of the week
    total_hours_per_weekday = df.groupby('Day_of_Week')['Hours'].sum().reset_index()

    # Calculate the number of unique study days for each day of the week
    unique_days_per_weekday = df.groupby('Day_of_Week')['Full_Date'].nunique().reset_index()

    # Merge the two DataFrames
    average_hours_per_weekday = pd.merge(total_hours_per_weekday, unique_days_per_weekday, on='Day_of_Week')
    average_hours_per_weekday['Average_Hours'] = average_hours_per_weekday['Hours'] / average_hours_per_weekday['Full_Date']

    # Reorder the days of the week
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    average_hours_per_weekday['Day_of_Week'] = pd.Categorical(average_hours_per_weekday['Day_of_Week'], categories=days_order, ordered=True)
    average_hours_per_weekday = average_hours_per_weekday.sort_values('Day_of_Week')

    # Plot the average study hours by day of the week
    average_hours_per_weekday['Average_Hours'] = average_hours_per_weekday['Average_Hours'].round(2)  # Round to 2 decimals

    fig_avg_weekday = px.bar(
        average_hours_per_weekday, 
        x='Day_of_Week', 
        y='Average_Hours',
        title='Average Study Hours by Day of the Week',
        labels={'Day_of_Week': 'Day of the Week', 'Average_Hours': 'Average Hours'},
        text=average_hours_per_weekday['Average_Hours'].apply(lambda x: f"{x:.2f}"),  # Format text to 2 decimals
        color='Average_Hours',
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig_avg_weekday.update_layout(
        title_font=dict(size=24),
        xaxis_title_font=dict(size=18),
        yaxis_title_font=dict(size=18),
        legend=dict(title_font=dict(size=16), font=dict(size=14)),
        width=1800, 
        height=600
    )
    st.plotly_chart(fig_avg_weekday)

        # Function to fetch temperature data for a specific date
    def fetch_temperature(date, city='Petropolis'):
        API_KEY = 'your_api_key_here'  # You'll need to replace this with your actual API key
        BASE_URL = f"http://api.openweathermap.org/data/2.5/onecall/timemachine"
        LAT, LON = -22.5149, -43.1779  # Coordinates for Petrópolis

        # API call to fetch weather for the specific date
        timestamp = int(pd.Timestamp(date).timestamp())
        response = requests.get(
            f"{BASE_URL}?lat={LAT}&lon={LON}&dt={timestamp}&appid={API_KEY}&units=metric"
        )

        # Debug the response
        if response.status_code != 200:
            st.error(f"Failed to fetch temperature data: {response.status_code}")
            return None

        data = response.json()

        if 'hourly' not in data:
            st.error("No hourly data found in the API response.")
            return None

        # Get the average temperature for that day
        temps = [hourly['temp'] for hourly in data['hourly']]
        avg_temp = sum(temps) / len(temps)
        return avg_temp

    # Fetch study data
    data = fetch_data()  # Assuming this fetches your study data
    df = pd.DataFrame(data)

    # Ensure there is data in the DataFrame
    if df.empty:
        st.error("The study data is empty.")
    else:
        st.write("Study data loaded successfully:", df.head())

    # Add temperature data to each date in the study dataset
    df['Full_Date'] = pd.to_datetime(df['Full_Date'])
    df['Avg_Temperature'] = df['Full_Date'].apply(fetch_temperature)

    # Ensure temperature data was fetched correctly
    if df['Avg_Temperature'].isnull().all():
        st.error("No temperature data was fetched.")
    else:
        st.write("Temperature data added:", df[['Full_Date', 'Avg_Temperature']].head())

    # Group by temperature and calculate the average study hours
    df_grouped = df.groupby('Avg_Temperature')['Hours'].mean().reset_index()

    # Ensure there is data to plot
    if df_grouped.empty:
        st.error("No data to plot after grouping.")
    else:
        st.write("Grouped data for plotting:", df_grouped.head())

        # Create scatter plot to visualize correlation
        fig = px.scatter(df_grouped, x='Avg_Temperature', y='Hours',
                        title='Correlation Between Average Temperature and Study Hours',
                        labels={'Avg_Temperature': 'Average Temperature (°C)', 'Hours': 'Average Study Hours'},
                        trendline="ols")  # Add a trendline to observe the correlation

        # Show the plot
        st.plotly_chart(fig)
else:
    st.write("No data available.")
