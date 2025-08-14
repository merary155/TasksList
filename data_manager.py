import pandas as pd
import os
from datetime import datetime, date
from typing import Optional

class DataManager:
    """Handles all data operations for the study progress system"""
    
    def __init__(self):
        self.immersion_file = "immersion_data.csv"
        self.toeic_file = "toeic_data.csv"
        self._ensure_data_files()
    
    def _ensure_data_files(self):
        """Create data files if they don't exist"""
        # Create immersion data file
        if not os.path.exists(self.immersion_file):
            immersion_df = pd.DataFrame(columns=['date', 'minutes', 'notes'])
            immersion_df.to_csv(self.immersion_file, index=False)
        
        # Create TOEIC data file
        if not os.path.exists(self.toeic_file):
            toeic_df = pd.DataFrame(columns=[
                'date', 'shadowing', 'vocabulary', 'reading', 'total_completed', 'notes'
            ])
            toeic_df.to_csv(self.toeic_file, index=False)
    
    def load_immersion_data(self) -> pd.DataFrame:
        """Load immersion study data from CSV"""
        try:
            df = pd.read_csv(self.immersion_file)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date']).dt.date
                df = df.sort_values('date')
            return df
        except Exception as e:
            print(f"Error loading immersion data: {e}")
            return pd.DataFrame(columns=['date', 'minutes', 'notes'])
    
    def load_toeic_data(self) -> pd.DataFrame:
        """Load TOEIC task data from CSV"""
        try:
            df = pd.read_csv(self.toeic_file)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date']).dt.date
                df = df.sort_values('date')
                # Ensure boolean columns are properly typed
                for col in ['shadowing', 'vocabulary', 'reading']:
                    df[col] = df[col].astype(bool)
            return df
        except Exception as e:
            print(f"Error loading TOEIC data: {e}")
            return pd.DataFrame(columns=[
                'date', 'shadowing', 'vocabulary', 'reading', 'total_completed', 'notes'
            ])
    
    def add_immersion_entry(self, study_date: date, minutes: int, notes: str = "") -> bool:
        """Add or update an immersion study entry"""
        try:
            df = self.load_immersion_data()
            
            # Check if entry for this date already exists
            existing_mask = df['date'] == study_date
            
            if existing_mask.any():
                # Update existing entry
                df.loc[existing_mask, 'minutes'] = minutes
                df.loc[existing_mask, 'notes'] = str(notes)
            else:
                # Add new entry
                new_entry = pd.DataFrame({
                    'date': [study_date],
                    'minutes': [minutes],
                    'notes': [notes]
                })
                df = pd.concat([df, new_entry], ignore_index=True)
            
            # Sort by date and save
            df = df.sort_values('date')
            df.to_csv(self.immersion_file, index=False)
            return True
            
        except Exception as e:
            print(f"Error adding immersion entry: {e}")
            return False
    
    def add_toeic_entry(self, task_date: date, shadowing: bool, vocabulary: bool, 
                       reading: bool, notes: str = "") -> bool:
        """Add or update a TOEIC task entry"""
        try:
            df = self.load_toeic_data()
            
            # Calculate total completed tasks
            total_completed = sum([shadowing, vocabulary, reading])
            
            # Check if entry for this date already exists
            existing_mask = df['date'] == task_date
            
            if existing_mask.any():
                # Update existing entry
                df.loc[existing_mask, 'shadowing'] = shadowing
                df.loc[existing_mask, 'vocabulary'] = vocabulary
                df.loc[existing_mask, 'reading'] = reading
                df.loc[existing_mask, 'total_completed'] = total_completed
                df.loc[existing_mask, 'notes'] = notes
            else:
                # Add new entry
                new_entry = pd.DataFrame({
                    'date': [task_date],
                    'shadowing': [shadowing],
                    'vocabulary': [vocabulary],
                    'reading': [reading],
                    'total_completed': [total_completed],
                    'notes': [notes]
                })
                df = pd.concat([df, new_entry], ignore_index=True)
            
            # Sort by date and save
            df = df.sort_values('date')
            df.to_csv(self.toeic_file, index=False)
            return True
            
        except Exception as e:
            print(f"Error adding TOEIC entry: {e}")
            return False
    
    def get_immersion_summary(self) -> dict:
        """Get summary statistics for immersion study"""
        df = self.load_immersion_data()
        
        if df.empty:
            return {
                'total_minutes': 0,
                'total_hours': 0,
                'days_studied': 0,
                'average_daily': 0,
                'progress_percentage': 0
            }
        
        total_minutes = df['minutes'].sum()
        total_hours = total_minutes / 60
        days_studied = len(df)
        average_daily = df['minutes'].mean()
        progress_percentage = (total_minutes / 60000) * 100  # Goal is 60,000 minutes
        
        return {
            'total_minutes': total_minutes,
            'total_hours': total_hours,
            'days_studied': days_studied,
            'average_daily': average_daily,
            'progress_percentage': progress_percentage
        }
    
    def get_toeic_summary(self) -> dict:
        """Get summary statistics for TOEIC tasks"""
        df = self.load_toeic_data()
        
        if df.empty:
            return {
                'total_days': 0,
                'shadowing_completion_rate': 0,
                'vocabulary_completion_rate': 0,
                'reading_completion_rate': 0,
                'average_tasks_per_day': 0
            }
        
        total_days = len(df)
        shadowing_rate = df['shadowing'].mean() * 100
        vocabulary_rate = df['vocabulary'].mean() * 100
        reading_rate = df['reading'].mean() * 100
        avg_tasks = df['total_completed'].mean()
        
        return {
            'total_days': total_days,
            'shadowing_completion_rate': shadowing_rate,
            'vocabulary_completion_rate': vocabulary_rate,
            'reading_completion_rate': reading_rate,
            'average_tasks_per_day': avg_tasks
        }
    
    def delete_immersion_entry(self, study_date: date) -> bool:
        """Delete an immersion entry for a specific date"""
        try:
            df = self.load_immersion_data()
            df = df[df['date'] != study_date]
            df.to_csv(self.immersion_file, index=False)
            return True
        except Exception as e:
            print(f"Error deleting immersion entry: {e}")
            return False
    
    def delete_toeic_entry(self, task_date: date) -> bool:
        """Delete a TOEIC entry for a specific date"""
        try:
            df = self.load_toeic_data()
            df = df[df['date'] != task_date]
            df.to_csv(self.toeic_file, index=False)
            return True
        except Exception as e:
            print(f"Error deleting TOEIC entry: {e}")
            return False
