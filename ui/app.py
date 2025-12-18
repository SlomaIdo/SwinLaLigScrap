"""
Swimming Performance Analysis Dashboard

A Dash-based web application for analyzing swimming performance data from the ISR database.
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ui.data_loader import DataLoader
from ui.components import (
    create_swimmer_dropdown,
    create_event_dropdown,
    create_category_dropdown,
    create_performance_chart,
    create_distribution_chart,
    create_comparison_chart
)

# Initialize the Dash app with custom styling
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    assets_folder='assets'
)

# Initialize data loader
data_loader = DataLoader()

# Load initial data
df = data_loader.load_data()
swimmers = data_loader.get_swimmers()
events = data_loader.get_events()
categories = data_loader.get_categories()

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1(
                    "🏊 Swimming Performance Analysis Dashboard",
                    className="text-center mb-2"
                ),
                html.P(
                    "Analyze swimmer performance, compare against cohorts, and explore event distributions",
                    className="text-center mb-0"
                ),
            ], className="dashboard-header")
        ])
    ]),
    
    # Data refresh button and status
    dbc.Row([
        dbc.Col([
            dbc.Button(
                [html.I(className="fas fa-sync-alt me-2"), "Refresh Data"],
                id="refresh-button",
                color="primary",
                className="mb-3"
            ),
            html.Div(id="refresh-status", className="mb-3")
        ], width=12)
    ]),
    
    # Tabs for different analysis views
    dbc.Tabs([
        # Tab 1: Individual Performance Analysis
        dbc.Tab(label="Individual Performance", tab_id="tab-individual", children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H4("Swimmer Selection", className="mt-4 mb-3"),
                        dbc.Label("Select Swimmer:"),
                        dcc.Dropdown(
                            id="swimmer-dropdown",
                            options=[{"label": name, "value": name} for name in swimmers],
                            placeholder="Search for a swimmer...",
                            searchable=True,
                            clearable=True
                        ),
                    ], md=6),
                    dbc.Col([
                        html.H4("Event Selection", className="mt-4 mb-3"),
                        dbc.Label("Select Event:"),
                        dcc.Dropdown(
                            id="event-dropdown-individual",
                            options=[{"label": event, "value": event} for event in events],
                            placeholder="Search for an event...",
                            searchable=True,
                            clearable=True
                        ),
                    ], md=6),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Analyze Performance",
                            id="analyze-button",
                            color="success",
                            className="w-100"
                        ),
                    ], md=12)
                ], className="mb-4"),
                
                # Performance statistics cards
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5("Total Races"),
                            html.H2(id="stat-total-races", children="--", className="text-primary")
                        ], className="stat-card")
                    ], md=3),
                    dbc.Col([
                        html.Div([
                            html.H5("Best Time"),
                            html.H2(id="stat-best-time", children="--", className="text-success")
                        ], className="stat-card")
                    ], md=3),
                    dbc.Col([
                        html.Div([
                            html.H5("Latest Time"),
                            html.H2(id="stat-latest-time", children="--", className="text-info")
                        ], className="stat-card")
                    ], md=3),
                    dbc.Col([
                        html.Div([
                            html.H5("Improvement"),
                            html.H2(id="stat-improvement", children="--", className="text-warning")
                        ], className="stat-card")
                    ], md=3),
                ], className="mb-4"),
                
                # Performance chart
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dcc.Graph(id="performance-chart")
                        ], className="graph-container")
                    ])
                ]),
            ], fluid=True)
        ]),
        
        # Tab 2: Event Distribution Analysis
        dbc.Tab(label="Event Distribution", tab_id="tab-distribution", children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H4("Event Selection", className="mt-4 mb-3"),
                        dbc.Label("Select Event:"),
                        dcc.Dropdown(
                            id="event-dropdown-distribution",
                            options=[{"label": event, "value": event} for event in events],
                            placeholder="Search for an event...",
                            searchable=True,
                            clearable=True
                        ),
                    ], md=6),
                    dbc.Col([
                        html.H4("Category Filter", className="mt-4 mb-3"),
                        dbc.Label("Select Categories (optional):"),
                        dcc.Dropdown(
                            id="category-dropdown",
                            options=[{"label": cat, "value": cat} for cat in categories],
                            placeholder="All categories",
                            multi=True,
                            searchable=True,
                            clearable=True
                        ),
                    ], md=6),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Analyze Distribution",
                            id="distribution-button",
                            color="success",
                            className="w-100"
                        ),
                    ], md=12)
                ], className="mb-4"),
                
                # Distribution statistics
                dbc.Row([
                    dbc.Col([
                        html.Div(id="distribution-stats")
                    ])
                ], className="mb-4"),
                
                # Distribution chart
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dcc.Graph(id="distribution-chart")
                        ], className="graph-container")
                    ])
                ]),
            ], fluid=True)
        ]),
        
        # Tab 3: Comparative Analysis
        dbc.Tab(label="Cohort Comparison", tab_id="tab-comparison", children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H4("Swimmer Selection", className="mt-4 mb-3"),
                        dbc.Label("Select Swimmer:"),
                        dcc.Dropdown(
                            id="swimmer-dropdown-comparison",
                            options=[{"label": name, "value": name} for name in swimmers],
                            placeholder="Search for a swimmer...",
                            searchable=True,
                            clearable=True
                        ),
                    ], md=4),
                    dbc.Col([
                        html.H4("Event Selection", className="mt-4 mb-3"),
                        dbc.Label("Select Event:"),
                        dcc.Dropdown(
                            id="event-dropdown-comparison",
                            options=[{"label": event, "value": event} for event in events],
                            placeholder="Search for an event...",
                            searchable=True,
                            clearable=True
                        ),
                    ], md=4),
                    dbc.Col([
                        html.H4("Gender Selection", className="mt-4 mb-3"),
                        dbc.Label("Select Gender:"),
                        dcc.Dropdown(
                            id="gender-dropdown",
                            options=[
                                {"label": "Boys", "value": "Boys"},
                                {"label": "Girls", "value": "Girls"}
                            ],
                            placeholder="Select gender...",
                            clearable=True
                        ),
                    ], md=4),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Compare with Cohort",
                            id="comparison-button",
                            color="success",
                            className="w-100"
                        ),
                    ], md=12)
                ], className="mb-4"),
                
                # Comparison statistics cards
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5("Swimmer's Time"),
                            html.H2(id="comp-swimmer-time", children="--", className="text-primary")
                        ], className="stat-card")
                    ], md=2),
                    dbc.Col([
                        html.Div([
                            html.H5("Cohort Size"),
                            html.H2(id="comp-cohort-size", children="--", className="text-info")
                        ], className="stat-card")
                    ], md=2),
                    dbc.Col([
                        html.Div([
                            html.H5("Cohort Mean"),
                            html.H2(id="comp-cohort-mean", children="--", className="text-secondary")
                        ], className="stat-card")
                    ], md=2),
                    dbc.Col([
                        html.Div([
                            html.H5("Percentile"),
                            html.H2(id="comp-percentile", children="--", className="text-success")
                        ], className="stat-card")
                    ], md=2),
                    dbc.Col([
                        html.Div([
                            html.H5("Faster Than"),
                            html.H2(id="comp-faster-than", children="--", className="text-warning")
                        ], className="stat-card")
                    ], md=2),
                    dbc.Col([
                        html.Div([
                            html.H5("Birth Year"),
                            html.H2(id="comp-birth-year", children="--", className="text-dark")
                        ], className="stat-card")
                    ], md=2),
                ], className="mb-4"),
                
                # Comparison charts
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dcc.Graph(id="comparison-density-chart")
                        ], className="graph-container")
                    ], md=12)
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dcc.Graph(id="comparison-histogram-chart")
                        ], className="graph-container")
                    ], md=12)
                ]),
            ], fluid=True)
        ]),
        
        # Tab 4: Data Explorer
        dbc.Tab(label="Data Explorer", tab_id="tab-explorer", children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col([
                        html.H4("Database Overview", className="mt-4 mb-3"),
                        html.Div(id="database-stats")
                    ])
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        html.H5("Recent Results", className="mb-3"),
                        html.Div(id="recent-results-table")
                    ])
                ]),
            ], fluid=True)
        ]),
    ], id="tabs", active_tab="tab-individual"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P(
                "Swimming Performance Analysis Dashboard - Israeli Swimming Records",
                className="text-center text-muted mb-4"
            )
        ])
    ])
], fluid=True)


# Callbacks

@app.callback(
    [Output("refresh-status", "children"),
     Output("swimmer-dropdown", "options"),
     Output("swimmer-dropdown-comparison", "options"),
     Output("event-dropdown-individual", "options"),
     Output("event-dropdown-distribution", "options"),
     Output("event-dropdown-comparison", "options"),
     Output("category-dropdown", "options")],
    Input("refresh-button", "n_clicks"),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    """Refresh data from database"""
    global df, swimmers, events, categories
    
    try:
        df = data_loader.load_data()
        swimmers = data_loader.get_swimmers()
        events = data_loader.get_events()
        categories = data_loader.get_categories()
        
        swimmer_options = [{"label": name, "value": name} for name in swimmers]
        event_options = [{"label": event, "value": event} for event in events]
        category_options = [{"label": cat, "value": cat} for cat in categories]
        
        status = dbc.Alert(
            f"Data refreshed successfully! Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            color="success",
            dismissable=True,
            duration=4000
        )
        
        return status, swimmer_options, swimmer_options, event_options, event_options, event_options, category_options
    except Exception as e:
        status = dbc.Alert(f"Error refreshing data: {str(e)}", color="danger", dismissable=True)
        return status, [], [], [], [], [], []


@app.callback(
    [Output("stat-total-races", "children"),
     Output("stat-best-time", "children"),
     Output("stat-latest-time", "children"),
     Output("stat-improvement", "children"),
     Output("performance-chart", "figure")],
    Input("analyze-button", "n_clicks"),
    [State("swimmer-dropdown", "value"),
     State("event-dropdown-individual", "value")],
    prevent_initial_call=True
)
def update_individual_performance(n_clicks, swimmer_name, event_pattern):
    """Update individual performance analysis"""
    if not swimmer_name or not event_pattern:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Please select both a swimmer and an event",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return "--", "--", "--", "--", empty_fig
    
    try:
        # Filter data for the specific swimmer and event
        swimmer_data = df[
            (df['Full name'].str.upper() == swimmer_name.upper()) & 
            (df['Event'].str.contains(event_pattern, case=False, na=False))
        ].copy()
        
        # Sort by date
        swimmer_data = swimmer_data.sort_values('Date')
        
        if len(swimmer_data) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text=f"No data found for {swimmer_name} in {event_pattern}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return "--", "--", "--", "--", empty_fig
        
        # Calculate statistics
        total_races = len(swimmer_data)
        best_time = swimmer_data['result_seconds'].min()
        latest_time = swimmer_data['result_seconds'].iloc[-1]
        
        if len(swimmer_data) >= 2:
            first_time = swimmer_data['result_seconds'].iloc[0]
            improvement = first_time - best_time
            improvement_pct = (improvement / first_time) * 100
            improvement_text = f"-{improvement:.2f}s ({improvement_pct:.1f}%)"
        else:
            improvement_text = "N/A"
        
        # Create performance chart
        fig = create_performance_chart(swimmer_data, swimmer_name, event_pattern)
        
        return (
            str(total_races),
            f"{best_time:.2f}s",
            f"{latest_time:.2f}s",
            improvement_text,
            fig
        )
    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red")
        )
        return "--", "--", "--", f"Error: {str(e)}", empty_fig


@app.callback(
    [Output("distribution-stats", "children"),
     Output("distribution-chart", "figure")],
    Input("distribution-button", "n_clicks"),
    [State("event-dropdown-distribution", "value"),
     State("category-dropdown", "value")],
    prevent_initial_call=True
)
def update_distribution(n_clicks, event_pattern, selected_categories):
    """Update event distribution analysis"""
    if not event_pattern:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Please select an event",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return html.Div("No data"), empty_fig
    
    try:
        # Filter data
        event_data = df[df['Event'].str.contains(event_pattern, case=False, na=False)].copy()
        
        if selected_categories:
            event_data = event_data[event_data['Category'].isin(selected_categories)]
        
        if len(event_data) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text=f"No data found for {event_pattern}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return html.Div("No data"), empty_fig
        
        # Create statistics cards
        stats_data = event_data.groupby('Category')['result_seconds'].agg([
            ('count', 'count'),
            ('mean', lambda x: f"{x.mean():.2f}s"),
            ('median', lambda x: f"{x.median():.2f}s"),
            ('min', lambda x: f"{x.min():.2f}s"),
            ('max', lambda x: f"{x.max():.2f}s")
        ]).reset_index()
        
        stats_table = dbc.Table.from_dataframe(
            stats_data,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True
        )
        
        stats_content = html.Div([
            html.H5(f"Total Results: {len(event_data)}", className="mb-3"),
            stats_table
        ])
        
        # Create distribution chart
        fig = create_distribution_chart(event_data, event_pattern)
        
        return stats_content, fig
    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red")
        )
        return html.Div(f"Error: {str(e)}"), empty_fig


@app.callback(
    [Output("comp-swimmer-time", "children"),
     Output("comp-cohort-size", "children"),
     Output("comp-cohort-mean", "children"),
     Output("comp-percentile", "children"),
     Output("comp-faster-than", "children"),
     Output("comp-birth-year", "children"),
     Output("comparison-density-chart", "figure"),
     Output("comparison-histogram-chart", "figure")],
    Input("comparison-button", "n_clicks"),
    [State("swimmer-dropdown-comparison", "value"),
     State("event-dropdown-comparison", "value"),
     State("gender-dropdown", "value")],
    prevent_initial_call=True
)
def update_comparison(n_clicks, swimmer_name, event_pattern, gender):
    """Update cohort comparison analysis"""
    if not swimmer_name or not event_pattern or not gender:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Please select swimmer, event, and gender",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return "--", "--", "--", "--", "--", "--", empty_fig, empty_fig
    
    try:
        # Get swimmer's birth year
        swimmer_data_all = df[df['Full name'].str.upper() == swimmer_name.upper()]
        
        if len(swimmer_data_all) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text=f"No data found for {swimmer_name}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return "--", "--", "--", "--", "--", "--", empty_fig, empty_fig
        
        swimmer_birth_year = swimmer_data_all['Year Of Birth'].iloc[0]
        
        # Filter cohort data
        event_data = df[
            (df['Year Of Birth'] == swimmer_birth_year) &
            (df['Event'].str.contains(event_pattern, case=False, na=False)) &
            (df['Category'].str.contains(gender, case=False, na=False))
        ].copy()
        
        if len(event_data) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text=f"No cohort data found",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return "--", "--", "--", "--", "--", str(int(swimmer_birth_year)), empty_fig, empty_fig
        
        # Get best times
        cohort_data = event_data.groupby('Full name', as_index=False)['result_seconds'].min()
        swimmer_best = cohort_data[cohort_data['Full name'].str.upper() == swimmer_name.upper()]
        
        if len(swimmer_best) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text=f"No event data found for {swimmer_name}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return "--", "--", "--", "--", "--", str(int(swimmer_birth_year)), empty_fig, empty_fig
        
        swimmer_time = swimmer_best['result_seconds'].iloc[0]
        cohort_times = cohort_data['result_seconds']
        
        # Calculate statistics
        from scipy import stats as scipy_stats
        percentile = scipy_stats.percentileofscore(cohort_times, swimmer_time, kind='rank')
        faster_count = (cohort_times < swimmer_time).sum()
        cohort_mean = cohort_times.mean()
        
        # Create charts
        density_fig = create_comparison_chart(
            cohort_data, swimmer_name, swimmer_time, event_pattern, gender, 
            int(swimmer_birth_year), chart_type="density"
        )
        histogram_fig = create_comparison_chart(
            cohort_data, swimmer_name, swimmer_time, event_pattern, gender,
            int(swimmer_birth_year), chart_type="histogram"
        )
        
        return (
            f"{swimmer_time:.2f}s",
            str(len(cohort_data)),
            f"{cohort_mean:.2f}s",
            f"{percentile:.1f}%",
            str(faster_count),
            str(int(swimmer_birth_year)),
            density_fig,
            histogram_fig
        )
    except Exception as e:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red")
        )
        return "--", "--", "--", "--", "--", "--", empty_fig, empty_fig


@app.callback(
    [Output("database-stats", "children"),
     Output("recent-results-table", "children")],
    Input("tabs", "active_tab")
)
def update_data_explorer(active_tab):
    """Update data explorer tab"""
    if active_tab != "tab-explorer":
        return html.Div(), html.Div()
    
    try:
        # Database statistics
        total_results = len(df)
        total_swimmers = df['Full name'].nunique()
        total_events = df['Event'].nunique()
        total_competitions = df['competition_name'].nunique() if 'competition_name' in df.columns else 'N/A'
        
        date_range = "N/A"
        if 'Date' in df.columns:
            date_range = f"{df['Date'].min()} to {df['Date'].max()}"
        
        stats_cards = dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Total Results"),
                    html.H3(f"{total_results:,}", className="text-primary")
                ], className="stat-card")
            ], md=3),
            dbc.Col([
                html.Div([
                    html.H5("Unique Swimmers"),
                    html.H3(f"{total_swimmers:,}", className="text-success")
                ], className="stat-card")
            ], md=3),
            dbc.Col([
                html.Div([
                    html.H5("Unique Events"),
                    html.H3(f"{total_events:,}", className="text-info")
                ], className="stat-card")
            ], md=3),
            dbc.Col([
                html.Div([
                    html.H5("Date Range"),
                    html.H6(date_range, className="text-secondary")
                ], className="stat-card")
            ], md=3),
        ])
        
        # Recent results
        recent_df = df.sort_values('Date', ascending=False).head(50) if 'Date' in df.columns else df.head(50)
        display_columns = ['Date', 'Full name', 'Event', 'Category', 'result_seconds', 'Club']
        display_columns = [col for col in display_columns if col in recent_df.columns]
        
        recent_table = dbc.Table.from_dataframe(
            recent_df[display_columns],
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            size='sm'
        )
        
        return stats_cards, recent_table
    except Exception as e:
        return html.Div(f"Error loading data: {str(e)}"), html.Div()


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
