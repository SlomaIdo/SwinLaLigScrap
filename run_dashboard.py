"""
Quick start script for the Swimming Dashboard

This script provides a simple way to launch the dashboard with
error checking and helpful messages.
"""

import sys
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed."""
    required_packages = [
        'dash',
        'dash_bootstrap_components',
        'plotly',
        'pandas',
        'numpy',
        'scipy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nPlease install requirements:")
        print("   pip install -r ui/requirements.txt")
        return False
    
    return True


def check_database():
    """Check if the database file exists."""
    db_path = Path(__file__).parent / "swim_database_2.sqlite3"
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        print("\nPlease ensure the database file exists.")
        return False
    
    print(f"✓ Database found: {db_path}")
    return True


def main():
    """Main function to launch the dashboard."""
    print("=" * 60)
    print("🏊 Swimming Performance Analysis Dashboard")
    print("=" * 60)
    print()
    
    # Check requirements
    print("Checking requirements...")
    if not check_requirements():
        sys.exit(1)
    print("✓ All required packages installed")
    print()
    
    # Check database
    print("Checking database...")
    if not check_database():
        sys.exit(1)
    print()
    
    # Import and run the app
    print("Starting dashboard...")
    print()
    print("🌐 Dashboard will be available at: http://localhost:8050")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        from ui.app import app
        app.run_server(debug=True, host="0.0.0.0", port=8050)
    except KeyboardInterrupt:
        print("\n\n✓ Dashboard stopped")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
