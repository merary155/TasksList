import json
import os
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional

class TaskConfigManager:
    """Manages custom task configurations and their data"""
    
    def __init__(self):
        self.config_file = "task_config.json"
        self.data_dir = "custom_task_data"
        self._ensure_config_file()
        self._ensure_data_directory()
    
    def _ensure_config_file(self):
        """Create config file if it doesn't exist"""
        if not os.path.exists(self.config_file):
            default_config = {
                "tasks": [
                    {
                        "id": "immersion",
                        "name": "イマージョン学習",
                        "unit": "分",
                        "target": 60000,
                        "enabled": True,
                        "created_date": datetime.now().isoformat()
                    },
                    {
                        "id": "toeic_shadowing",
                        "name": "シャドーイング練習",
                        "unit": "回",
                        "target": 365,
                        "enabled": True,
                        "created_date": datetime.now().isoformat()
                    },
                    {
                        "id": "toeic_vocabulary",
                        "name": "単語テスト",
                        "unit": "問",
                        "target": 73000,
                        "enabled": True,
                        "created_date": datetime.now().isoformat()
                    },
                    {
                        "id": "toeic_reading",
                        "name": "長文読解",
                        "unit": "題",
                        "target": 1095,
                        "enabled": True,
                        "created_date": datetime.now().isoformat()
                    }
                ]
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_config(self) -> Dict:
        """Load task configuration from file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"tasks": []}
    
    def save_config(self, config: Dict) -> bool:
        """Save task configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_all_tasks(self) -> List[Dict]:
        """Get all configured tasks"""
        config = self.load_config()
        return config.get("tasks", [])
    
    def get_enabled_tasks(self) -> List[Dict]:
        """Get only enabled tasks"""
        tasks = self.get_all_tasks()
        return [task for task in tasks if task.get("enabled", True)]
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID"""
        tasks = self.get_all_tasks()
        for task in tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def add_task(self, name: str, unit: str, target: int) -> bool:
        """Add a new task"""
        try:
            config = self.load_config()
            
            # Generate unique ID
            task_id = name.lower().replace(" ", "_").replace("　", "_")
            existing_ids = [task["id"] for task in config["tasks"]]
            
            counter = 1
            original_id = task_id
            while task_id in existing_ids:
                task_id = f"{original_id}_{counter}"
                counter += 1
            
            new_task = {
                "id": task_id,
                "name": name,
                "unit": unit,
                "target": target,
                "enabled": True,
                "created_date": datetime.now().isoformat()
            }
            
            config["tasks"].append(new_task)
            
            # Create data file for new task
            self._create_task_data_file(task_id)
            
            return self.save_config(config)
        except Exception as e:
            print(f"Error adding task: {e}")
            return False
    
    def update_task(self, task_id: str, name: str = None, unit: str = None, 
                   target: int = None, enabled: bool = None) -> bool:
        """Update an existing task"""
        try:
            config = self.load_config()
            
            for task in config["tasks"]:
                if task["id"] == task_id:
                    if name is not None:
                        task["name"] = name
                    if unit is not None:
                        task["unit"] = unit
                    if target is not None:
                        task["target"] = target
                    if enabled is not None:
                        task["enabled"] = enabled
                    task["updated_date"] = datetime.now().isoformat()
                    break
            
            return self.save_config(config)
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            config = self.load_config()
            config["tasks"] = [task for task in config["tasks"] if task["id"] != task_id]
            
            # Delete associated data file
            data_file = os.path.join(self.data_dir, f"{task_id}_data.csv")
            if os.path.exists(data_file):
                os.remove(data_file)
            
            return self.save_config(config)
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    def _create_task_data_file(self, task_id: str):
        """Create empty data file for a task"""
        data_file = os.path.join(self.data_dir, f"{task_id}_data.csv")
        if not os.path.exists(data_file):
            df = pd.DataFrame(columns=['date', 'value', 'notes'])
            df.to_csv(data_file, index=False)
    
    def load_task_data(self, task_id: str) -> pd.DataFrame:
        """Load data for a specific task"""
        data_file = os.path.join(self.data_dir, f"{task_id}_data.csv")
        
        if not os.path.exists(data_file):
            self._create_task_data_file(task_id)
        
        try:
            df = pd.read_csv(data_file)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date']).dt.date
                df = df.sort_values('date')
            return df
        except Exception as e:
            print(f"Error loading task data for {task_id}: {e}")
            return pd.DataFrame(columns=['date', 'value', 'notes'])
    
    def save_task_data(self, task_id: str, df: pd.DataFrame) -> bool:
        """Save data for a specific task"""
        try:
            data_file = os.path.join(self.data_dir, f"{task_id}_data.csv")
            df.to_csv(data_file, index=False)
            return True
        except Exception as e:
            print(f"Error saving task data for {task_id}: {e}")
            return False
    
    def add_task_entry(self, task_id: str, entry_date: date, value: float, notes: str = "") -> bool:
        """Add or update an entry for a task"""
        try:
            df = self.load_task_data(task_id)
            
            # Check if entry for this date already exists
            existing_mask = df['date'] == entry_date
            
            if existing_mask.any():
                # Update existing entry
                df.loc[existing_mask, 'value'] = value
                df.loc[existing_mask, 'notes'] = notes
            else:
                # Add new entry
                new_entry = pd.DataFrame({
                    'date': [entry_date],
                    'value': [value],
                    'notes': [notes]
                })
                df = pd.concat([df, new_entry], ignore_index=True)
            
            # Sort by date and save
            df = df.sort_values('date')
            return self.save_task_data(task_id, df)
        except Exception as e:
            print(f"Error adding task entry: {e}")
            return False
    
    def get_task_summary(self, task_id: str) -> Dict:
        """Get summary statistics for a task"""
        task = self.get_task_by_id(task_id)
        if not task:
            return {}
        
        df = self.load_task_data(task_id)
        
        if df.empty:
            return {
                'task_name': task['name'],
                'unit': task['unit'],
                'target': task['target'],
                'total_value': 0,
                'days_logged': 0,
                'progress_percentage': 0,
                'average_daily': 0
            }
        
        total_value = df['value'].sum()
        days_logged = len(df)
        progress_percentage = (total_value / task['target']) * 100 if task['target'] > 0 else 0
        average_daily = df['value'].mean()
        
        return {
            'task_name': task['name'],
            'unit': task['unit'],
            'target': task['target'],
            'total_value': total_value,
            'days_logged': days_logged,
            'progress_percentage': progress_percentage,
            'average_daily': average_daily
        }
    
    def get_available_units(self) -> List[str]:
        """Get list of available units"""
        return ["分", "時間", "回", "問", "題", "ページ", "章", "個", "本", "日"]
    
    def validate_task_input(self, name: str, unit: str, target: int) -> tuple[bool, str]:
        """Validate task input"""
        if not name or len(name.strip()) == 0:
            return False, "タスク名を入力してください"
        
        if len(name.strip()) > 50:
            return False, "タスク名は50文字以内で入力してください"
        
        if not unit or unit not in self.get_available_units():
            return False, "有効な単位を選択してください"
        
        if target <= 0:
            return False, "目標値は1以上の数値を入力してください"
        
        if target > 1000000:
            return False, "目標値は1,000,000以下で入力してください"
        
        return True, "有効な入力です"