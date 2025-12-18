"""
Analysis module for swimming performance features.
"""

from .player_features import (
    individual_performance_analysis,
    event_specific_analysis,
    comparative_analysis
)

__all__ = [
    'individual_performance_analysis',
    'event_specific_analysis',
    'comparative_analysis'
]
