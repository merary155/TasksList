from datetime import datetime, date, timedelta
import pandas as pd

def format_time(minutes: float) -> str:
    """Format minutes into a human-readable time string"""
    if minutes < 60:
        return f"{int(minutes)}m"
    
    hours = int(minutes // 60)
    remaining_minutes = int(minutes % 60)
    
    if remaining_minutes == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {remaining_minutes}m"

def calculate_progress_percentage(current_minutes: int, target_minutes: int) -> float:
    """Calculate progress percentage towards target"""
    if target_minutes <= 0:
        return 0.0
    return min((current_minutes / target_minutes) * 100, 100.0)

def get_date_range_options():
    """Get common date range options for filtering"""
    today = date.today()
    return {
        "Last 7 days": today - timedelta(days=7),
        "Last 30 days": today - timedelta(days=30),
        "Last 90 days": today - timedelta(days=90),
        "This year": date(today.year, 1, 1),
        "All time": None
    }

def filter_dataframe_by_date_range(df: pd.DataFrame, start_date: date = None, end_date: date = None) -> pd.DataFrame:
    """Filter a dataframe by date range"""
    if df.empty:
        return df
    
    filtered_df = df.copy()
    
    if start_date:
        filtered_df = filtered_df[filtered_df['date'] >= start_date]
    
    if end_date:
        filtered_df = filtered_df[filtered_df['date'] <= end_date]
    
    return filtered_df

def calculate_study_streak(df: pd.DataFrame, min_minutes: int = 1) -> dict:
    """Calculate current and longest study streaks"""
    if df.empty:
        return {"current_streak": 0, "longest_streak": 0}
    
    # Sort by date
    df_sorted = df.sort_values('date')
    
    # Create a complete date range from first to last study date
    date_range = pd.date_range(
        start=df_sorted['date'].min(),
        end=df_sorted['date'].max(),
        freq='D'
    ).date
    
    # Create a set of study dates that meet minimum requirement
    study_dates = set(df_sorted[df_sorted['minutes'] >= min_minutes]['date'])
    
    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    # Start from today and go backwards for current streak
    current_date = date.today()
    while current_date in study_dates:
        current_streak += 1
        current_date -= timedelta(days=1)
    
    # Calculate longest streak
    for check_date in date_range:
        if check_date in study_dates:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0
    
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }

def get_study_statistics(df: pd.DataFrame) -> dict:
    """Get comprehensive study statistics"""
    if df.empty:
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "total_hours": 0,
            "average_session": 0,
            "median_session": 0,
            "most_productive_day": None,
            "least_productive_day": None
        }
    
    total_sessions = len(df)
    total_minutes = df['minutes'].sum()
    total_hours = total_minutes / 60
    average_session = df['minutes'].mean()
    median_session = df['minutes'].median()
    
    # Find most and least productive days
    max_day = df.loc[df['minutes'].idxmax()]
    min_day = df.loc[df['minutes'].idxmin()]
    
    return {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "total_hours": total_hours,
        "average_session": average_session,
        "median_session": median_session,
        "most_productive_day": {
            "date": max_day['date'],
            "minutes": max_day['minutes']
        },
        "least_productive_day": {
            "date": min_day['date'],
            "minutes": min_day['minutes']
        }
    }

def validate_study_time_input(hours: int, minutes: int) -> tuple[bool, str]:
    """Validate study time input"""
    if hours < 0 or minutes < 0:
        return False, "Time values cannot be negative"
    
    if hours > 24:
        return False, "Hours cannot exceed 24"
    
    if minutes >= 60:
        return False, "Minutes must be less than 60"
    
    total_minutes = hours * 60 + minutes
    if total_minutes == 0:
        return False, "Please enter a valid study time"
    
    if total_minutes > 24 * 60:  # More than 24 hours
        return False, "Total study time cannot exceed 24 hours"
    
    return True, "Valid input"

def get_motivation_message(progress_percentage: float) -> str:
    """Get a motivational message based on progress"""
    if progress_percentage >= 100:
        return "🎉 Congratulations! You've achieved your 1000-hour goal!"
    elif progress_percentage >= 90:
        return "🔥 Almost there! Just a little more to reach your goal!"
    elif progress_percentage >= 75:
        return "💪 Great progress! You're in the final stretch!"
    elif progress_percentage >= 50:
        return "⚡ Halfway there! Keep up the excellent work!"
    elif progress_percentage >= 25:
        return "🌟 Good momentum! You're building a strong foundation!"
    elif progress_percentage >= 10:
        return "🚀 Great start! Every hour counts towards your goal!"
    else:
        return "🌱 Beginning your journey! The first step is always the hardest!"

def calculate_estimated_completion_date(current_minutes: int, target_minutes: int, daily_average: float) -> date:
    """Calculate estimated completion date based on current progress and average"""
    if daily_average <= 0 or current_minutes >= target_minutes:
        return None
    
    remaining_minutes = target_minutes - current_minutes
    days_remaining = remaining_minutes / daily_average
    
    completion_date = date.today() + timedelta(days=int(days_remaining))
    return completion_date

def export_data_summary(immersion_df: pd.DataFrame, toeic_df: pd.DataFrame) -> str:
    """Generate a text summary of all data for export"""
    summary_lines = []
    summary_lines.append("STUDY PROGRESS SUMMARY")
    summary_lines.append("=" * 50)
    summary_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")
    
    # Immersion summary
    if not immersion_df.empty:
        total_minutes = immersion_df['minutes'].sum()
        total_hours = total_minutes / 60
        progress_pct = calculate_progress_percentage(total_minutes, 60000)
        
        summary_lines.append("IMMERSION STUDY PROGRESS")
        summary_lines.append("-" * 30)
        summary_lines.append(f"Total Study Time: {format_time(total_minutes)}")
        summary_lines.append(f"Progress towards 1000h goal: {progress_pct:.1f}%")
        summary_lines.append(f"Days studied: {len(immersion_df)}")
        summary_lines.append(f"Average per session: {format_time(immersion_df['minutes'].mean())}")
        summary_lines.append("")
    
    # TOEIC summary
    if not toeic_df.empty:
        summary_lines.append("TOEIC TASK PROGRESS")
        summary_lines.append("-" * 30)
        summary_lines.append(f"Total days tracked: {len(toeic_df)}")
        summary_lines.append(f"Shadowing completion rate: {toeic_df['shadowing'].mean() * 100:.1f}%")
        summary_lines.append(f"Vocabulary completion rate: {toeic_df['vocabulary'].mean() * 100:.1f}%")
        summary_lines.append(f"Reading completion rate: {toeic_df['reading'].mean() * 100:.1f}%")
        summary_lines.append(f"Average tasks per day: {toeic_df['total_completed'].mean():.1f}/3")
        summary_lines.append("")
    
    return "\n".join(summary_lines)
