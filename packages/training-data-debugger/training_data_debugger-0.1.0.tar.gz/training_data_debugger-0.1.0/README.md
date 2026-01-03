# Training Data Debugger

[![PyPI version](https://badge.fury.io/py/training-data-debugger.svg)](https://badge.fury.io/py/training-data-debugger)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Find and fix issues in your ML training data before they degrade model performance.**

Training Data Debugger automatically identifies data quality issues that commonly cause ML models to underperform, including duplicates, label errors, outliers, class imbalance, missing values, and PII exposure.

## Features

- 🔍 **Duplicate Detection** - Find exact and near-duplicate samples using hash-based and n-gram similarity
- 🏷️ **Label Error Detection** - Identify mislabeled samples and label inconsistencies
- 📊 **Outlier Detection** - Detect statistical outliers using multiple methods
- ⚖️ **Class Imbalance Analysis** - Measure imbalance ratios and get rebalancing suggestions
- 🕳️ **Missing Value Analysis** - Find null, empty, and placeholder values
- 📝 **Text Quality Checks** - Detect encoding errors, length anomalies, and quality issues
- 🔒 **PII Exposure Detection** - Find exposed emails, phone numbers, SSNs in your data
- 📈 **Comprehensive Statistics** - Get detailed dataset and column-level statistics
- 🎯 **Actionable Suggestions** - Receive specific recommendations for each issue

## Installation

```bash
# Basic installation (zero dependencies)
pip install training-data-debugger

# With ML capabilities (numpy, pandas, scikit-learn)
pip install training-data-debugger[ml]

# With visualization (matplotlib, seaborn)
pip install training-data-debugger[viz]

# Full installation
pip install training-data-debugger[full]
```

## Quick Start

### Basic Usage

```python
from training_data_debugger import DataDebugger

# Your training data
texts = [
    "The product is great!",
    "The product is great!",  # Duplicate
    "Terrible experience, never buying again",
    "Contact me at john@email.com",  # PII
    "",  # Empty
    "Love it! ⭐⭐⭐⭐⭐",
]
labels = ["positive", "negative", "negative", "positive", "positive", "positive"]
#                      ^ Wrong label (duplicate with different label)

# Debug your data
debugger = DataDebugger()
results = debugger.debug(texts, labels)

# View results
print(f"Total issues found: {results.total_issues}")
print(f"Critical issues: {results.critical_count}")

for issue in results.issues:
    print(f"[{issue.severity.value}] {issue.issue_type.value}: {issue.description}")
```

### Text Data Debugging

```python
from training_data_debugger import TextDataDebugger

debugger = TextDataDebugger()

# Debug text classification data
texts = [
    "Great movie, loved every minute!",
    "Great movie, loved every minute!",  # Exact duplicate
    "Gret moive, lovd evry minite!",     # Near duplicate (typos)
    "Bad",                                # Too short
    "Contact: test@email.com 555-1234",  # PII
    "",                                   # Empty
]
labels = ["positive", "negative", "positive", "positive", "neutral", "positive"]

results = debugger.debug(texts, labels)

# Access specific issue types
duplicates = results.get_issues_by_type(IssueType.DUPLICATE)
label_errors = results.get_issues_by_type(IssueType.LABEL_ERROR)
pii_issues = results.get_issues_by_type(IssueType.PII_EXPOSURE)
```

### Tabular Data Debugging

```python
from training_data_debugger import TabularDataDebugger

debugger = TabularDataDebugger()

# Debug tabular data (as list of dicts)
data = [
    {"age": 25, "income": 50000, "city": "NYC", "target": 1},
    {"age": 25, "income": 50000, "city": "NYC", "target": 0},  # Duplicate, different label
    {"age": 150, "income": 50000, "city": "LA", "target": 1},  # Outlier age
    {"age": None, "income": 75000, "city": "", "target": 1},   # Missing values
    {"age": 30, "income": -5000, "city": "Chicago", "target": 0},  # Invalid income
]

results = debugger.debug(data, label_column="target")

# Get statistics
print(f"Dataset size: {results.statistics.total_samples}")
print(f"Missing value rate: {results.statistics.missing_rate:.2%}")
```

## Configuration

Customize detection thresholds and enable/disable specific checks:

```python
from training_data_debugger import DataDebugger, DebugConfig

config = DebugConfig(
    # Detection toggles
    check_duplicates=True,
    check_label_errors=True,
    check_outliers=True,
    check_class_imbalance=True,
    check_missing_values=True,
    check_text_quality=True,
    check_pii=True,
    
    # Thresholds
    duplicate_threshold=0.9,      # Similarity threshold for near-duplicates
    outlier_std_threshold=3.0,    # Standard deviations for outlier detection
    imbalance_threshold=0.1,      # Minority class ratio threshold
    min_text_length=10,           # Minimum acceptable text length
    max_text_length=10000,        # Maximum acceptable text length
    
    # N-gram settings for near-duplicate detection
    ngram_size=3,
    
    # Severity configuration
    duplicate_severity=IssueSeverity.HIGH,
    label_error_severity=IssueSeverity.CRITICAL,
)

debugger = DataDebugger(config=config)
results = debugger.debug(texts, labels)
```

## Issue Types

| Issue Type | Description | Default Severity |
|------------|-------------|------------------|
| `DUPLICATE` | Exact duplicate samples | HIGH |
| `NEAR_DUPLICATE` | Similar samples (n-gram based) | MEDIUM |
| `LABEL_ERROR` | Same content with different labels | CRITICAL |
| `LABEL_INCONSISTENCY` | Inconsistent labeling patterns | HIGH |
| `OUTLIER` | Statistical outliers | MEDIUM |
| `CLASS_IMBALANCE` | Imbalanced class distribution | MEDIUM |
| `MISSING_VALUE` | Null or empty values | HIGH |
| `TEXT_TOO_SHORT` | Text below minimum length | LOW |
| `TEXT_TOO_LONG` | Text above maximum length | LOW |
| `ENCODING_ERROR` | Character encoding issues | MEDIUM |
| `PII_EXPOSURE` | Personal information exposed | CRITICAL |
| `INVALID_FORMAT` | Data format issues | MEDIUM |
| `DISTRIBUTION_SHIFT` | Feature distribution anomalies | MEDIUM |

## Working with Results

### Filtering Issues

```python
from training_data_debugger import IssueType, IssueSeverity

# Get issues by type
duplicates = results.get_issues_by_type(IssueType.DUPLICATE)

# Get issues by severity
critical = results.get_issues_by_severity(IssueSeverity.CRITICAL)
high_priority = results.get_issues_by_severity(IssueSeverity.HIGH)

# Get affected indices
affected_indices = results.get_affected_indices()
```

### Generating Reports

```python
# JSON report
json_report = results.to_json(indent=2)

# Dictionary format
report_dict = results.to_dict()

# Summary statistics
print(f"Total samples: {results.statistics.total_samples}")
print(f"Unique samples: {results.statistics.unique_samples}")
print(f"Duplicate rate: {results.statistics.duplicate_rate:.2%}")
print(f"Missing rate: {results.statistics.missing_rate:.2%}")
print(f"Label distribution: {results.statistics.label_distribution}")
```

### Getting Recommendations

```python
# Each issue includes suggestions
for issue in results.issues:
    print(f"Issue: {issue.description}")
    print(f"Suggestion: {issue.suggestion}")
    print(f"Affected indices: {issue.indices}")
    print("---")
```

## Advanced Usage

### Custom Issue Detection

```python
from training_data_debugger import DataDebugger, DataIssue, IssueType, IssueSeverity

class CustomDebugger(DataDebugger):
    def _detect_custom_issues(self, data, labels):
        """Add custom detection logic."""
        issues = []
        
        for i, text in enumerate(data):
            # Custom check: detect specific patterns
            if "CONFIDENTIAL" in str(text).upper():
                issues.append(DataIssue(
                    issue_type=IssueType.PII_EXPOSURE,
                    severity=IssueSeverity.CRITICAL,
                    indices=[i],
                    description=f"Confidential marker found at index {i}",
                    suggestion="Remove or redact confidential content",
                    details={"pattern": "CONFIDENTIAL"}
                ))
        
        return issues
    
    def debug(self, data, labels=None):
        results = super().debug(data, labels)
        custom_issues = self._detect_custom_issues(data, labels)
        results.issues.extend(custom_issues)
        return results
```

### Batch Processing

```python
from training_data_debugger import DataDebugger

debugger = DataDebugger()

# Process large datasets in batches
def debug_in_batches(data, labels, batch_size=10000):
    all_issues = []
    
    for i in range(0, len(data), batch_size):
        batch_data = data[i:i+batch_size]
        batch_labels = labels[i:i+batch_size] if labels else None
        
        results = debugger.debug(batch_data, batch_labels)
        
        # Adjust indices for batch offset
        for issue in results.issues:
            issue.indices = [idx + i for idx in issue.indices]
        
        all_issues.extend(results.issues)
    
    return all_issues
```

### Integration with Pandas

```python
import pandas as pd
from training_data_debugger import TabularDataDebugger

# Load your data
df = pd.read_csv("training_data.csv")

# Convert to list of dicts for debugging
data = df.to_dict(orient="records")

debugger = TabularDataDebugger()
results = debugger.debug(data, label_column="target")

# Get clean indices
problematic_indices = results.get_affected_indices()
clean_df = df.drop(index=problematic_indices)

print(f"Removed {len(problematic_indices)} problematic samples")
print(f"Clean dataset size: {len(clean_df)}")
```

## Statistics Reference

### Dataset Statistics

```python
stats = results.statistics

# Basic counts
stats.total_samples      # Total number of samples
stats.unique_samples     # Number of unique samples
stats.duplicate_count    # Number of duplicates
stats.missing_count      # Number of missing values

# Rates
stats.duplicate_rate     # Proportion of duplicates
stats.missing_rate       # Proportion of missing values

# Label information
stats.label_distribution # Dict of label -> count
stats.class_weights      # Suggested weights for imbalance

# Text statistics (if applicable)
stats.avg_text_length    # Average text length
stats.min_text_length    # Minimum text length
stats.max_text_length    # Maximum text length
```

### Column Statistics (Tabular Data)

```python
for col_name, col_stats in results.column_statistics.items():
    print(f"Column: {col_name}")
    print(f"  Type: {col_stats.data_type}")
    print(f"  Missing: {col_stats.missing_count}")
    print(f"  Unique: {col_stats.unique_count}")
    print(f"  Mean: {col_stats.mean}")
    print(f"  Std: {col_stats.std}")
```

## Best Practices

1. **Run Early**: Debug your data before training to catch issues early
2. **Prioritize Critical Issues**: Address CRITICAL and HIGH severity issues first
3. **Iterative Cleaning**: Run the debugger multiple times as you fix issues
4. **Document Decisions**: Keep track of why certain samples were removed/modified
5. **Validate Fixes**: Verify that fixes don't introduce new problems

## API Reference

### Classes

- `DataDebugger` - Main debugger for general data
- `TextDataDebugger` - Specialized debugger for text data
- `TabularDataDebugger` - Specialized debugger for tabular data
- `DebugConfig` - Configuration for detection thresholds
- `DebugResults` - Container for debugging results
- `DataIssue` - Individual issue representation

### Enums

- `IssueType` - Types of data issues
- `IssueSeverity` - Issue severity levels (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- `DataType` - Data type classifications

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Created by **Pranay M**

---

**Found an issue?** [Report it on GitHub](https://github.com/pranaym/training-data-debugger/issues)
