import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from data_manager import DataManager
from visualizations import create_progress_charts, create_custom_task_charts
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
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Task Progress Visualization", "🎯 Custom Tasks", 
        "⚙️ Task Settings", "📈 Detailed Analytics"
    ])
    
    with tab1:
        show_task_progress_visualization(data_manager, task_manager)
    
    with tab2:
        manage_custom_tasks(task_manager)
    
    with tab3:
        task_settings(task_manager)
    
    with tab4:
        show_detailed_analytics(data_manager, task_manager)

def show_task_progress_visualization(data_manager, task_manager):
    """Display progress bars, goal completion, and study time logging"""
    
    # Study Time Input Section
    st.header("⏰ Log Study Time")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Study time input form
        with st.form("log_study_form"):
            study_date = st.date_input(
                "Study Date",
                value=date.today(),
                max_value=date.today()
            )
            
            col_hours, col_minutes = st.columns(2)
            with col_hours:
                hours = st.number_input("Hours", min_value=0, max_value=24, value=1)
            with col_minutes:
                minutes = st.number_input("Minutes", min_value=0, max_value=59, value=0)
            
            notes = st.text_area(
                "Notes (optional)",
                placeholder="What did you study today?"
            )
            
            if st.form_submit_button("📝 Log Study Time", type="primary"):
                total_minutes = hours * 60 + minutes
                if total_minutes > 0:
                    success = data_manager.add_immersion_entry(study_date, total_minutes, notes)
                    if success:
                        st.success(f"Successfully logged {format_time(total_minutes)} for {study_date}")
                        st.rerun()
                    else:
                        st.error("Failed to log study time. Please try again.")
                else:
                    st.error("Please enter a valid study time.")
    
    with col2:
        # Recent entries with delete functionality
        st.subheader("Recent Entries")
        immersion_df = data_manager.load_immersion_data()
        if not immersion_df.empty:
            recent_entries = immersion_df.tail(5).iloc[::-1]  # Last 5, reversed
            
            for idx, row in recent_entries.iterrows():
                with st.container():
                    col_date, col_time, col_actions = st.columns([2, 2, 1])
                    
                    with col_date:
                        st.write(f"**{row['date'].strftime('%m/%d')}**")
                        if row['notes']:
                            st.caption(row['notes'])
                    
                    with col_time:
                        st.write(format_time(row['minutes']))
                    
                    with col_actions:
                        # Delete button
                        if st.button("🗑️", key=f"delete_{idx}", help="Delete entry"):
                            success = data_manager.delete_immersion_entry(row['date'])
                            if success:
                                st.success("Entry deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete entry")
                    
                    st.divider()
        else:
            st.info("No study sessions logged yet.")
    
    # Progress Bars Section
    st.header("📊 Progress Bars")
    
    # Load current data
    immersion_df = data_manager.load_immersion_data()
    total_minutes = immersion_df['minutes'].sum() if not immersion_df.empty else 0
    total_hours = total_minutes / 60
    progress_percentage = calculate_progress_percentage(total_minutes, 60000)
    
    # Immersion progress bar
    st.subheader("Immersion Study Progress")
    progress_bar_col, metrics_col = st.columns([3, 1])
    
    with progress_bar_col:
        st.progress(progress_percentage / 100, text=f"Progress: {progress_percentage:.1f}% of 1000h goal")
        st.write(f"**{total_hours:.1f}h** completed • **{1000 - total_hours:.1f}h** remaining")
    
    with metrics_col:
        st.metric("Total Hours", f"{total_hours:.1f}h")
        if not immersion_df.empty:
            avg_session = immersion_df['minutes'].mean()
            st.metric("Avg Session", format_time(avg_session))
    
    # Custom Tasks Progress Bars
    custom_tasks = task_manager.get_enabled_tasks()
    if custom_tasks:
        st.subheader("Custom Tasks Progress")
        
        for task in custom_tasks:
            task_data = task_manager.load_task_data(task['id'])
            
            if not task_data.empty:
                total_value = task_data['value'].sum()
                task_progress = min((total_value / task['target']) * 100, 100)
                
                progress_bar_col, metrics_col = st.columns([3, 1])
                
                with progress_bar_col:
                    st.progress(
                        task_progress / 100, 
                        text=f"{task['name']}: {task_progress:.1f}% of {task['target']} {task['unit']}"
                    )
                    remaining = max(0, task['target'] - total_value)
                    st.write(f"**{total_value:.1f} {task['unit']}** completed • **{remaining:.1f} {task['unit']}** remaining")
                
                with metrics_col:
                    st.metric(f"Total {task['unit']}", f"{total_value:.1f}")
                    if len(task_data) > 0:
                        avg_value = task_data['value'].mean()
                        st.metric("Daily Avg", f"{avg_value:.1f}")
            else:
                st.progress(0, text=f"{task['name']}: 0% of {task['target']} {task['unit']}")
                st.write(f"**0 {task['unit']}** completed • **{task['target']} {task['unit']}** remaining")
    
    # Goal Completion Section
    st.header("🏆 Goal Completion")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Immersion goal status
        if progress_percentage >= 100:
            st.success("🎉 Immersion Goal Completed!")
        elif progress_percentage >= 75:
            st.warning("🔥 Almost there! 75%+ completed")
        elif progress_percentage >= 50:
            st.info("📈 Halfway to your goal!")
        else:
            st.info("🌱 Just getting started")
        
        st.metric("Immersion Goal", f"{progress_percentage:.1f}%")
    
    with col2:
        # Custom tasks completion summary
        if custom_tasks:
            completed_tasks = 0
            for task in custom_tasks:
                task_data = task_manager.load_task_data(task['id'])
                if not task_data.empty:
                    total_value = task_data['value'].sum()
                    if total_value >= task['target']:
                        completed_tasks += 1
            
            completion_rate = (completed_tasks / len(custom_tasks)) * 100
            st.metric("Custom Tasks Completed", f"{completed_tasks}/{len(custom_tasks)}")
            
            if completion_rate == 100:
                st.success("🎉 All custom tasks completed!")
            elif completion_rate >= 50:
                st.info(f"📊 {completion_rate:.0f}% of tasks completed")
            else:
                st.info("🚀 Keep working on your goals!")
        else:
            st.info("No custom tasks configured")
    
    with col3:
        # Overall study streak
        if not immersion_df.empty:
            # Calculate study streak (consecutive days with entries)
            dates = immersion_df['date'].sort_values(ascending=False)
            current_streak = 0
            today = date.today()
            
            for i, study_date in enumerate(dates):
                expected_date = today - timedelta(days=i)
                if study_date == expected_date:
                    current_streak += 1
                else:
                    break
            
            st.metric("Study Streak", f"{current_streak} days")
            
            if current_streak >= 30:
                st.success("🔥 Amazing consistency!")
            elif current_streak >= 7:
                st.info("📅 Great weekly habit!")
            else:
                st.info("💪 Building the habit!")
        else:
            st.metric("Study Streak", "0 days")
            st.info("🌟 Start your journey!")





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
    
    # Overview of all custom tasks
    if len(enabled_tasks) > 1:
        st.subheader("All Custom Tasks Overview")
        
        # Create comparison chart
        task_comparison_data = []
        for task in enabled_tasks:
            summary = task_manager.get_task_summary(task['id'])
            task_comparison_data.append({
                'name': task['name'],
                'progress': summary['progress_percentage'],
                'total': summary['total_value'],
                'target': task['target'],
                'unit': task['unit']
            })
        
        # Progress comparison chart
        names = [data['name'] for data in task_comparison_data]
        progress_values = [data['progress'] for data in task_comparison_data]
        
        fig = go.Figure(data=[
            go.Bar(
                x=names,
                y=progress_values,
                text=[f"{val:.1f}%" for val in progress_values],
                textposition='auto',
                marker_color=['#4ECDC4', '#FF6B6B', '#45B7D1', '#96CEB4'][:len(names)]
            )
        ])
        
        fig.update_layout(
            title="Custom Tasks Progress Comparison",
            xaxis_title="Tasks",
            yaxis_title="Completion Percentage (%)",
            yaxis=dict(range=[0, 100]),
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_progress = sum(progress_values) / len(progress_values)
            st.metric("Average Progress", f"{avg_progress:.1f}%")
        
        with col2:
            completed_tasks = len([p for p in progress_values if p >= 100])
            st.metric("Completed Tasks", f"{completed_tasks}/{len(progress_values)}")
        
        with col3:
            active_tasks = len([p for p in progress_values if 0 < p < 100])
            st.metric("In Progress", f"{active_tasks} tasks")

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
    
    # Show current tasks summary
    st.subheader("Current Tasks")
    
    all_tasks = task_manager.get_all_tasks()
    if all_tasks:
        for task in all_tasks:
            summary = task_manager.get_task_summary(task['id'])
            status = "✅ Enabled" if task.get('enabled', True) else "❌ Disabled"
            
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.write(f"**{task['name']}**")
                st.caption(f"Target: {task['target']} {task['unit']}")
            
            with col2:
                st.metric("Progress", f"{summary['total_value']:.0f} {task['unit']}")
            
            with col3:
                st.metric("Completion", f"{summary['progress_percentage']:.1f}%")
            
            with col4:
                st.write(status)
                if st.button("🗑️", key=f"delete_{task['id']}", help="Delete task"):
                    success = task_manager.delete_task(task['id'])
                    if success:
                        st.success("Task deleted!")
                        st.rerun()
            
            st.divider()
    else:
        st.info("No tasks configured yet. Add your first task above!")

def show_detailed_analytics(data_manager, task_manager):
    """Show detailed analytics and trends"""
    st.header("Detailed Analytics")
    
    # Load data
    immersion_df = data_manager.load_immersion_data()
    custom_tasks = task_manager.get_enabled_tasks()
    
    if immersion_df.empty and not custom_tasks:
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
