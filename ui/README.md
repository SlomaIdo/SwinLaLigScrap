# Swimming Performance Analysis Dashboard 🏊

A comprehensive web-based dashboard for analyzing swimming performance data from the Israeli Swimming Records (ISR) database.

## Features

### 📊 Individual Performance Analysis
- Track swimmer performance over time for specific events
- View performance statistics: total races, best time, latest time, and improvement
- Interactive time-series charts showing progression and trends
- Identify personal best performances

### 📈 Event Distribution Analysis
- Analyze performance distributions across age groups and categories
- Violin plots showing the spread of times within categories
- Filter by specific categories for focused analysis
- Summary statistics for each category

### 🎯 Cohort Comparison
- Compare individual swimmer performance against same-age cohorts
- Density and histogram visualizations
- Percentile rankings and statistical comparisons
- See how a swimmer ranks within their birth year group

### 🔍 Data Explorer
- Browse database statistics
- View recent results
- Explore the full dataset

## Installation

### Prerequisites
- Python 3.8 or higher
- SQLite database with swimming results (`swim_database_2.sqlite3`)

### Setup

1. **Navigate to the project directory:**
   ```bash
   cd c:\Repository\SwinLaLigScrap
   ```

2. **Install dependencies:**
   ```bash
   pip install -r ui/requirements.txt
   ```

3. **Verify database location:**
   Make sure `swim_database_2.sqlite3` exists in the project root directory.

## Running the Dashboard

### Development Mode

Run the dashboard locally with debug mode enabled:

```bash
python ui/app.py
```

The dashboard will be available at: **http://localhost:8050**

### Production Mode

For production deployment with Gunicorn (Linux/Mac):

```bash
gunicorn ui.app:app.server -b 0.0.0.0:8050
```

For Windows, use waitress:

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8050 ui.app:app.server
```

## Usage Guide

### Individual Performance Tab

1. **Select a swimmer** from the dropdown menu
2. **Select an event** (e.g., "200m Backstroke")
3. Click **"Analyze Performance"**
4. View:
   - Performance statistics in cards
   - Time-series chart showing performance over time
   - Trend line indicating improvement direction

### Event Distribution Tab

1. **Select an event** to analyze
2. (Optional) **Select specific categories** to filter
3. Click **"Analyze Distribution"**
4. View:
   - Summary statistics table by category
   - Violin plot showing time distributions
   - Individual data points overlaid on distributions

### Cohort Comparison Tab

1. **Select a swimmer** to analyze
2. **Select an event** they competed in
3. **Select gender** (Boys/Girls)
4. Click **"Compare with Cohort"**
5. View:
   - Comparison statistics (percentile, cohort size, etc.)
   - Density plot showing swimmer vs cohort distribution
   - Histogram with swimmer's position marked

### Data Explorer Tab

- View overall database statistics
- Browse recent swimming results
- Check data coverage and completeness

## Project Structure

```
ui/
├── __init__.py           # Package initialization
├── app.py                # Main Dash application
├── data_loader.py        # Data loading utilities
├── components.py         # Visualization components
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Technical Details

### Data Sources

The dashboard reads from the `discipline_results_ingest` table in `swim_database_2.sqlite3`, which contains:
- Swimmer names and birth years
- Event details and categories
- Competition dates and results
- Club information
- Performance times

### Data Processing

- **Time Conversion**: Swimming times are automatically converted to seconds for analysis
- **Date Parsing**: Competition dates are parsed for time-series analysis
- **Caching**: Data is cached in memory to improve performance
- **Error Handling**: Robust error handling for missing or invalid data

### Visualization Libraries

- **Plotly**: Interactive charts and graphs
- **Dash**: Web framework for the dashboard
- **Bootstrap**: Responsive UI components

## Configuration

### Database Path

The default database path is `swim_database_2.sqlite3` in the project root. To change this, modify the `DataLoader` initialization in `app.py`:

```python
data_loader = DataLoader(db_path="path/to/your/database.sqlite3")
```

### Port Configuration

To run on a different port, modify the `app.run_server()` call in `app.py`:

```python
app.run_server(debug=True, host="0.0.0.0", port=YOUR_PORT)
```

## Troubleshooting

### Dashboard won't start

- **Check Python version**: Ensure Python 3.8+ is installed
- **Verify dependencies**: Run `pip install -r ui/requirements.txt`
- **Database location**: Confirm `swim_database_2.sqlite3` exists in the correct location

### No data appears

- **Database check**: Verify the database has records in `discipline_results_ingest`
- **Check logs**: Look for error messages in the console
- **Refresh data**: Use the "Refresh Data" button in the dashboard

### Performance issues

- **Data size**: Large datasets may take time to load initially
- **Browser cache**: Clear browser cache if visualizations don't update
- **Memory**: Close other applications if the system is low on memory

## Development

### Adding New Features

1. **New visualization**: Add chart creation functions to `components.py`
2. **New analysis**: Add analysis functions to `src/analysis/player_features.py`
3. **New tab**: Add a new tab in the `app.py` layout and create corresponding callbacks

### Testing

Run the dashboard in debug mode to see detailed error messages:

```python
app.run_server(debug=True)
```

## Dependencies

Main dependencies (see `requirements.txt` for full list):
- `dash` - Web framework
- `dash-bootstrap-components` - Bootstrap components for Dash
- `plotly` - Interactive visualizations
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `scipy` - Statistical analysis

## License

This project is part of the SwinLaLigScrap swimming data scraping and analysis system.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments and docstrings
3. Check the console for error messages

## Future Enhancements

Potential improvements:
- [ ] Export functionality for charts and data
- [ ] Advanced filtering options
- [ ] Custom date range selection
- [ ] Multi-swimmer comparisons
- [ ] Season-over-season analysis
- [ ] Progress prediction models
- [ ] Competition result predictions
- [ ] Club-level analytics

## Contributing

When adding new features:
1. Follow the existing code style
2. Add docstrings to new functions
3. Update this README with new features
4. Test thoroughly before committing

---

**Happy Swimming Analysis! 🏊‍♂️🏊‍♀️**
