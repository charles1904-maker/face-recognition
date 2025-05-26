import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os
from PIL import Image

# Page config
st.set_page_config(
    page_title="Face Recognition Attendance System",
    page_icon="👥",
    layout="wide"
)

# Title and description
st.title("Face Recognition Attendance System")
st.markdown("---")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Daily Attendance", "Statistics"])

# Timestamp and date
ts = time.time()
date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

# Autorefresh
from streamlit_autorefresh import st_autorefresh
count = st_autorefresh(interval=2000, limit=100, key="attendance_refresh")

if page == "Daily Attendance":
    # Date selector
    selected_date = st.date_input("Select Date", datetime.now())
    formatted_date = selected_date.strftime("%d-%m-%Y")
    
    # Display attendance for selected date
    attendance_file_path = f"Attendance/Attendance_{formatted_date}.csv"
    
    if os.path.exists(attendance_file_path):
        df = pd.read_csv(attendance_file_path)
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_entries = len(df)
            st.metric("Total Entries", total_entries)
            
        with col2:
            clock_ins = len(df[df['STATUS'] == 'CLOCK IN'])
            st.metric("Clock Ins", clock_ins)
            
        with col3:
            clock_outs = len(df[df['STATUS'] == 'CLOCK OUT'])
            st.metric("Clock Outs", clock_outs)
        
        # Display full attendance data
        st.subheader(f"Attendance Data for {formatted_date}")
        
        # Style the dataframe
        def highlight_status(val):
            if val == 'CLOCK IN':
                return 'background-color: #90EE90'  # Light green
            elif val == 'CLOCK OUT':
                return 'background-color: #FFB6C1'  # Light red
            return ''
        
        styled_df = df.style.applymap(highlight_status, subset=['STATUS'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Download button for CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download CSV",
            csv,
            f"attendance_{formatted_date}.csv",
            "text/csv",
            key='download-csv'
        )
        
    else:
        st.info(f"No attendance record found for {formatted_date}")

elif page == "Statistics":
    st.subheader("Attendance Statistics")
    
    # Get all attendance files
    attendance_files = [f for f in os.listdir("Attendance") if f.startswith("Attendance_") and f.endswith(".csv")]
    
    if attendance_files:
        # Combine all data
        all_data = []
        for file in attendance_files:
            df = pd.read_csv(os.path.join("Attendance", file))
            all_data.append(df)
        
        if all_data:
            combined_df = pd.concat(all_data)
            
            # Calculate statistics
            total_students = combined_df['NAME'].nunique()
            total_days = len(attendance_files)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Students", total_students)
                st.metric("Total Days", total_days)
            
            with col2:
                # Safely get most common times
                clock_in_times = combined_df[combined_df['STATUS'] == 'CLOCK IN']['TIME']
                clock_out_times = combined_df[combined_df['STATUS'] == 'CLOCK OUT']['TIME']
                
                avg_clock_in = clock_in_times.mode().iloc[0] if not clock_in_times.empty else "No data"
                avg_clock_out = clock_out_times.mode().iloc[0] if not clock_out_times.empty else "No data"
                
                st.metric("Most Common Clock In Time", avg_clock_in)
                st.metric("Most Common Clock Out Time", avg_clock_out)
            
            # Show attendance patterns
            st.subheader("Student Attendance Patterns")
            try:
                # Calculate statistics separately
                days_present = combined_df.groupby('NAME')['DATE'].nunique().reset_index()
                clock_ins = combined_df[combined_df['STATUS'] == 'CLOCK IN'].groupby('NAME').size().reset_index(name='Total Clock Ins')
                clock_outs = combined_df[combined_df['STATUS'] == 'CLOCK OUT'].groupby('NAME').size().reset_index(name='Total Clock Outs')
                
                # Merge all statistics
                attendance_patterns = days_present.merge(clock_ins, on='NAME', how='left')
                attendance_patterns = attendance_patterns.merge(clock_outs, on='NAME', how='left')
                
                # Rename columns
                attendance_patterns.columns = ['Name', 'Days Present', 'Total Clock Ins', 'Total Clock Outs']
                
                # Fill NaN values with 0
                attendance_patterns = attendance_patterns.fillna(0)
                
                # Convert to integer
                attendance_patterns['Total Clock Ins'] = attendance_patterns['Total Clock Ins'].astype(int)
                attendance_patterns['Total Clock Outs'] = attendance_patterns['Total Clock Outs'].astype(int)
                
                # Add attendance rate
                attendance_patterns['Attendance Rate'] = (attendance_patterns['Days Present'] / total_days * 100).round(2).astype(str) + '%'
                
                # Sort by Days Present in descending order
                attendance_patterns = attendance_patterns.sort_values('Days Present', ascending=False)
                
                st.dataframe(attendance_patterns, use_container_width=True)
                
                # Add download button for patterns
                csv_patterns = attendance_patterns.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Attendance Patterns",
                    csv_patterns,
                    "attendance_patterns.csv",
                    "text/csv",
                    key='download-patterns'
                )
            except Exception as e:
                st.error(f"Error generating attendance patterns: {str(e)}")
    else:
        st.info("No attendance records found")

# python -m streamlit run face_recognition_project-main\app.py 
# To run the app, use the command:
# streamlit run app.py