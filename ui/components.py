"""
Visualization components for the swimming dashboard.

This module provides reusable chart creation functions for different
types of swimming performance visualizations.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Optional, Tuple


def create_swimmer_dropdown(swimmers: List[str]) -> List[dict]:
    """
    Create dropdown options for swimmer selection.
    
    Parameters
    ----------
    swimmers : List[str]
        List of swimmer names
    
    Returns
    -------
    List[dict]
        List of dropdown option dictionaries
    """
    return [{"label": name, "value": name} for name in swimmers]


def create_event_dropdown(events: List[str]) -> List[dict]:
    """
    Create dropdown options for event selection.
    
    Parameters
    ----------
    events : List[str]
        List of event names
    
    Returns
    -------
    List[dict]
        List of dropdown option dictionaries
    """
    return [{"label": event, "value": event} for event in events]


def create_category_dropdown(categories: List[str]) -> List[dict]:
    """
    Create dropdown options for category selection.
    
    Parameters
    ----------
    categories : List[str]
        List of category names
    
    Returns
    -------
    List[dict]
        List of dropdown option dictionaries
    """
    return [{"label": cat, "value": cat} for cat in categories]


def create_performance_chart(
    swimmer_data: pd.DataFrame,
    swimmer_name: str,
    event_pattern: str
) -> go.Figure:
    """
    Create an interactive performance chart showing progression over time.
    
    Parameters
    ----------
    swimmer_data : pd.DataFrame
        DataFrame containing swimmer's results
    swimmer_name : str
        Name of the swimmer
    event_pattern : str
        Event pattern being analyzed
    
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    # Sort by date and create a copy
    swimmer_data = swimmer_data.sort_values('Date').copy()
    
    # Calculate improvements
    swimmer_data['prev_time'] = swimmer_data['result_seconds'].shift(1)
    swimmer_data['improvement_from_prev'] = swimmer_data['prev_time'] - swimmer_data['result_seconds']
    swimmer_data['improvement_pct_from_prev'] = (swimmer_data['improvement_from_prev'] / swimmer_data['prev_time']) * 100
    
    # Calculate year-to-year improvement
    swimmer_data['year'] = swimmer_data['Date'].dt.year
    yearly_best = swimmer_data.groupby('year')['result_seconds'].min().reset_index()
    yearly_best['prev_year_best'] = yearly_best['result_seconds'].shift(1)
    yearly_best['ytoy_improvement_pct'] = ((yearly_best['prev_year_best'] - yearly_best['result_seconds']) / yearly_best['prev_year_best']) * 100
    
    # Merge year-to-year data back
    swimmer_data = swimmer_data.merge(yearly_best[['year', 'ytoy_improvement_pct']], on='year', how='left')
    
    # Calculate best time and trend
    best_time = swimmer_data['result_seconds'].min()
    best_idx = swimmer_data['result_seconds'].idxmin()
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add main performance line
    fig.add_trace(go.Scatter(
        x=swimmer_data['Date'],
        y=swimmer_data['result_seconds'],
        mode='lines+markers',
        name='Performance Time',
        line=dict(color='#4f46e5', width=3),  # primary color
        marker=dict(size=10, color='#4f46e5'),
        yaxis='y',
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                      '<b>Time:</b> %{y:.2f}s<br>' +
                      '<extra></extra>'
    ))
    
    # Add best time marker
    fig.add_trace(go.Scatter(
        x=[swimmer_data.loc[best_idx, 'Date']],
        y=[best_time],
        mode='markers',
        name='Best Time',
        marker=dict(size=15, color='#fbbf24', symbol='star', line=dict(color='#f59e0b', width=2)),  # secondary/chart-4
        yaxis='y',
        hovertemplate='<b>Best Time</b><br>' +
                      '<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                      '<b>Time:</b> %{y:.2f}s<br>' +
                      '<extra></extra>'
    ))
    
    # Add improvement from previous measurement (on secondary axis)
    fig.add_trace(go.Scatter(
        x=swimmer_data['Date'],
        y=swimmer_data['improvement_from_prev'],
        mode='lines+markers',
        name='Improvement from Previous',
        line=dict(color='#10b981', width=2, dash='dot'),  # chart-3 (green)
        marker=dict(size=6, color='#10b981'),
        yaxis='y2',
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                      '<b>Improvement:</b> %{y:.2f}s<br>' +
                      '<extra></extra>'
    ))
    
    # Add year-to-year percentage improvement (on secondary axis)
    # Filter out NaN values for cleaner display
    ytoy_data = swimmer_data[swimmer_data['ytoy_improvement_pct'].notna()].copy()
    if len(ytoy_data) > 0:
        fig.add_trace(go.Scatter(
            x=ytoy_data['Date'],
            y=ytoy_data['ytoy_improvement_pct'],
            mode='lines+markers',
            name='Year-to-Year Improvement %',
            line=dict(color='#ec4899', width=2, dash='dashdot'),  # chart-5 (pink)
            marker=dict(size=8, color='#ec4899', symbol='diamond'),
            yaxis='y2',
            hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br>' +
                          '<b>YoY Improvement:</b> %{y:.2f}%<br>' +
                          '<extra></extra>'
        ))
    
    # Add trend line if enough data points
    if len(swimmer_data) >= 3:
        # Convert dates to numeric for regression
        swimmer_data['date_numeric'] = (swimmer_data['Date'] - swimmer_data['Date'].min()).dt.days
        
        # Calculate linear regression
        z = np.polyfit(swimmer_data['date_numeric'], swimmer_data['result_seconds'], 1)
        p = np.poly1d(z)
        
        fig.add_trace(go.Scatter(
            x=swimmer_data['Date'],
            y=p(swimmer_data['date_numeric']),
            mode='lines',
            name='Trend Line',
            line=dict(color='#ef4444', width=2, dash='dash'),  # destructive color
            yaxis='y',
            hovertemplate='<b>Trend Line</b><br>' +
                          '<b>Time:</b> %{y:.2f}s<br>' +
                          '<extra></extra>'
        ))
    
    # Update layout with dual y-axes
    fig.update_layout(
        title=dict(
            text=f"{swimmer_name} - {event_pattern} Performance Over Time",
            font=dict(size=18, family='Arial, sans-serif'),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="Date",
        hovermode='x unified',
        template='plotly_white',
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(79, 70, 229, 0.2)',
            borderwidth=1
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(79, 70, 229, 0.1)'
        ),
        yaxis=dict(
            title="Time (seconds)",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(79, 70, 229, 0.1)',
            autorange='reversed',  # Lower times are better
            side='left'
        ),
        yaxis2=dict(
            title="Improvement (seconds / %)",
            overlaying='y',
            side='right',
            showgrid=False,
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='rgba(0, 0, 0, 0.3)'
        )
    )
    
    return fig


def create_distribution_chart(
    event_data: pd.DataFrame,
    event_pattern: str
) -> go.Figure:
    """
    Create a violin plot showing event distribution by swimmer age.
    
    Parameters
    ----------
    event_data : pd.DataFrame
        DataFrame containing event results with 'Age' and 'Age_Binned' columns
    event_pattern : str
        Event pattern being analyzed
    
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    # Sort by age for proper ordering (smallest on left), with 18+ at the end
    event_data_sorted = event_data.copy()
    event_data_sorted['sort_key'] = event_data_sorted['Age_Binned'].apply(lambda x: 999 if x == '18+' else int(x))
    event_data_sorted = event_data_sorted.sort_values('sort_key')
    
    # Create violin plot using plotly express (without individual points)
    fig = px.violin(
        event_data_sorted,
        x='Age_Binned',
        y='result_seconds',
        box=True,
        points=False,
        color='Age_Binned',
        hover_data=['Full name', 'Date', 'Club', 'Category', 'Year Of Birth'],
        title=f"{event_pattern} - Distribution by Age"
    )
    
    # Update violin traces to not stretch for outliers
    fig.update_traces(
        spanmode='soft',  # Don't stretch to outliers
        scalemode='width'
    )
    
    # Update layout
    # Create custom category order with 18+ at the end
    unique_ages = event_data_sorted['Age_Binned'].unique()
    age_order = sorted([age for age in unique_ages if age != '18+'], key=lambda x: int(x))
    if '18+' in unique_ages:
        age_order.append('18+')
    
    # Determine y-axis range based on event distance (reversed so lower times are at top)
    y_range = None
    if '100' in event_pattern:
        y_range = [200, 30]
    elif '200' in event_pattern:
        y_range = [300, 100]
    elif '400' in event_pattern:
        y_range = [500, 250]
    
    fig.update_layout(
        title=dict(
            font=dict(size=18, color='#333', family='Arial, sans-serif'),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="Age (years)",
        yaxis_title="Time (seconds)",
        hovermode='closest',
        template='plotly_white',
        height=600,
        showlegend=False,
        xaxis=dict(
            type='category',
            categoryorder='array',
            categoryarray=age_order
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            autorange='reversed' if y_range is None else True,  # Lower times are better (at top)
            range=y_range if y_range else None
        )
    )
    
    return fig


def create_comparison_chart(
    cohort_data: pd.DataFrame,
    swimmer_name: str,
    swimmer_time: float,
    event_pattern: str,
    gender_label: str,
    birth_year: int,
    chart_type: str = "density"
) -> go.Figure:
    """
    Create comparison charts (density or histogram) for cohort analysis.
    
    Parameters
    ----------
    cohort_data : pd.DataFrame
        DataFrame with best times for all swimmers in cohort
    swimmer_name : str
        Name of the swimmer being analyzed
    swimmer_time : float
        Swimmer's best time
    event_pattern : str
        Event pattern being analyzed
    gender_label : str
        Gender category label
    birth_year : int
        Birth year of the cohort
    chart_type : str
        Type of chart: "density" or "histogram"
    
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    cohort_times = cohort_data['result_seconds']
    mean_time = cohort_times.mean()
    median_time = cohort_times.median()
    
    fig = go.Figure()
    
    if chart_type == "density":
        # Create KDE density plot
        from scipy.stats import gaussian_kde
        
        # Create density estimation
        density = gaussian_kde(cohort_times)
        xs = np.linspace(cohort_times.min(), cohort_times.max(), 200)
        ys = density(xs)
        
        # Add density plot
        fig.add_trace(go.Scatter(
            x=xs,
            y=ys,
            mode='lines',
            name='Cohort Distribution',
            fill='tozeroy',
            line=dict(color='#06b6d4', width=2),  # accent color
            hovertemplate='<b>Time:</b> %{x:.2f}s<br>' +
                          '<b>Density:</b> %{y:.4f}<br>' +
                          '<extra></extra>'
        ))
        
        # Add vertical lines for swimmer, mean, and median
        fig.add_vline(
            x=swimmer_time,
            line_dash="dash",
            line_color="#ef4444",  # destructive
            line_width=3,
            annotation_text=f"{swimmer_name}: {swimmer_time:.2f}s",
            annotation_position="top"
        )
        
        fig.add_vline(
            x=mean_time,
            line_dash="dot",
            line_color="#10b981",  # chart-3
            line_width=2,
            annotation_text=f"Mean: {mean_time:.2f}s",
            annotation_position="bottom"
        )
        
        fig.add_vline(
            x=median_time,
            line_dash="dot",
            line_color="#f59e0b",  # chart-4
            line_width=2,
            annotation_text=f"Median: {median_time:.2f}s",
            annotation_position="bottom"
        )
        
        title = f"Cohort Distribution - {event_pattern} ({gender_label}) - Birth Year {birth_year}"
        yaxis_title = "Density"
        
    else:  # histogram
        # Create histogram
        fig.add_trace(go.Histogram(
            x=cohort_times,
            nbinsx=30,
            name='Cohort Times',
            marker=dict(
                color='#06b6d4',  # accent
                line=dict(color='#4f46e5', width=1)  # primary
            ),
            opacity=0.7,
            hovertemplate='<b>Time Range:</b> %{x}<br>' +
                          '<b>Count:</b> %{y}<br>' +
                          '<extra></extra>'
        ))
        
        # Add swimmer's time marker
        fig.add_vline(
            x=swimmer_time,
            line_dash="dash",
            line_color="#ef4444",  # destructive
            line_width=3,
            annotation_text=f"{swimmer_name}",
            annotation_position="top"
        )
        
        title = f"Distribution of Best Times - {len(cohort_data)} swimmers"
        yaxis_title = "Count"
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, family='Arial, sans-serif'),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="Time (seconds)",
        yaxis_title=yaxis_title,
        hovermode='closest',
        template='plotly_white',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(79, 70, 229, 0.1)'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(79, 70, 229, 0.1)'
        )
    )
    
    return fig


def create_percentile_gauge(percentile: float) -> go.Figure:
    """
    Create a gauge chart showing percentile ranking.
    
    Parameters
    ----------
    percentile : float
        Percentile value (0-100)
    
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    # Determine color based on percentile
    if percentile >= 90:
        color = "darkgreen"
    elif percentile >= 75:
        color = "green"
    elif percentile >= 50:
        color = "yellow"
    elif percentile >= 25:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentile,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Percentile Rank", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': '#ffcccc'},
                {'range': [25, 50], 'color': '#ffffcc'},
                {'range': [50, 75], 'color': '#ccffcc'},
                {'range': [75, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def create_improvement_chart(
    swimmer_data: pd.DataFrame,
    swimmer_name: str,
    event_pattern: str
) -> go.Figure:
    """
    Create a chart showing improvement metrics over time.
    
    Parameters
    ----------
    swimmer_data : pd.DataFrame
        DataFrame containing swimmer's results
    swimmer_name : str
        Name of the swimmer
    event_pattern : str
        Event pattern being analyzed
    
    Returns
    -------
    go.Figure
        Plotly figure object
    """
    swimmer_data = swimmer_data.sort_values('Date').copy()
    
    # Calculate rolling best and improvement from first time
    swimmer_data['rolling_best'] = swimmer_data['result_seconds'].cummin()
    first_time = swimmer_data['result_seconds'].iloc[0]
    swimmer_data['improvement_seconds'] = first_time - swimmer_data['result_seconds']
    swimmer_data['improvement_pct'] = (swimmer_data['improvement_seconds'] / first_time) * 100
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add improvement in seconds
    fig.add_trace(go.Scatter(
        x=swimmer_data['Date'],
        y=swimmer_data['improvement_seconds'],
        mode='lines+markers',
        name='Improvement (seconds)',
        line=dict(color='green', width=2),
        marker=dict(size=8),
        yaxis='y1'
    ))
    
    # Add improvement percentage on secondary axis
    fig.add_trace(go.Scatter(
        x=swimmer_data['Date'],
        y=swimmer_data['improvement_pct'],
        mode='lines+markers',
        name='Improvement (%)',
        line=dict(color='orange', width=2, dash='dash'),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    # Update layout with dual axes
    fig.update_layout(
        title=f"{swimmer_name} - {event_pattern} Improvement Progress",
        xaxis=dict(title="Date"),
        yaxis=dict(
            title="Improvement (seconds)",
            titlefont=dict(color="green"),
            tickfont=dict(color="green")
        ),
        yaxis2=dict(
            title="Improvement (%)",
            titlefont=dict(color="orange"),
            tickfont=dict(color="orange"),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        hovermode='x unified',
        template='plotly_white',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig
