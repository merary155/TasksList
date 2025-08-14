import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from data_manager import DataManager
from visualizations import create_progress_charts, create_toeic_charts, create_custom_task_charts
from utils import format_time, calculate_progress_percentage
from task_config_manager import TaskConfigManager

def main():
    st.set_page_config(
        page_title="Study Progress Management System",
        page_icon="📚",
        layout="wide"
    )
    
    # Initialize data managers
    data_manager = DataManager()
    task_manager = TaskConfigManager()
    
    # Main title
    st.title("📚 Study Progress Management System")
    st.markdown("Track your study progress with customizable tasks")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", "⏰ Log Study Time", "✅ TOEIC Tasks", 
        "🎯 Custom Tasks", "⚙️ Task Settings", "📈 Detailed Analytics"
    ])
    
    with tab1:
        show_dashboard(data_manager, task_manager)
    
    with tab2:
        log_study_time(data_manager)
    
    with tab3:
        log_toeic_tasks(data_manager)
    
    with tab4:
        manage_custom_tasks(task_manager)
    
    with tab5:
        task_settings(task_manager)
    
    with tab6:
        show_detailed_analytics(data_manager, task_manager)

def show_dashboard(data_manager, task_manager):
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
    
    # Custom tasks overview
    st.subheader("Custom Tasks Overview")
    custom_tasks = task_manager.get_enabled_tasks()
    if custom_tasks:
        cols = st.columns(min(len(custom_tasks), 4))
        for i, task in enumerate(custom_tasks):
            with cols[i % 4]:
                summary = task_manager.get_task_summary(task['id'])
                st.metric(
                    label=task['name'],
                    value=f"{summary['total_value']:.0f}{task['unit']}",
                    delta=f"{summary['progress_percentage']:.1f}% complete"
                )
    else:
        st.info("No custom tasks configured. Go to Task Settings to add your own tasks!")

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

def manage_custom_tasks(task_manager):
    """Interface for managing custom task progress"""
    st.header("🎯 Custom Task Management")
    
    # Get enabled tasks
    enabled_tasks = task_manager.get_enabled_tasks()
    
    if not enabled_tasks:
        st.info("No custom tasks available. Go to Task Settings to create your first task!")
        return
    
    # Task selector
    task_options = {task['name']: task['id'] for task in enabled_tasks}
    selected_task_name = st.selectbox("Select Task", list(task_options.keys()))
    selected_task_id = task_options[selected_task_name]
    selected_task = task_manager.get_task_by_id(selected_task_id)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"Log Progress: {selected_task['name']}")
        
        # Date selection
        selected_date = st.date_input(
            "Date",
            value=date.today(),
            max_value=date.today()
        )
        
        # Value input
        value = st.number_input(
            f"Value ({selected_task['unit']})",
            min_value=0.0,
            value=0.0,
            step=1.0 if selected_task['unit'] in ['回', '問', '題', '個', '本', '日'] else 0.1
        )
        
        # Notes
        notes = st.text_area("Notes (optional)", placeholder="Additional details about this session...")
        
        # Submit button
        if st.button("Log Progress", type="primary"):
            if value > 0:
                success = task_manager.add_task_entry(selected_task_id, selected_date, value, notes)
                if success:
                    st.success(f"Successfully logged {value} {selected_task['unit']} for {selected_task['name']}")
                    st.rerun()
                else:
                    st.error("Failed to log progress. Please try again.")
            else:
                st.error("Please enter a valid value.")
    
    with col2:
        # Task summary
        st.subheader("Task Summary")
        summary = task_manager.get_task_summary(selected_task_id)
        
        st.metric(
            "Total Progress",
            f"{summary['total_value']:.1f} {summary['unit']}",
            f"{summary['progress_percentage']:.1f}% of goal"
        )
        
        st.metric(
            "Days Logged",
            summary['days_logged']
        )
        
        if summary['days_logged'] > 0:
            st.metric(
                "Daily Average",
                f"{summary['average_daily']:.1f} {summary['unit']}"
            )
        
        # Progress bar
        progress = min(summary['progress_percentage'] / 100, 1.0)
        st.progress(progress, text=f"Goal: {summary['target']} {summary['unit']}")
        
        # Recent entries
        st.subheader("Recent Entries")
        task_data = task_manager.load_task_data(selected_task_id)
        if not task_data.empty:
            recent_entries = task_data.tail(5).iloc[::-1]
            for _, row in recent_entries.iterrows():
                with st.container():
                    st.write(f"**{row['date'].strftime('%m/%d')}**: {row['value']:.1f} {selected_task['unit']}")
                    if row['notes']:
                        st.caption(row['notes'])
        else:
            st.info("No entries logged yet.")
    
    # Task visualization
    if not task_data.empty:
        st.subheader("Progress Visualization")
        create_custom_task_charts(task_data, selected_task)

def task_settings(task_manager):
    """Interface for configuring custom tasks"""
    st.header("⚙️ Task Settings")
    
    # Add new task section
    st.subheader("Add New Task")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_task_name = st.text_input(
            "Task Name",
            placeholder="例: 英語リーディング",
            help="Enter a descriptive name for your task"
        )
    
    with col2:
        unit_options = task_manager.get_available_units()
        new_task_unit = st.selectbox("Unit", unit_options)
    
    with col3:
        new_task_target = st.number_input(
            "Target Goal",
            min_value=1,
            value=100,
            help="Set your target goal for this task"
        )
    
    if st.button("Add Task", type="primary"):
        if new_task_name:
            is_valid, message = task_manager.validate_task_input(
                new_task_name, new_task_unit, new_task_target
            )
            if is_valid:
                success = task_manager.add_task(new_task_name, new_task_unit, new_task_target)
                if success:
                    st.success(f"Successfully added task: {new_task_name}")
                    st.rerun()
                else:
                    st.error("Failed to add task. Please try again.")
            else:
                st.error(message)
        else:
            st.error("Please enter a task name.")
    
    # Manage existing tasks
    st.subheader("Manage Existing Tasks")
    
    all_tasks = task_manager.get_all_tasks()
    if all_tasks:
        for task in all_tasks:
            with st.expander(f"{task['name']} ({task['unit']})", expanded=False):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    # Edit task name
                    new_name = st.text_input(
                        "Name",
                        value=task['name'],
                        key=f"name_{task['id']}"
                    )
                
                with col2:
                    # Edit unit
                    unit_idx = unit_options.index(task['unit']) if task['unit'] in unit_options else 0
                    new_unit = st.selectbox(
                        "Unit",
                        unit_options,
                        index=unit_idx,
                        key=f"unit_{task['id']}"
                    )
                
                with col3:
                    # Edit target
                    new_target = st.number_input(
                        "Target",
                        min_value=1,
                        value=task['target'],
                        key=f"target_{task['id']}"
                    )
                
                with col4:
                    # Enable/disable toggle
                    enabled = st.checkbox(
                        "Enabled",
                        value=task.get('enabled', True),
                        key=f"enabled_{task['id']}"
                    )
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Update", key=f"update_{task['id']}"):
                        success = task_manager.update_task(
                            task['id'], new_name, new_unit, new_target, enabled
                        )
                        if success:
                            st.success("Task updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update task.")
                
                with col2:
                    # Show task summary
                    summary = task_manager.get_task_summary(task['id'])
                    st.write(f"Progress: {summary['progress_percentage']:.1f}%")
                
                with col3:
                    if st.button("Delete", key=f"delete_{task['id']}", type="secondary"):
                        if st.button("Confirm Delete", key=f"confirm_delete_{task['id']}", type="secondary"):
                            success = task_manager.delete_task(task['id'])
                            if success:
                                st.success("Task deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete task.")
    else:
        st.info("No tasks configured yet. Add your first task above!")

def show_detailed_analytics(data_manager, task_manager):
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
            cutoff_date = (datetime.now() - timedelta(days=7)).date()
            filtered_df = immersion_df[immersion_df['date'] >= cutoff_date]
        elif period == "Last 30 days":
            cutoff_date = (datetime.now() - timedelta(days=30)).date()
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
    
    # Custom tasks analytics
    custom_tasks = task_manager.get_enabled_tasks()
    if custom_tasks:
        st.subheader("🎯 Custom Tasks Analytics")
        
        # Allow user to select which custom task to analyze
        task_options = {task['name']: task['id'] for task in custom_tasks}
        if task_options:
            selected_task_name = st.selectbox("Select Custom Task for Analysis", list(task_options.keys()))
            selected_task_id = task_options[selected_task_name]
            selected_task = task_manager.get_task_by_id(selected_task_id)
            
            task_data = task_manager.load_task_data(selected_task_id)
            if not task_data.empty:
                create_custom_task_charts(task_data, selected_task)
            else:
                st.info(f"No data available for {selected_task['name']}")
    
    # Data export section
    st.subheader("📁 Data Export")
    col1, col2, col3 = st.columns(3)
    
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
    
    with col3:
        if st.button("Download Custom Task Data"):
            if custom_tasks:
                # Export all custom task data as a combined file
                all_custom_data = []
                for task in custom_tasks:
                    task_data = task_manager.load_task_data(task['id'])
                    if not task_data.empty:
                        task_data_export = task_data.copy()
                        task_data_export['task_name'] = task['name']
                        task_data_export['task_unit'] = task['unit']
                        all_custom_data.append(task_data_export)
                
                if all_custom_data:
                    combined_df = pd.concat(all_custom_data, ignore_index=True)
                    csv = combined_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"custom_tasks_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No custom task data to export")
            else:
                st.warning("No custom tasks configured")

if __name__ == "__main__":
    main()
