"""
Player performance analysis functions for swimming data.

This module provides reusable functions for analyzing individual swimmer performance,
event-specific distributions, and comparative analysis across cohorts.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Optional, List, Tuple


def individual_performance_analysis(
    df: pd.DataFrame,
    full_name: str,
    event_pattern: str,
    title: Optional[str] = None,
    plot: bool = False
) -> pd.DataFrame:
    """
    Analyze an individual swimmer's performance over time for a specific event.
    
    This function creates a visualization showing performance progression over time
    and calculates improvement statistics.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing swimming results with columns:
        - 'Full name': Swimmer's full name
        - 'Event name': Event description
        - 'Date': Competition date
        - 'result_seconds': Time in seconds
    full_name : str
        Full name of the swimmer to analyze
    event_pattern : str
        Pattern to match in event name (e.g., '200m Backstroke')
    title : Optional[str]
        Custom title for the plot. If None, generates default title.
    plot : bool
        Whether to display the performance plot. Default is False.
    
    Returns
    -------
    pd.DataFrame
        Filtered DataFrame containing only the swimmer's results for the specified event,
        sorted by date
    
    Examples
    --------
    >>> swimmer_data = individual_performance_analysis(
    ...     df, 
    ...     'Ayala Saloma', 
    ...     '200m Backstroke'
    ... )
    """
    # Filter data for the specific swimmer and event
    swimmer_data = df[
        (df['Full name'].str.upper() == full_name.upper()) & 
        (df['Event'].str.contains(event_pattern, case=False, na=False))
    ].copy()
    
    # Sort by date
    swimmer_data = swimmer_data.sort_values('Date')
    
    if len(swimmer_data) == 0:
        print(f"No data found for {full_name} in {event_pattern}")
        return swimmer_data
    
    # Calculate improvement statistics
    if len(swimmer_data) >= 2:
        first_time = swimmer_data['result_seconds'].iloc[0]
        best_time = swimmer_data['result_seconds'].min()
        last_time = swimmer_data['result_seconds'].iloc[-1]
        
        improvement_from_first = first_time - best_time
        improvement_pct = (improvement_from_first / first_time) * 100
        
        print(f"\n{full_name} - {event_pattern} Performance Summary:")
        print(f"  Total races: {len(swimmer_data)}")
        print(f"  First recorded time: {first_time:.2f}s")
        print(f"  Best time: {best_time:.2f}s")
        print(f"  Latest time: {last_time:.2f}s")
        print(f"  Improvement from first: {improvement_from_first:.2f}s ({improvement_pct:.1f}%)")
    
    # Create visualization only if plot=True
    if plot:
        if title is None:
            title = f"{full_name} - {event_pattern} Performance Over Time"
        
        plt.figure(figsize=(12, 6))
        plt.plot(swimmer_data['Date'], swimmer_data['result_seconds'], 
                 marker='o', linestyle='-', linewidth=2, markersize=8)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Time (seconds)', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    return swimmer_data


def event_specific_analysis(
    df: pd.DataFrame,
    event_pattern: str,
    categories: Optional[List[str]] = None,
    ylim: Optional[Tuple[float, float]] = None,
    title: Optional[str] = None
) -> pd.DataFrame:
    """
    Analyze event-specific performance distribution across age groups and categories.
    
    This function creates violin plots showing the distribution of times across
    different age groups and categories for a specific event.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing swimming results with columns:
        - 'Event name': Event description
        - 'Category': Age/gender category
        - 'result_seconds': Time in seconds
    event_pattern : str
        Pattern to match in event name (e.g., '400m Freestyle')
    categories : Optional[List[str]]
        List of categories to include in analysis. If None, includes all categories.
    ylim : Optional[Tuple[float, float]]
        Y-axis limits for the plot as (min, max). If None, uses automatic scaling.
    title : Optional[str]
        Custom title for the plot. If None, generates default title.
    
    Returns
    -------
    pd.DataFrame
        Filtered DataFrame containing only results for the specified event and categories
    
    Examples
    --------
    >>> event_data = event_specific_analysis(
    ...     df,
    ...     '400m Freestyle',
    ...     categories=['Boys 15-16', 'Boys 17-18'],
    ...     ylim=(220, 320)
    ... )
    """
    # Filter data for the specific event
    event_data = df[
        df['Event'].str.contains(event_pattern, case=False, na=False)
    ].copy()
    
    # Filter by categories if specified
    if categories is not None:
        event_data = event_data[event_data['Category'].isin(categories)]
    
    if len(event_data) == 0:
        print(f"No data found for {event_pattern}")
        return event_data
    
    # Print summary statistics
    print(f"\n{event_pattern} Distribution Summary:")
    print(f"  Total results: {len(event_data)}")
    print(f"  Categories: {sorted(event_data['Category'].unique())}")
    print(f"\nStatistics by Category:")
    print(event_data.groupby('Category')['result_seconds'].agg([
        ('count', 'count'),
        ('mean', lambda x: f"{x.mean():.2f}"),
        ('median', lambda x: f"{x.median():.2f}"),
        ('min', lambda x: f"{x.min():.2f}"),
        ('max', lambda x: f"{x.max():.2f}")
    ]))
    
    # Create visualization
    if title is None:
        title = f"{event_pattern} - Distribution by Age Group"
    
    plt.figure(figsize=(14, 8))
    sns.violinplot(data=event_data, x='Category', y='result_seconds', 
                   palette='Set2', inner='box')
    plt.xlabel('Category', fontsize=12)
    plt.ylabel('Time (seconds)', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    
    if ylim is not None:
        plt.ylim(ylim)
    
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.show()
    
    return event_data


def comparative_analysis(
    df: pd.DataFrame,
    full_name: str,
    event_pattern: str,
    gender: str,
    xlim: Optional[Tuple[float, float]] = None,
    title: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compare an individual swimmer's performance against their cohort.
    
    This function analyzes how a swimmer's best time compares to other swimmers
    in the same gender category for a specific event. It uses only the best time
    for each swimmer to avoid bias from multiple entries.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing swimming results with columns:
        - 'Full name': Swimmer's full name
        - 'Event name': Event description
        - 'Category': Age/gender category
        - 'result_seconds': Time in seconds
    full_name : str
        Full name of the swimmer to analyze
    event_pattern : str
        Pattern to match in event name (e.g., '200m Backstroke')
    gender : str
        Gender to filter by ('Boys' or 'Girls')
    xlim : Optional[Tuple[float, float]]
        X-axis limits for the plot as (min, max). If None, uses automatic scaling.
    title : Optional[str]
        Custom title for the plot. If None, generates default title.
    
    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        - cohort_data: DataFrame with best times for all swimmers in the cohort
        - swimmer_data: DataFrame with the target swimmer's best time
    
    Examples
    --------
    >>> cohort, swimmer = comparative_analysis(
    ...     df,
    ...     'Amit Gur',
    ...     '400m Freestyle',
    ...     'Boys',
    ...     xlim=(220, 320)
    ... )
    """
    # Get the swimmer's birth year first
    swimmer_birth_year_data = df[df['Full name'].str.upper() == full_name.upper()]
    
    if len(swimmer_birth_year_data) == 0:
        print(f"No data found for {full_name}")
        return pd.DataFrame(), pd.DataFrame()
    
    swimmer_birth_year = swimmer_birth_year_data['Year Of Birth'].iloc[0]
    
    # Filter for the specific event, gender, and birth year
    event_data = df[
        (df['Year Of Birth'] == swimmer_birth_year) &
        (df['Event'].str.contains(event_pattern, case=False, na=False)) &
        (df['Category'].str.contains(gender, case=False, na=False))
    ].copy()
    
    if len(event_data) == 0:
        print(f"No data found for {event_pattern} in {gender} categories for birth year {swimmer_birth_year}")
        return pd.DataFrame(), pd.DataFrame()
    
    # Get best time for each swimmer (groupby optimization)
    cohort_data = event_data.groupby('Full name', as_index=False)['result_seconds'].min()
    
    # Get the swimmer's best time
    swimmer_data = cohort_data[cohort_data['Full name'].str.upper() == full_name.upper()]
    
    if len(swimmer_data) == 0:
        print(f"No data found for {full_name} in {event_pattern} ({gender})")
        return cohort_data, swimmer_data
    
    swimmer_time = swimmer_data['result_seconds'].iloc[0]
    
    # Calculate statistics
    cohort_times = cohort_data['result_seconds']
    percentile = stats.percentileofscore(cohort_times, swimmer_time, kind='rank')
    
    faster_count = (cohort_times < swimmer_time).sum()
    slower_count = (cohort_times > swimmer_time).sum()
    
    mean_time = cohort_times.mean()
    median_time = cohort_times.median()
    std_time = cohort_times.std()
    
    # Print analysis
    print(f"\n{full_name} - {event_pattern} ({gender}) Comparative Analysis:")
    print(f"  Birth year: {int(swimmer_birth_year)}")
    print(f"  Swimmer's best time: {swimmer_time:.2f}s")
    print(f"  Cohort size: {len(cohort_data)} swimmers (same birth year)")
    print(f"  Cohort mean: {mean_time:.2f}s")
    print(f"  Cohort median: {median_time:.2f}s")
    print(f"  Cohort std dev: {std_time:.2f}s")
    print(f"  Percentile rank: {percentile:.1f}%")
    print(f"  Faster swimmers: {faster_count}")
    print(f"  Slower swimmers: {slower_count}")
    
    if swimmer_time < mean_time:
        diff = mean_time - swimmer_time
        print(f"  Performance: {diff:.2f}s faster than average")
    else:
        diff = swimmer_time - mean_time
        print(f"  Performance: {diff:.2f}s slower than average")
    
    # Create visualization
    if title is None:
        title = f"{full_name} vs Cohort - {event_pattern} ({gender}) - Birth Year {int(swimmer_birth_year)}"
    
    plt.figure(figsize=(14, 8))
    
    # Density plot for cohort
    plt.subplot(2, 1, 1)
    cohort_times.plot(kind='density', linewidth=2, label='Cohort Distribution (Same Birth Year)')
    plt.axvline(swimmer_time, color='red', linestyle='--', linewidth=2, 
                label=f'{full_name}: {swimmer_time:.2f}s')
    plt.axvline(mean_time, color='green', linestyle='--', linewidth=1.5, 
                alpha=0.7, label=f'Mean: {mean_time:.2f}s')
    plt.axvline(median_time, color='orange', linestyle='--', linewidth=1.5, 
                alpha=0.7, label=f'Median: {median_time:.2f}s')
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.title(f'{title}\nPercentile: {percentile:.1f}%', 
              fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if xlim is not None:
        plt.xlim(xlim)
    
    # Histogram with KDE
    plt.subplot(2, 1, 2)
    plt.hist(cohort_times, bins=30, alpha=0.6, color='skyblue', 
             edgecolor='black', density=True, label='Histogram')
    cohort_times.plot(kind='density', linewidth=2, color='blue', 
                      label='KDE', ax=plt.gca())
    plt.axvline(swimmer_time, color='red', linestyle='--', linewidth=2, 
                label=f'{full_name}')
    plt.xlabel('Time (seconds)', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.title(f'Distribution of Best Times ({len(cohort_data)} swimmers)', 
              fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if xlim is not None:
        plt.xlim(xlim)
    
    plt.tight_layout()
    plt.show()
    
    return cohort_data, swimmer_data
