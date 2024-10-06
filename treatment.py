import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

API_URL = "https://sheetdb.io/api/v1/pqxbedqqemsvb"
st.set_page_config(layout="wide")

def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")
        return []

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
        # Create columns for the top studies
    col1, col2, col3 = st.columns(3)

    # Use an array to store the columns
    columns = [col1, col2, col3]

    for index, row in top_studies.iterrows():
        with columns[index]:  # Assign each row to a specific column
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
else:
    st.warning("No data fetched from the API.")
