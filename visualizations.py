import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def create_progress_charts(immersion_df: pd.DataFrame, total_minutes: int):
    """Create progress visualization charts for immersion study"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Progress bar chart
        st.subheader("Goal Progress")
        
        goal_minutes = 60000  # 1000 hours
        progress_percentage = (total_minutes / goal_minutes) * 100
        remaining_percentage = 100 - progress_percentage
        
        # Create a horizontal bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=['Progress'],
            x=[progress_percentage],
            orientation='h',
            name='Completed',
            marker_color='#2E8B57',
            text=f'{progress_percentage:.1f}%',
            textposition='inside'
        ))
        
        fig.add_trace(go.Bar(
            y=['Progress'],
            x=[remaining_percentage],
            orientation='h',
            name='Remaining',
            marker_color='#F0F0F0',
            text=f'{remaining_percentage:.1f}%',
            textposition='inside'
        ))
        
        fig.update_layout(
            barmode='stack',
            xaxis=dict(range=[0, 100], title='Percentage'),
            yaxis=dict(title=''),
            height=200,
            showlegend=True,
            title="1000-Hour Goal Progress"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Pie chart
        st.subheader("Time Distribution")
        
        completed_hours = total_minutes / 60
        remaining_hours = 1000 - completed_hours
        
        fig = go.Figure(data=[go.Pie(
            labels=['Completed', 'Remaining'],
            values=[completed_hours, remaining_hours],
            hole=0.4,
            marker_colors=['#2E8B57', '#F0F0F0']
        )])
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )
        
        fig.update_layout(
            title="Study Time Breakdown",
            height=300,
            annotations=[dict(text=f'{completed_hours:.1f}h<br>Completed', 
                            x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Daily study time trend (last 30 days)
    if len(immersion_df) > 1:
        st.subheader("Daily Study Time Trend")
        
        # Get last 30 days of data
        recent_df = immersion_df.tail(30).copy()
        recent_df['hours'] = recent_df['minutes'] / 60
        
        fig = px.line(
            recent_df,
            x='date',
            y='hours',
            title='Daily Study Hours (Last 30 Sessions)',
            labels={'hours': 'Hours', 'date': 'Date'},
            markers=True
        )
        
        # Add average line
        avg_hours = recent_df['hours'].mean()
        fig.add_hline(
            y=avg_hours,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Average: {avg_hours:.1f}h"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Cumulative progress chart
    if len(immersion_df) > 1:
        st.subheader("Cumulative Progress")
        
        # Calculate cumulative minutes
        df_cumulative = immersion_df.copy()
        df_cumulative['cumulative_minutes'] = df_cumulative['minutes'].cumsum()
        df_cumulative['cumulative_hours'] = df_cumulative['cumulative_minutes'] / 60
        df_cumulative['progress_percentage'] = (df_cumulative['cumulative_minutes'] / 60000) * 100
        
        fig = px.area(
            df_cumulative,
            x='date',
            y='cumulative_hours',
            title='Cumulative Study Hours Over Time',
            labels={'cumulative_hours': 'Cumulative Hours', 'date': 'Date'}
        )
        
        # Add goal line
        fig.add_hline(
            y=1000,
            line_dash="dash",
            line_color="gold",
            annotation_text="1000 Hour Goal"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def create_toeic_charts(toeic_df: pd.DataFrame):
    """Create TOEIC task completion visualization charts"""
    
    if toeic_df.empty:
        st.info("No TOEIC data available for visualization")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Task completion heatmap-style chart
        st.subheader("Task Completion Overview")
        
        # Prepare data for stacked bar chart
        task_data = toeic_df[['date', 'shadowing', 'vocabulary', 'reading']].copy()
        task_data['date_str'] = task_data['date'].astype(str)
        
        fig = go.Figure()
        
        # Add bars for each task
        fig.add_trace(go.Bar(
            name='Shadowing',
            x=task_data['date_str'],
            y=task_data['shadowing'].astype(int),
            marker_color='#FF6B6B'
        ))
        
        fig.add_trace(go.Bar(
            name='Vocabulary',
            x=task_data['date_str'],
            y=task_data['vocabulary'].astype(int),
            marker_color='#4ECDC4'
        ))
        
        fig.add_trace(go.Bar(
            name='Reading',
            x=task_data['date_str'],
            y=task_data['reading'].astype(int),
            marker_color='#45B7D1'
        ))
        
        fig.update_layout(
            barmode='stack',
            title='Daily Task Completion',
            xaxis_title='Date',
            yaxis_title='Tasks Completed',
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Completion rate pie charts
        st.subheader("Overall Completion Rates")
        
        # Calculate completion rates
        shadowing_rate = toeic_df['shadowing'].mean()
        vocabulary_rate = toeic_df['vocabulary'].mean()
        reading_rate = toeic_df['reading'].mean()
        
        rates_data = {
            'Task': ['Shadowing', 'Vocabulary', 'Reading'],
            'Completion Rate': [shadowing_rate * 100, vocabulary_rate * 100, reading_rate * 100]
        }
        
        fig = px.bar(
            rates_data,
            x='Task',
            y='Completion Rate',
            title='Task Completion Rates (%)',
            color='Task',
            color_discrete_map={
                'Shadowing': '#FF6B6B',
                'Vocabulary': '#4ECDC4',
                'Reading': '#45B7D1'
            }
        )
        
        fig.update_layout(
            height=400,
            yaxis=dict(range=[0, 100]),
            showlegend=False
        )
        
        # Add percentage labels on bars
        for i, rate in enumerate(rates_data['Completion Rate']):
            fig.add_annotation(
                x=i,
                y=rate + 2,
                text=f"{rate:.1f}%",
                showarrow=False,
                font=dict(size=12, color="black")
            )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Streak analysis
    st.subheader("Completion Streaks")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Calculate current streak for all tasks
        current_streak = calculate_current_streak(toeic_df, 'total_completed', 3)
        st.metric("Perfect Day Streak", f"{current_streak} days", help="Consecutive days with all 3 tasks completed")
    
    with col2:
        # Calculate best streak
        best_streak = calculate_best_streak(toeic_df, 'total_completed', 3)
        st.metric("Best Streak", f"{best_streak} days", help="Longest streak of perfect days")
    
    with col3:
        # Recent average
        recent_avg = toeic_df.tail(7)['total_completed'].mean()
        st.metric("7-Day Average", f"{recent_avg:.1f}/3", help="Average tasks completed in last 7 days")

def calculate_current_streak(df: pd.DataFrame, column: str, target_value) -> int:
    """Calculate current streak of target value achievements"""
    if df.empty:
        return 0
    
    streak = 0
    for i in range(len(df) - 1, -1, -1):  # Go backwards from most recent
        if df.iloc[i][column] == target_value:
            streak += 1
        else:
            break
    
    return streak

def calculate_best_streak(df: pd.DataFrame, column: str, target_value) -> int:
    """Calculate the best (longest) streak of target value achievements"""
    if df.empty:
        return 0
    
    current_streak = 0
    best_streak = 0
    
    for _, row in df.iterrows():
        if row[column] == target_value:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        else:
            current_streak = 0
    
    return best_streak

def create_weekly_summary_chart(immersion_df: pd.DataFrame, toeic_df: pd.DataFrame):
    """Create a weekly summary combining both immersion and TOEIC data"""
    
    if immersion_df.empty and toeic_df.empty:
        return
    
    st.subheader("Weekly Summary")
    
    # Prepare weekly aggregation
    if not immersion_df.empty:
        immersion_weekly = immersion_df.copy()
        immersion_weekly['week'] = pd.to_datetime(immersion_weekly['date']).dt.to_period('W')
        immersion_weekly = immersion_weekly.groupby('week')['minutes'].sum().reset_index()
        immersion_weekly['hours'] = immersion_weekly['minutes'] / 60
        immersion_weekly['week_str'] = immersion_weekly['week'].astype(str)
    
    if not toeic_df.empty:
        toeic_weekly = toeic_df.copy()
        toeic_weekly['week'] = pd.to_datetime(toeic_weekly['date']).dt.to_period('W')
        toeic_weekly = toeic_weekly.groupby('week')['total_completed'].sum().reset_index()
        toeic_weekly['week_str'] = toeic_weekly['week'].astype(str)
    
    # Create dual-axis chart if both datasets exist
    if not immersion_df.empty and not toeic_df.empty:
        fig = go.Figure()
        
        # Add immersion hours
        fig.add_trace(go.Bar(
            name='Study Hours',
            x=immersion_weekly['week_str'],
            y=immersion_weekly['hours'],
            yaxis='y',
            marker_color='#2E8B57'
        ))
        
        # Add TOEIC tasks
        fig.add_trace(go.Scatter(
            name='TOEIC Tasks',
            x=toeic_weekly['week_str'],
            y=toeic_weekly['total_completed'],
            yaxis='y2',
            mode='lines+markers',
            marker_color='#FF6B6B',
            line=dict(width=3)
        ))
        
        fig.update_layout(
            title='Weekly Study Hours vs TOEIC Task Completion',
            xaxis_title='Week',
            yaxis=dict(title='Study Hours', side='left'),
            yaxis2=dict(title='TOEIC Tasks Completed', side='right', overlaying='y'),
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
