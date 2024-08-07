import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
@st.cache_data
def load_data():
    data = pd.read_csv('data/consumes.csv')
    data['time'] = pd.to_datetime(data['time'])
    return data

data = load_data()

# Convert datetime to numerical timestamps for the slider
data['time_timestamp'] = data['time'].astype(int) / 10**9  # Convert to Unix timestamp

# Sidebar filters
st.sidebar.header("Filter Data")

def multi_select_with_all(label, options, default=None):
    st.sidebar.write(label)
    all_selected = st.sidebar.checkbox(f"Select All {label}", value=False)
    if all_selected:
        selected = options
    else:
        selected = st.sidebar.multiselect(f"Select {label}", options, default=default)
    return selected

# Get unique values for filters
unique_ids = data['id'].unique()
unique_user_ids = data['userId'].unique()
unique_device_ids = data['deviceId'].unique()
unique_is_at_home = data['isAtHome'].unique()
unique_is_anomalous = data['isAnomalous'].unique()

# Filter options with select all functionality
selected_id = multi_select_with_all("ID", unique_ids)
selected_user_id = multi_select_with_all("User ID", unique_user_ids)
selected_device_id = multi_select_with_all("Device ID", unique_device_ids)
selected_is_at_home = multi_select_with_all("Is At Home", unique_is_at_home)
selected_is_anomalous = multi_select_with_all("Is Anomalous", unique_is_anomalous)

# Time range slider
selected_time_range = st.sidebar.slider(
    "Select Time Range",
    min_value=float(data['time_timestamp'].min()),
    max_value=float(data['time_timestamp'].max()),
    value=(float(data['time_timestamp'].min()), float(data['time_timestamp'].max()))
)

# Convert selected_time_range back to datetime
start_date, end_date = pd.to_datetime(selected_time_range, unit='s')

# Filter data based on selections
filtered_data = data.copy()

# Check if selections are empty
if len(selected_id) > 0:
    filtered_data = filtered_data[filtered_data['id'].isin(selected_id)]
if len(selected_user_id) > 0:
    filtered_data = filtered_data[filtered_data['userId'].isin(selected_user_id)]
if len(selected_device_id) > 0:
    filtered_data = filtered_data[filtered_data['deviceId'].isin(selected_device_id)]
if len(selected_is_at_home) > 0:
    filtered_data = filtered_data[filtered_data['isAtHome'].isin(selected_is_at_home)]
if len(selected_is_anomalous) > 0:
    filtered_data = filtered_data[filtered_data['isAnomalous'].isin(selected_is_anomalous)]

# Apply time range filter
filtered_data = filtered_data[(filtered_data['time'] >= start_date) & (filtered_data['time'] <= end_date)]

# Display filtered data
st.title("Water Consumption Analysis Dashboard")
st.write(f"Showing {filtered_data.shape[0]} rows of filtered data.")
st.dataframe(filtered_data)

# Create and display charts
st.header("Charts")

# Time series chart for water consumption
fig1 = px.line(filtered_data, x='time', y='consume', title='Water Consumption Over Time', labels={'consume': 'Water Consumption (L)', 'time': 'Date'})
st.plotly_chart(fig1)

# Bar chart for total consumption by user
fig2 = px.bar(filtered_data, x='userId', y='totalConsume', title='Total Consumption by User', labels={'totalConsume': 'Total Consumption (L)', 'userId': 'User ID'})
st.plotly_chart(fig2)

# Pie chart for consumption at home vs not at home
fig3 = px.pie(filtered_data, names='isAtHome', values='consume', title='Consumption at Home vs Not at Home', labels={'isAtHome': 'At Home', 'consume': 'Water Consumption (L)'})
st.plotly_chart(fig3)

# Scatter plot for consumption vs total consumption
fig4 = px.scatter(filtered_data, x='totalConsume', y='consume', color='isAnomalous', title='Consumption vs Total Consumption', labels={'totalConsume': 'Total Consumption (L)', 'consume': 'Water Consumption (L)'})
st.plotly_chart(fig4)
