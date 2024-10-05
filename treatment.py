if not df.empty:
    # Convert 'Hours' to numeric and handle errors
    df['Hours'] = pd.to_numeric(df['Hours'], errors='coerce')

    # Format the 'Full_Date' column to datetime
    df['Full_Date'] = pd.to_datetime(df['Full_Date'])

    # Get the last 15 days
    last_15_days = datetime.now() - timedelta(days=15)
    df_recent = df[df['Full_Date'] >= last_15_days]

    # Group by 'Study' and sum the hours
    df_study_recent = df_recent.groupby("Study")['Hours'].sum().reset_index()

    # Sort the DataFrame by Hours in descending order and get the top 3 subjects
    top_studies = df_study_recent.sort_values(by='Hours', ascending=False).head(3)

    # Display metrics for the top 3 subjects in columns
    st.subheader("🌟 Top Subjects Studied in the Last 15 Days")

    cols = st.columns(3)  # Create three columns

    if not top_studies.empty:
        for index, row in top_studies.iterrows():
            with cols[index]:  # Use each column for a card
                st.markdown(
                    f"""
                    <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; text-align: center;">
                        <h2 style="color: #4a4a4a;">{row['Study']}</h2>
                        <h3 style="color: #008080;">{row['Hours']:.2f} Hours</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.warning("No subjects studied in the last 15 days.")

    # Continue with your existing charts and analysis...
    # Group by 'Full_Date' and sum the hours
    df_daily = df.groupby("Full_Date")['Hours'].sum().reset_index()

    # Check if df_daily is not empty before proceeding
    if not df_daily.empty:
        # Calculate the 7-day rolling standard deviation
        df_daily['Rolling Volatility'] = df_daily['Hours'].rolling(window=7).std()

        # Calculate the weekly average starting from Monday
        df_daily['Week'] = df_daily['Full_Date'].dt.to_period('W').apply(lambda r: r.start_time)  # Get the start date of the week
        df_weekly = df_daily.groupby('Week')['Hours'].mean().reset_index()

        # Format the average hours to 2 decimal points
        df_weekly['Hours'] = df_weekly['Hours'].round(2)

        # Check if df_daily is not empty before plotting
        # [Your plotting code continues here]
