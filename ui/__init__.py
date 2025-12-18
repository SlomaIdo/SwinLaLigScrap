"""
Swimming Performance Analysis Dashboard UI Package

This package provides a web-based dashboard for analyzing swimming performance data
from the Israeli Swimming Records database.
"""

__version__ = "1.0.0"
__author__ = "Swimming Data Analysis Team"

from .data_loader import DataLoader
from .components import (
    create_performance_chart,
    create_distribution_chart,
    create_comparison_chart
)

__all__ = [
    'DataLoader',
    'create_performance_chart',
    'create_distribution_chart',
    'create_comparison_chart'
]
