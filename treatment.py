import streamlit as st
import pandas as pd
import requests
import plotly.express as px

test_data = {
    'date': pd.date_range(start='2023-01-01', periods=10),
    'hours': [5, 3, 8, 6, 2, 7, 4, 5, 3, 9]
}
test_df = pd.DataFrame(test_data)

fig = px.line(test_df, x='date', y='hours', title='Test Plotly Graph')
st.plotly_chart(fig)
