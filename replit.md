# Study Progress Management System

## Overview

This is a Streamlit-based web application designed to help users track their study progress with both predefined and custom tasks. The system includes immersion hours tracking, TOEIC preparation, and user-configurable custom tasks with flexible units and targets. It provides comprehensive tracking capabilities with visual analytics and progress monitoring.

The application features a multi-tab interface for dashboard overview, study time logging, TOEIC task tracking, custom task management, task configuration, and detailed analytics. It uses CSV files for data persistence and Plotly for interactive visualizations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework for rapid web app development
- **Layout**: Multi-tab interface with wide page layout configuration
- **Components**: 
  - Dashboard tab for progress overview
  - Study time logging interface
  - TOEIC task tracking system
  - Custom task management interface
  - Task configuration and settings
  - Detailed analytics with interactive charts

### Data Management
- **Storage**: CSV file-based data persistence with JSON configuration
- **Data Models**: 
  - Immersion data: date, minutes, notes
  - TOEIC data: date, task completion flags (shadowing, vocabulary, reading), total completed, notes
  - Custom task data: date, value, notes (configurable per task)
  - Task configuration: JSON file storing task definitions with ID, name, unit, target, enabled status
- **Data Processing**: Pandas DataFrame operations for data manipulation and analysis

### Visualization System
- **Charting Library**: Plotly Express and Plotly Graph Objects for interactive visualizations
- **Chart Types**: Progress bars, time series charts, completion tracking
- **Progress Tracking**: Visual representation of 1000-hour goal with percentage completion

### Utility Functions
- **Time Formatting**: Conversion between minutes and human-readable time formats
- **Progress Calculations**: Percentage calculations for goal tracking
- **Date Filtering**: Range-based data filtering with predefined options
- **Streak Calculations**: Study consistency tracking

### Application Structure
- **Modular Design**: Separated concerns across multiple files
  - `app.py`: Main application entry point and UI coordination
  - `data_manager.py`: Data persistence and retrieval operations for immersion and TOEIC data
  - `task_config_manager.py`: Custom task configuration and data management
  - `visualizations.py`: Chart creation and visual components including custom task charts
  - `utils.py`: Helper functions and calculations
- **Error Handling**: Basic exception handling for data operations
- **Data Validation**: Type checking and data integrity maintenance with input validation for custom tasks

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for the user interface
- **pandas**: Data manipulation and analysis operations
- **plotly**: Interactive visualization library (plotly.express and plotly.graph_objects)
- **datetime**: Built-in date and time handling

### Data Storage
- **CSV Files**: Local file system storage for immersion and TOEIC tracking data
- **File Structure**: Two primary data files (immersion_data.csv, toeic_data.csv)

### System Dependencies
- **os**: File system operations for data file management
- **typing**: Type hints for better code documentation and IDE support