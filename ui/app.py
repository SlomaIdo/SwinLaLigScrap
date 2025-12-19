"""
Swimming Performance Analysis Dashboard

A Dash-based web application for analyzing swimming performance data from the ISR database.
"""

import dash
from dash import dcc, html, Input, Output, State, dash_table
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

# Filter out relay teams (names with commas) for individual swimmer analysis
df_individual = df[~df['Full name'].str.contains(',', na=False)].copy()

swimmers = sorted(df_individual['Full name'].dropna().unique())
events = data_loader.get_events()

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
                    ], md=12),
                ], className="mb-4"),
                
                # Swimmer events summary table
                dbc.Row([
                    dbc.Col([
                        html.Div(id="swimmer-events-summary")
                    ])
                ], className="mb-4"),
                
                dbc.Row([
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
                    dbc.Col([
                        html.Div([
                            html.H4("Analyze Event", className="mt-4 mb-3"),
                            dbc.Button(
                                "Analyze Performance",
                                id="analyze-button",
                                color="success",
                                className="w-100 mt-4"
                            ),
                        ])
                    ], md=6),
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
                        html.H4("Gender", className="mt-4 mb-3"),
                        dbc.Label("Select Gender:"),
                        dbc.RadioItems(
                            id="gender-radio-distribution",
                            options=[
                                {"label": "Female (Girls/Women)", "value": "Female"},
                                {"label": "Male (Boys/Men)", "value": "Male"}
                            ],
                            value="Female",
                            inline=True,
                            className="mt-2"
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
                
                # Distribution chart (shown first)
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dcc.Graph(id="distribution-chart")
                        ], className="graph-container")
                    ])
                ], className="mb-4"),
                
                # Distribution statistics (shown below chart)
                dbc.Row([
                    dbc.Col([
                        html.Div(id="distribution-stats")
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
                    ], md=6),
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
                    ], md=6),
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
                
                # Filters section
                dbc.Row([
                    dbc.Col([
                        html.H5("Filter Results", className="mb-3"),
                    ])
                ]),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Club:"),
                        dcc.Dropdown(
                            id="explorer-club-dropdown",
                            options=[],
                            placeholder="All clubs",
                            multi=True,
                            searchable=True,
                            clearable=True
                        ),
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Year of Birth:"),
                        dcc.Dropdown(
                            id="explorer-year-dropdown",
                            options=[],
                            placeholder="All years",
                            multi=True,
                            searchable=True,
                            clearable=True
                        ),
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Gender:"),
                        dcc.Dropdown(
                            id="explorer-gender-dropdown",
                            options=[
                                {"label": "Boys", "value": "Boys"},
                                {"label": "Girls", "value": "Girls"}
                            ],
                            placeholder="All",
                            clearable=True
                        ),
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Event:"),
                        dcc.Dropdown(
                            id="explorer-event-dropdown",
                            options=[],
                            placeholder="All events",
                            searchable=True,
                            clearable=True
                        ),
                    ], md=3),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            [html.I(className="fas fa-search me-2"), "Apply Filters"],
                            id="explorer-filter-button",
                            color="primary",
                            className="me-2"
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-redo me-2"), "Reset Filters"],
                            id="explorer-reset-button",
                            color="secondary"
                        ),
                    ], className="mb-3")
                ]),
                
                # Results section
                dbc.Row([
                    dbc.Col([
                        html.H5(id="results-count", className="mb-3"),
                        html.Div(id="filtered-results-table")
                    ])
                ], className="mb-3"),
                
                # Pagination controls
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            dbc.ButtonGroup([
                                dbc.Button("Previous", id="prev-page-button", color="primary", outline=True),
                                dbc.Button(id="page-info", disabled=True, color="light"),
                                dbc.Button("Next", id="next-page-button", color="primary", outline=True),
                            ]),
                            dcc.Store(id='current-page', data=1),
                            dcc.Store(id='total-pages', data=1),
                        ], className="d-flex justify-content-center")
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
    Output("swimmer-events-summary", "children"),
    Input("swimmer-dropdown", "value")
)
def update_swimmer_events_summary(swimmer_name):
    """Display summary table of all events for selected swimmer"""
    if not swimmer_name:
        return html.Div()
    
    try:
        # Get all data for the swimmer (using individual swimmers only)
        swimmer_data = df_individual[df_individual['Full name'].str.upper() == swimmer_name.upper()].copy()
        
        if len(swimmer_data) == 0:
            return html.Div()
        
        # Group by event and calculate statistics
        event_stats = []
        for event in swimmer_data['Event'].unique():
            event_data = swimmer_data[swimmer_data['Event'] == event].sort_values('Date')
            
            total_races = len(event_data)
            best_time = event_data['result_seconds'].min()
            latest_time = event_data['result_seconds'].iloc[-1]
            first_time = event_data['result_seconds'].iloc[0]
            
            # Calculate total improvement from first to latest (negative means got faster)
            total_improvement = ((latest_time - first_time) / first_time * 100) if first_time > 0 else 0
            
            # Calculate improvement from last race (n from n-1)
            if len(event_data) >= 2:
                second_last_time = event_data['result_seconds'].iloc[-2]
                improvement_from_last = ((latest_time - second_last_time) / second_last_time * 100) if second_last_time > 0 else 0
            else:
                improvement_from_last = 0
            
            event_stats.append({
                'Event': event,
                'Total Races': total_races,
                'Best Time': f"{best_time:.2f}s",
                'Latest Time': f"{latest_time:.2f}s",
                'Total Improvement': f"{total_improvement:+.1f}%",
                'Improvement from Last': f"{improvement_from_last:+.1f}%"
            })
        
        # Create DataFrame and sort by event name
        summary_df = pd.DataFrame(event_stats).sort_values('Event').reset_index(drop=True)
        
        # Create interactive DataTable
        summary_table = dash_table.DataTable(
            id='events-summary-table',
            columns=[{"name": col, "id": col} for col in summary_df.columns],
            data=summary_df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '14px'
            },
            style_header={
                'backgroundColor': '#4f46e5',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'left'
            },
            style_data={
                'backgroundColor': 'white',
                'border': '1px solid #ddd'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f8f9fa'
                },
                {
                    'if': {'state': 'selected'},
                    'backgroundColor': '#e0e7ff',
                    'border': '1px solid #4f46e5'
                }
            ],
            row_selectable='single',
            selected_rows=[],
            page_action='none',
            css=[{
                'selector': '.dash-spreadsheet td div',
                'rule': '''
                    line-height: 15px;
                    max-height: 30px; min-height: 30px; height: 30px;
                    display: block;
                    overflow-y: hidden;
                '''
            }]
        )
        
        return html.Div([
            html.H5(f"Events Summary for {swimmer_name}", className="mb-3"),
            html.P("Click on a row to select that event for detailed analysis", className="text-muted small mb-2"),
            summary_table
        ])
        
    except Exception as e:
        return html.Div(f"Error loading swimmer data: {str(e)}", className="text-danger")


@app.callback(
    Output("event-dropdown-individual", "value"),
    Input("events-summary-table", "selected_rows"),
    State("events-summary-table", "data"),
    prevent_initial_call=True
)
def update_event_from_table(selected_rows, table_data):
    """Update event dropdown when a row is clicked in the summary table"""
    if selected_rows and table_data:
        selected_event = table_data[selected_rows[0]]['Event']
        return selected_event
    return dash.no_update


@app.callback(
    [Output("refresh-status", "children"),
     Output("swimmer-dropdown", "options"),
     Output("swimmer-dropdown-comparison", "options"),
     Output("event-dropdown-individual", "options"),
     Output("event-dropdown-distribution", "options"),
     Output("event-dropdown-comparison", "options")],
    Input("refresh-button", "n_clicks"),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    """Refresh data from database"""
    global df, df_individual, swimmers, events
    
    try:
        df = data_loader.load_data()
        # Filter out relay teams (names with commas)
        df_individual = df[~df['Full name'].str.contains(',', na=False)].copy()
        swimmers = sorted(df_individual['Full name'].dropna().unique())
        events = data_loader.get_events()
        
        swimmer_options = [{"label": name, "value": name} for name in swimmers]
        event_options = [{"label": event, "value": event} for event in events]
        
        status = dbc.Alert(
            f"Data refreshed successfully! Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            color="success",
            dismissable=True,
            duration=4000
        )
        
        return status, swimmer_options, swimmer_options, event_options, event_options, event_options
    except Exception as e:
        status = dbc.Alert(f"Error refreshing data: {str(e)}", color="danger", dismissable=True)
        return status, [], [], [], [], []


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
        # Filter data for the specific swimmer and event (using individual swimmers only)
        swimmer_data = df_individual[
            (df_individual['Full name'].str.upper() == swimmer_name.upper()) & 
            (df_individual['Event'].str.contains(event_pattern, case=False, na=False))
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
     State("gender-radio-distribution", "value")],
    prevent_initial_call=True
)
def update_distribution(n_clicks, event_pattern, selected_gender):
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
        # Filter data by event
        event_data = df[df['Event'].str.contains(event_pattern, case=False, na=False)].copy()
        
        # Filter by gender (Boys/Men or Girls/Women)
        if selected_gender == "Female":
            event_data = event_data[event_data['Category'].str.contains('Girl|Women', case=False, na=False)]
        elif selected_gender == "Male":
            event_data = event_data[event_data['Category'].str.contains('Boy|Men', case=False, na=False)]
        
        if len(event_data) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text=f"No data found for {event_pattern}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return html.Div("No data"), empty_fig
        
        # Calculate swimmer age at the time of the result
        event_data['Date'] = pd.to_datetime(event_data['Date'], errors='coerce')
        event_data['Year Of Birth'] = pd.to_numeric(event_data['Year Of Birth'], errors='coerce')
        event_data['Age'] = event_data['Date'].dt.year - event_data['Year Of Birth']
        
        # Filter out invalid ages and limit to age 22 or below
        event_data = event_data[event_data['Age'].notna() & (event_data['Age'] > 0) & (event_data['Age'] <= 22)]
        
        # Bin ages above 18 into "18+"
        event_data['Age_Binned'] = event_data['Age'].apply(lambda x: '18+' if x > 18 else str(int(x)))
        
        if len(event_data) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text=f"No valid age data found for {event_pattern}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return html.Div("No data"), empty_fig
        
        # Create statistics cards by age (using binned ages for display)
        stats_data = event_data.groupby('Age_Binned')['result_seconds'].agg([
            ('count', 'count'),
            ('mean', lambda x: f"{x.mean():.2f}s"),
            ('median', lambda x: f"{x.median():.2f}s"),
            ('min', lambda x: f"{x.min():.2f}s"),
            ('max', lambda x: f"{x.max():.2f}s")
        ]).reset_index()
        stats_data.rename(columns={'Age_Binned': 'Age'}, inplace=True)
        # Sort with 18+ at the end
        stats_data['sort_key'] = stats_data['Age'].apply(lambda x: 999 if x == '18+' else int(x))
        stats_data = stats_data.sort_values('sort_key').drop(columns=['sort_key'])
        
        stats_table = dbc.Table.from_dataframe(
            stats_data,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True
        )
        
        # Create distribution chart
        fig = create_distribution_chart(event_data, event_pattern)
        
        # Create statistics section below the chart
        stats_content = html.Div([
            html.Hr(className="my-4"),
            html.H5(f"Total Results: {len(event_data)}", className="mb-3"),
            html.P(f"Age Range: {int(event_data['Age'].min())} - {int(event_data['Age'].max())} years", className="text-muted"),
            stats_table
        ])
        
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
     State("event-dropdown-comparison", "value")],
    prevent_initial_call=True
)
def update_comparison(n_clicks, swimmer_name, event_pattern):
    """Update cohort comparison analysis"""
    if not swimmer_name or not event_pattern:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Please select swimmer and event",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return "--", "--", "--", "--", "--", "--", empty_fig, empty_fig
    
    try:
        # Get swimmer's birth year and infer gender (using individual swimmers only)
        swimmer_data_all = df_individual[df_individual['Full name'].str.upper() == swimmer_name.upper()]
        
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
        
        # Infer gender from swimmer's category
        swimmer_category = swimmer_data_all['Category'].iloc[0]
        if 'Girl' in swimmer_category or 'Women' in swimmer_category:
            gender_filter = 'Girl|Women'
            gender_label = 'Girls/Women'
        elif 'Boy' in swimmer_category or 'Men' in swimmer_category:
            gender_filter = 'Boy|Men'
            gender_label = 'Boys/Men'
        else:
            # Default fallback
            gender_filter = 'Boy|Girl|Men|Women'
            gender_label = 'All'
        
        # Filter cohort data (using individual swimmers only to exclude relay teams)
        event_data = df_individual[
            (df_individual['Year Of Birth'] == swimmer_birth_year) &
            (df_individual['Event'].str.contains(event_pattern, case=False, na=False)) &
            (df_individual['Category'].str.contains(gender_filter, case=False, na=False))
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
            cohort_data, swimmer_name, swimmer_time, event_pattern, gender_label, 
            int(swimmer_birth_year), chart_type="density"
        )
        histogram_fig = create_comparison_chart(
            cohort_data, swimmer_name, swimmer_time, event_pattern, gender_label,
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
     Output("explorer-club-dropdown", "options"),
     Output("explorer-year-dropdown", "options"),
     Output("explorer-event-dropdown", "options")],
    Input("tabs", "active_tab")
)
def update_data_explorer_init(active_tab):
    """Initialize data explorer tab with filter options"""
    if active_tab != "tab-explorer":
        return html.Div(), [], [], []
    
    try:
        # Database statistics
        total_results = len(df)
        total_swimmers = df['Full name'].nunique()
        total_events = df['Event'].nunique()
        
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
        
        # Get filter options
        clubs = sorted(df['Club'].dropna().unique()) if 'Club' in df.columns else []
        club_options = [{"label": club, "value": club} for club in clubs]
        
        years = sorted(df['Year Of Birth'].dropna().unique(), reverse=True) if 'Year Of Birth' in df.columns else []
        year_options = [{"label": int(year), "value": year} for year in years]
        
        events = sorted(df['Event'].dropna().unique()) if 'Event' in df.columns else []
        event_options = [{"label": event, "value": event} for event in events]
        
        return stats_cards, club_options, year_options, event_options
    except Exception as e:
        return html.Div(f"Error loading data: {str(e)}"), [], [], []


@app.callback(
    [Output("explorer-club-dropdown", "value"),
     Output("explorer-year-dropdown", "value"),
     Output("explorer-gender-dropdown", "value"),
     Output("explorer-event-dropdown", "value")],
    Input("explorer-reset-button", "n_clicks"),
    prevent_initial_call=True
)
def reset_explorer_filters(n_clicks):
    """Reset all filter dropdowns"""
    return None, None, None, None


@app.callback(
    [Output("filtered-results-table", "children"),
     Output("results-count", "children"),
     Output("current-page", "data"),
     Output("total-pages", "data"),
     Output("page-info", "children")],
    [Input("explorer-filter-button", "n_clicks"),
     Input("prev-page-button", "n_clicks"),
     Input("next-page-button", "n_clicks")],
    [State("explorer-club-dropdown", "value"),
     State("explorer-year-dropdown", "value"),
     State("explorer-gender-dropdown", "value"),
     State("explorer-event-dropdown", "value"),
     State("current-page", "data")],
    prevent_initial_call=True
)
def update_filtered_results(filter_clicks, prev_clicks, next_clicks, clubs, years, gender, event, current_page):
    """Filter and paginate results"""
    ctx = dash.callback_context
    
    # Determine which button was clicked
    if not ctx.triggered:
        button_id = None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Reset to page 1 if filter button was clicked
    if button_id == "explorer-filter-button":
        current_page = 1
    elif button_id == "prev-page-button":
        current_page = max(1, current_page - 1)
    elif button_id == "next-page-button":
        current_page = current_page + 1
    
    try:
        # Start with full dataset
        filtered_df = df.copy()
        
        # Apply filters
        if clubs:
            filtered_df = filtered_df[filtered_df['Club'].isin(clubs)]
        
        if years:
            filtered_df = filtered_df[filtered_df['Year Of Birth'].isin(years)]
        
        if gender:
            filtered_df = filtered_df[filtered_df['Category'].str.contains(gender, case=False, na=False)]
        
        if event:
            filtered_df = filtered_df[filtered_df['Event'] == event]
        
        if len(filtered_df) == 0:
            return (
                html.Div("No results found with the selected filters.", className="text-muted"),
                "Results: 0",
                1,
                1,
                "Page 1 of 1"
            )
        
        # Get best time for each swimmer in each event
        grouped = filtered_df.groupby(['Full name', 'Event'], as_index=False).agg({
            'result_seconds': 'min',
            'Date': 'max',
            'Club': 'first',
            'Category': 'first',
            'Year Of Birth': 'first'
        })
        
        # Sort by best time
        grouped = grouped.sort_values('result_seconds')
        
        # Pagination
        results_per_page = 50
        total_results = len(grouped)
        total_pages = max(1, (total_results + results_per_page - 1) // results_per_page)
        current_page = min(current_page, total_pages)
        
        start_idx = (current_page - 1) * results_per_page
        end_idx = start_idx + results_per_page
        
        page_df = grouped.iloc[start_idx:end_idx]
        
        # Prepare display columns
        display_columns = ['Full name', 'Event', 'result_seconds', 'Date', 'Club', 'Category', 'Year Of Birth']
        display_columns = [col for col in display_columns if col in page_df.columns]
        
        # Rename for display
        display_df = page_df[display_columns].copy()
        display_df['result_seconds'] = display_df['result_seconds'].apply(lambda x: f"{x:.2f}s")
        display_df = display_df.rename(columns={
            'Full name': 'Swimmer',
            'result_seconds': 'Best Time',
            'Year Of Birth': 'Birth Year'
        })
        
        # Create table
        results_table = dbc.Table.from_dataframe(
            display_df,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            size='sm'
        )
        
        results_count = f"Results: {total_results:,} swimmers (showing {start_idx + 1}-{min(end_idx, total_results)})"
        page_info = f"Page {current_page} of {total_pages}"
        
        return results_table, results_count, current_page, total_pages, page_info
        
    except Exception as e:
        return (
            html.Div(f"Error: {str(e)}", className="text-danger"),
            "Results: 0",
            1,
            1,
            "Page 1 of 1"
        )


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
