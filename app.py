import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from data_manager import DataManager
from visualizations import create_progress_charts, create_toeic_charts
from utils import format_time, calculate_progress_percentage

def main():
    st.set_page_config(
        page_title="Study Progress Management System",
        page_icon="📚",
        layout="wide"
    )
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Main title
    st.title("📚 Study Progress Management System")
    st.markdown("Track your immersion hours and TOEIC preparation progress")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "⏰ Log Study Time", "✅ TOEIC Tasks", "📈 Detailed Analytics"])
    
    with tab1:
        show_dashboard(data_manager)
    
    with tab2:
        log_study_time(data_manager)
    
    with tab3:
        log_toeic_tasks(data_manager)
    
    with tab4:
        show_detailed_analytics(data_manager)

def show_dashboard(data_manager):
    """Display the main dashboard with current progress"""
    st.header("Progress Overview")
    
    # Load current data
    immersion_df = data_manager.load_immersion_data()
    toeic_df = data_manager.load_toeic_data()
    
    # Calculate current statistics
    total_minutes = immersion_df['minutes'].sum() if not immersion_df.empty else 0
    total_hours = total_minutes / 60
    progress_percentage = calculate_progress_percentage(total_minutes, 60000)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Study Time",
            value=format_time(total_minutes),
            delta=f"{progress_percentage:.1f}% of goal"
        )
    
    with col2:
        st.metric(
            label="Hours Completed",
            value=f"{total_hours:.1f}h",
            delta=f"{1000 - total_hours:.1f}h remaining"
        )
    
    with col3:
        if not toeic_df.empty:
            recent_completion = toeic_df.tail(7)['total_completed'].mean()
            st.metric(
                label="Avg Daily TOEIC Tasks",
                value=f"{recent_completion:.1f}/3",
                delta="Last 7 days"
            )
        else:
            st.metric(label="Avg Daily TOEIC Tasks", value="0/3")
    
    with col4:
        days_studied = len(immersion_df) if not immersion_df.empty else 0
        st.metric(
            label="Days Studied",
            value=str(days_studied),
            delta="Total sessions"
        )
    
    # Progress charts
    if not immersion_df.empty:
        st.subheader("Progress Visualization")
        create_progress_charts(immersion_df, total_minutes)
    
    # Recent TOEIC performance
    if not toeic_df.empty:
        st.subheader("Recent TOEIC Performance")
        create_toeic_charts(toeic_df.tail(14))  # Last 14 days

def log_study_time(data_manager):
    """Interface for logging daily study time"""
    st.header("Log Study Time")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Date selection
        selected_date = st.date_input(
            "Study Date",
            value=date.today(),
            max_value=date.today()
        )
        
        # Time input
        hours = st.number_input("Hours", min_value=0, max_value=24, value=0)
        minutes = st.number_input("Minutes", min_value=0, max_value=59, value=0)
        
        total_minutes = hours * 60 + minutes
        
        if total_minutes > 0:
            st.info(f"Total time: {format_time(total_minutes)}")
        
        # Notes (optional)
        notes = st.text_area("Notes (optional)", placeholder="What did you study today?")
        
        # Submit button
        if st.button("Log Study Time", type="primary"):
            if total_minutes > 0:
                success = data_manager.add_immersion_entry(selected_date, total_minutes, notes)
                if success:
                    st.success(f"Successfully logged {format_time(total_minutes)} for {selected_date}")
                    st.rerun()
                else:
                    st.error("Failed to log study time. Please try again.")
            else:
                st.error("Please enter a valid study time.")
    
    with col2:
        # Recent entries
        st.subheader("Recent Entries")
        immersion_df = data_manager.load_immersion_data()
        if not immersion_df.empty:
            recent_entries = immersion_df.tail(5).iloc[::-1]  # Last 5, reversed
            for _, row in recent_entries.iterrows():
                with st.container():
                    st.write(f"**{row['date'].strftime('%m/%d')}**: {format_time(row['minutes'])}")
                    if row['notes']:
                        st.caption(row['notes'])
        else:
            st.info("No study sessions logged yet.")

def log_toeic_tasks(data_manager):
    """Interface for logging TOEIC task completion"""
    st.header("TOEIC Daily Tasks")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Date selection
        selected_date = st.date_input(
            "Task Date",
            value=date.today(),
            max_value=date.today(),
            key="toeic_date"
        )
        
        st.subheader("Task Completion")
        
        # Task checkboxes
        shadowing = st.checkbox(
            "Shadowing Practice (30 minutes)",
            help="Complete 30 minutes of shadowing practice"
        )
        
        vocabulary = st.checkbox(
            "Vocabulary Test (200 questions)",
            help="Complete 200 vocabulary questions"
        )
        
        reading = st.checkbox(
            "Reading Comprehension (3 triple passages)",
            help="Complete 3 triple passage reading exercises"
        )
        
        # Additional notes
        notes = st.text_area(
            "Task Notes (optional)",
            placeholder="Any observations or difficulties with today's tasks?"
        )
        
        # Submit button
        if st.button("Log TOEIC Tasks", type="primary"):
            success = data_manager.add_toeic_entry(
                selected_date, shadowing, vocabulary, reading, notes
            )
            if success:
                completed_count = sum([shadowing, vocabulary, reading])
                st.success(f"Successfully logged {completed_count}/3 tasks for {selected_date}")
                st.rerun()
            else:
                st.error("Failed to log TOEIC tasks. Please try again.")
    
    with col2:
        # Recent task completion
        st.subheader("Recent Completion")
        toeic_df = data_manager.load_toeic_data()
        if not toeic_df.empty:
            recent_entries = toeic_df.tail(7).iloc[::-1]  # Last 7 days, reversed
            for _, row in recent_entries.iterrows():
                with st.container():
                    completed = row['total_completed']
                    completion_emoji = "✅" if completed == 3 else "⚠️" if completed > 0 else "❌"
                    st.write(f"**{row['date'].strftime('%m/%d')}** {completion_emoji} {completed}/3 tasks")
                    
                    # Show individual task status
                    task_status = []
                    if row['shadowing']:
                        task_status.append("🗣️ Shadowing")
                    if row['vocabulary']:
                        task_status.append("📝 Vocabulary")
                    if row['reading']:
                        task_status.append("📖 Reading")
                    
                    if task_status:
                        st.caption(" • ".join(task_status))
        else:
            st.info("No TOEIC tasks logged yet.")

def show_detailed_analytics(data_manager):
    """Show detailed analytics and trends"""
    st.header("Detailed Analytics")
    
    # Load data
    immersion_df = data_manager.load_immersion_data()
    toeic_df = data_manager.load_toeic_data()
    
    if immersion_df.empty and toeic_df.empty:
        st.info("No data available for analytics. Start logging your study sessions!")
        return
    
    # Immersion Analytics
    if not immersion_df.empty:
        st.subheader("📊 Immersion Study Analytics")
        
        # Time period selector
        period = st.selectbox("Analysis Period", ["Last 7 days", "Last 30 days", "All time"])
        
        if period == "Last 7 days":
            cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=7)
            filtered_df = immersion_df[immersion_df['date'] >= cutoff_date]
        elif period == "Last 30 days":
            cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=30)
            filtered_df = immersion_df[immersion_df['date'] >= cutoff_date]
        else:
            filtered_df = immersion_df
        
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Daily study time trend
                fig = px.line(
                    filtered_df,
                    x='date',
                    y='minutes',
                    title='Daily Study Time Trend',
                    labels={'minutes': 'Minutes', 'date': 'Date'}
                )
                fig.update_traces(mode='lines+markers')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Study time distribution
                fig = px.histogram(
                    filtered_df,
                    x='minutes',
                    nbins=20,
                    title='Study Time Distribution',
                    labels={'minutes': 'Minutes per Session', 'count': 'Frequency'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            avg_daily = filtered_df['minutes'].mean()
            total_time = filtered_df['minutes'].sum()
            st.write(f"**Average daily study time**: {format_time(avg_daily)}")
            st.write(f"**Total study time in period**: {format_time(total_time)}")
    
    # TOEIC Analytics
    if not toeic_df.empty:
        st.subheader("✅ TOEIC Task Analytics")
        
        # Task completion trends
        fig = px.line(
            toeic_df.tail(30),  # Last 30 days
            x='date',
            y=['shadowing', 'vocabulary', 'reading'],
            title='TOEIC Task Completion Trends (Last 30 Days)',
            labels={'value': 'Completed (1=Yes, 0=No)', 'date': 'Date'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Completion rate summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            shadowing_rate = toeic_df['shadowing'].mean() * 100
            st.metric("Shadowing Completion Rate", f"{shadowing_rate:.1f}%")
        
        with col2:
            vocab_rate = toeic_df['vocabulary'].mean() * 100
            st.metric("Vocabulary Completion Rate", f"{vocab_rate:.1f}%")
        
        with col3:
            reading_rate = toeic_df['reading'].mean() * 100
            st.metric("Reading Completion Rate", f"{reading_rate:.1f}%")
    
    # Data export section
    st.subheader("📁 Data Export")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download Immersion Data"):
            if not immersion_df.empty:
                csv = immersion_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"immersion_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No immersion data to export")
    
    with col2:
        if st.button("Download TOEIC Data"):
            if not toeic_df.empty:
                csv = toeic_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"toeic_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No TOEIC data to export")

if __name__ == "__main__":
    main()
