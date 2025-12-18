"""
Dashboard Test Script

Quick test to verify all components are working correctly.
Run this before starting the full dashboard.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import dash
        print("  ✓ dash")
        import dash_bootstrap_components
        print("  ✓ dash_bootstrap_components")
        import plotly
        print("  ✓ plotly")
        import pandas
        print("  ✓ pandas")
        import numpy
        print("  ✓ numpy")
        import scipy
        print("  ✓ scipy")
        
        from ui.data_loader import DataLoader
        print("  ✓ ui.data_loader")
        from ui.components import create_performance_chart
        print("  ✓ ui.components")
        
        print("\n✅ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Please run: pip install --user -r ui/requirements.txt")
        return False


def test_database():
    """Test database connection and data loading."""
    print("Testing database connection...")
    try:
        from ui.data_loader import DataLoader
        
        loader = DataLoader()
        df = loader.load_data()
        
        print(f"  ✓ Database loaded: {len(df)} records")
        
        swimmers = loader.get_swimmers()
        print(f"  ✓ Found {len(swimmers)} swimmers")
        
        events = loader.get_events()
        print(f"  ✓ Found {len(events)} events")
        
        categories = loader.get_categories()
        print(f"  ✓ Found {len(categories)} categories")
        
        print("\n✅ Database connection successful!\n")
        return True
    except Exception as e:
        print(f"\n❌ Database error: {e}")
        return False


def test_components():
    """Test that visualization components can be created."""
    print("Testing visualization components...")
    try:
        from ui.data_loader import DataLoader
        from ui.components import create_performance_chart
        import pandas as pd
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=5),
            'result_seconds': [65.2, 64.8, 64.5, 64.9, 64.3]
        })
        
        # Try to create a chart
        fig = create_performance_chart(sample_data, "Test Swimmer", "100m Freestyle")
        
        print("  ✓ Performance chart created")
        print("\n✅ Visualization components working!\n")
        return True
    except Exception as e:
        print(f"\n❌ Component error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Dashboard Component Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test database
    results.append(("Database", test_database()))
    
    # Test components
    results.append(("Components", test_components()))
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20s}: {status}")
    print()
    
    if all(result for _, result in results):
        print("🎉 All tests passed! Dashboard is ready to launch.")
        print("\nTo start the dashboard, run:")
        print("  python run_dashboard.py")
        print("\nOr double-click START_DASHBOARD.bat")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the dashboard.")
        sys.exit(1)


if __name__ == "__main__":
    main()
