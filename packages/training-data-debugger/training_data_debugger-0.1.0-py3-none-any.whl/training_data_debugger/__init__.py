"""
Training Data Debugger - Find and fix issues in your ML training data.

A comprehensive toolkit for identifying data quality issues that can
degrade model performance, including duplicates, label errors, outliers,
class imbalance, and more.

Example:
    >>> from training_data_debugger import DataDebugger
    >>> debugger = DataDebugger()
    >>> results = debugger.debug(texts, labels)
    >>> print(f"Found {results.total_issues} issues")
"""

from .types import (
    # Enums
    IssueType,
    IssueSeverity,
    DataType,
    # Data classes
    DataIssue,
    DuplicateInfo,
    LabelErrorInfo,
    OutlierInfo,
    ClassImbalanceInfo,
    MissingValueInfo,
    TextQualityInfo,
    PIIExposureInfo,
    DebugConfig,
    DebugResults,
    DatasetStatistics,
    ColumnStatistics,
)

from .debugger import (
    DataDebugger,
    TextDataDebugger,
    TabularDataDebugger,
)

__version__ = "0.1.0"
__author__ = "Pranay M"
__email__ = "pranay@example.com"

__all__ = [
    # Main classes
    "DataDebugger",
    "TextDataDebugger",
    "TabularDataDebugger",
    # Enums
    "IssueType",
    "IssueSeverity",
    "DataType",
    # Data classes
    "DataIssue",
    "DuplicateInfo",
    "LabelErrorInfo",
    "OutlierInfo",
    "ClassImbalanceInfo",
    "MissingValueInfo",
    "TextQualityInfo",
    "PIIExposureInfo",
    "DebugConfig",
    "DebugResults",
    "DatasetStatistics",
    "ColumnStatistics",
]
