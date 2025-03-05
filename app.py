import streamlit as st
import json
import calendar
from datetime import datetime

# --- Load the calendar data from file ---
@st.cache_data
def load_calendar_data():
    with open("calender.json", "r") as f:
        data = json.load(f)
    return data

cal_data = load_calendar_data()

# --- Allow user to select month and year within the given range ---
allowed_years = [2023]
allowed_months = {2023: [10, 11, 12]}  # Only October - December 2023

col1, col2 = st.columns([1, 1])
with col1:
    selected_year = st.selectbox("Select Year", allowed_years, index=0)
with col2:
    selected_month = st.selectbox("Select Month", allowed_months[selected_year], index=0, format_func=lambda x: calendar.month_name[x])

st.title(f"Calendar for {selected_year}-{selected_month:02d}")

# --- Read query params to check if a date was clicked ---
# query_params = st.experimental_get_query_params()
# selected_date = query_params.get("date", [None])[0]
try:
    selected_date = st.query_params['date']
except:
    selected_date = None

# --- Generate the calendar grid dynamically ---
cal = calendar.monthcalendar(selected_year, selected_month)
weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Display weekday headers
cols = st.columns(7)
for i, wd in enumerate(weekdays):
    cols[i].markdown(f"<div style='text-align:center; font-weight:bold'>{wd}</div>", unsafe_allow_html=True)

# Display each week as a row in the grid
for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].markdown(" ")
        else:
            # Format the date as YYYY-MM-DD
            date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
            
            # Determine the cell's background color:
            if date_str in cal_data:
                if any(activity.get("is_travel", False) for activity in cal_data[date_str]):
                    color = "#ffcccc"  # Light red for travel days
                else:
                    color = "#ccffcc"  # Light green for scheduled days
            else:
                color = "#f0f0f0"      # Light gray when no activities

            # Create a clickable cell using an HTML anchor.
            cell_html = f"""
            <div style="
                background-color:{color};
                padding:10px;
                text-align:center;
                border:1px solid #ccc;
                border-radius:4px;
                margin:2px;">
                <a href="?date={date_str}" style="text-decoration:none; color:black; font-weight:bold;">{day}</a>
            </div>
            """
            cols[i].markdown(cell_html, unsafe_allow_html=True)

# --- Show the modal/dialog for the selected date ---
if selected_date:
    st.markdown("---")
    with st.expander(f"Activities for {selected_date}", expanded=True):
        activities = cal_data.get(selected_date, [])
        if activities:
            for activity in activities:
                st.markdown(f"**Activity:** {activity['activity']}")
                st.markdown(f"**Type:** {activity['type']}")
                st.markdown(f"**Facilitator:** {activity['facilitator']}")
                st.markdown(f"**Location:** {activity['location']}")
                st.markdown(f"**Details:** {activity['details']}")
                st.markdown("---")
        else:
            st.write("No activities scheduled for this day.")
    if st.button("Close"):
        if 'date' in st.query_params:
            _ = st.query_params.pop('date')
        st.rerun() 

st.write("Click on a date cell to view its activities.")
