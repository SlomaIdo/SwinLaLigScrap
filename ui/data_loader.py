"""
Data loading utilities for the swimming dashboard.

This module handles all data loading operations from the SQLite database,
including caching and data preprocessing.
"""

import pandas as pd
import sqlite3
from pathlib import Path
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Handle data loading from the swimming database.
    
    This class provides methods to load and cache swimming data from the SQLite database,
    as well as utility methods to extract unique swimmers, events, and categories.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the DataLoader.
        
        Parameters
        ----------
        db_path : Optional[str]
            Path to the SQLite database file. If None, uses default path.
        """
        if db_path is None:
            # Get the parent directory of the ui folder
            parent_dir = Path(__file__).parent.parent
            db_path = parent_dir / "swim_database_2.sqlite3"
        
        self.db_path = str(db_path)
        self._data_cache = None
        self._last_load_time = None
        
        logger.info(f"DataLoader initialized with database: {self.db_path}")
    
    def load_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load swimming results data from the database.
        
        This method loads data from the discipline_results_ingest table and performs
        basic preprocessing including date parsing and data type conversions.
        
        Parameters
        ----------
        force_reload : bool
            If True, reload data from database even if cached data exists.
            Default is False.
        
        Returns
        -------
        pd.DataFrame
            DataFrame containing swimming results with processed columns
        
        Raises
        ------
        FileNotFoundError
            If the database file doesn't exist
        sqlite3.Error
            If there's an error connecting to or querying the database
        """
        if not force_reload and self._data_cache is not None:
            logger.info("Returning cached data")
            return self._data_cache.copy()
        
        logger.info(f"Loading data from {self.db_path}")
        
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            # Load all columns from discipline_results_ingest table
            # Note: Club column has whitespace in its name in the database
            query = """
                SELECT *
                FROM discipline_results_ingest
                WHERE "Full name" IS NOT NULL
                AND "Results" IS NOT NULL
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"Loaded {len(df)} records from database")
            
            # Rename the Club column if it has whitespace in the name
            club_cols = [col for col in df.columns if 'Club' in col and col != 'Club']
            if club_cols:
                df = df.rename(columns={club_cols[0]: 'Club'})
                logger.info(f"Renamed column '{club_cols[0]}' to 'Club'")
            
            # Preprocess data
            df = self._preprocess_data(df)
            
            # Cache the data
            self._data_cache = df.copy()
            
            logger.info("Data preprocessing completed")
            return df
        
        except FileNotFoundError:
            logger.error(f"Database file not found: {self.db_path}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}")
            raise
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the raw data from the database.
        
        Parameters
        ----------
        df : pd.DataFrame
            Raw DataFrame from database
        
        Returns
        -------
        pd.DataFrame
            Preprocessed DataFrame with additional computed columns
        """
        # Convert Results to seconds
        df['result_seconds'] = df['Results'].apply(self._convert_time_to_seconds)
        
        # Parse dates
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Convert Year Of Birth to numeric
        if 'Year Of Birth' in df.columns:
            df['Year Of Birth'] = pd.to_numeric(df['Year Of Birth'], errors='coerce')
        
        # Convert Place to numeric
        if 'Place' in df.columns:
            df['Place'] = pd.to_numeric(df['Place'], errors='coerce')
        
        # Remove rows with invalid result_seconds
        df = df[df['result_seconds'].notna()]
        df = df[df['result_seconds'] > 0]
        
        # Sort by date
        if 'Date' in df.columns:
            df = df.sort_values('Date')
        
        return df
    
    @staticmethod
    def _convert_time_to_seconds(time_str: str) -> Optional[float]:
        """
        Convert swimming time string to seconds.
        
        Handles formats like:
        - "1:23.45" (minutes:seconds.centiseconds)
        - "23.45" (seconds.centiseconds)
        - "1:23:45.00" (hours:minutes:seconds.centiseconds)
        
        Parameters
        ----------
        time_str : str
            Time string to convert
        
        Returns
        -------
        Optional[float]
            Time in seconds, or None if conversion fails
        """
        if pd.isna(time_str) or not isinstance(time_str, str):
            return None
        
        try:
            # Remove any whitespace
            time_str = time_str.strip()
            
            # Split by colon
            parts = time_str.split(':')
            
            if len(parts) == 1:
                # Format: SS.CC or S.CC
                return float(parts[0])
            elif len(parts) == 2:
                # Format: MM:SS.CC
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            elif len(parts) == 3:
                # Format: HH:MM:SS.CC
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            else:
                return None
        except (ValueError, AttributeError):
            return None
    
    def get_swimmers(self) -> List[str]:
        """
        Get a sorted list of unique swimmer names.
        
        Returns
        -------
        List[str]
            Sorted list of swimmer names
        """
        if self._data_cache is None:
            self.load_data()
        
        swimmers = sorted(self._data_cache['Full name'].dropna().unique())
        logger.info(f"Found {len(swimmers)} unique swimmers")
        return swimmers
    
    def get_events(self) -> List[str]:
        """
        Get a sorted list of unique event names.
        
        Returns
        -------
        List[str]
            Sorted list of event names
        """
        if self._data_cache is None:
            self.load_data()
        
        events = sorted(self._data_cache['Event'].dropna().unique())
        logger.info(f"Found {len(events)} unique events")
        return events
    
    def get_categories(self) -> List[str]:
        """
        Get a sorted list of unique categories.
        
        Returns
        -------
        List[str]
            Sorted list of category names
        """
        if self._data_cache is None:
            self.load_data()
        
        categories = sorted(self._data_cache['Category'].dropna().unique())
        logger.info(f"Found {len(categories)} unique categories")
        return categories
    
    def get_clubs(self) -> List[str]:
        """
        Get a sorted list of unique club names.
        
        Returns
        -------
        List[str]
            Sorted list of club names
        """
        if self._data_cache is None:
            self.load_data()
        
        clubs = sorted(self._data_cache['Club'].dropna().unique())
        logger.info(f"Found {len(clubs)} unique clubs")
        return clubs
    
    def get_swimmer_info(self, swimmer_name: str) -> pd.DataFrame:
        """
        Get all information for a specific swimmer.
        
        Parameters
        ----------
        swimmer_name : str
            Name of the swimmer
        
        Returns
        -------
        pd.DataFrame
            DataFrame containing all records for the specified swimmer
        """
        if self._data_cache is None:
            self.load_data()
        
        return self._data_cache[
            self._data_cache['Full name'].str.upper() == swimmer_name.upper()
        ].copy()
    
    def get_event_data(self, event_pattern: str) -> pd.DataFrame:
        """
        Get all data for a specific event.
        
        Parameters
        ----------
        event_pattern : str
            Pattern to match event names (case-insensitive)
        
        Returns
        -------
        pd.DataFrame
            DataFrame containing all records for events matching the pattern
        """
        if self._data_cache is None:
            self.load_data()
        
        return self._data_cache[
            self._data_cache['Event'].str.contains(event_pattern, case=False, na=False)
        ].copy()
    
    def clear_cache(self):
        """Clear the cached data to force a reload on next access."""
        self._data_cache = None
        logger.info("Data cache cleared")
