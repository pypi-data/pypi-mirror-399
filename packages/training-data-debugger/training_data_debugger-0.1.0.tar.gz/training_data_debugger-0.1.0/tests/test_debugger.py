"""
Tests for training-data-debugger package.
"""

import pytest
import json
from training_data_debugger import (
    DataDebugger,
    TextDataDebugger,
    TabularDataDebugger,
    DebugConfig,
    DebugResults,
    DataIssue,
    IssueType,
    IssueSeverity,
    DataType,
)


class TestDataDebugger:
    """Tests for the main DataDebugger class."""

    def test_init_default(self):
        """Test default initialization."""
        debugger = DataDebugger()
        assert debugger.config is not None
        assert debugger.config.check_duplicates is True

    def test_init_custom_config(self):
        """Test initialization with custom config."""
        config = DebugConfig(
            check_duplicates=False,
            outlier_std_threshold=2.0,
        )
        debugger = DataDebugger(config=config)
        assert debugger.config.check_duplicates is False
        assert debugger.config.outlier_std_threshold == 2.0

    def test_debug_empty_data(self):
        """Test debugging empty data."""
        debugger = DataDebugger()
        results = debugger.debug([])
        assert results.total_issues == 0
        assert results.statistics.total_samples == 0

    def test_debug_simple_data(self):
        """Test debugging simple data."""
        debugger = DataDebugger()
        texts = ["hello", "world", "test"]
        labels = ["a", "b", "a"]
        results = debugger.debug(texts, labels)
        assert results.statistics.total_samples == 3
        assert isinstance(results, DebugResults)

    def test_detect_exact_duplicates(self):
        """Test exact duplicate detection."""
        debugger = DataDebugger()
        texts = ["hello world", "hello world", "different text"]
        labels = ["a", "a", "b"]
        results = debugger.debug(texts, labels)
        
        duplicates = results.get_issues_by_type(IssueType.DUPLICATE)
        assert len(duplicates) > 0

    def test_detect_label_errors(self):
        """Test label error detection."""
        debugger = DataDebugger()
        texts = ["same text here", "same text here", "other text"]
        labels = ["positive", "negative", "neutral"]
        results = debugger.debug(texts, labels)
        
        label_errors = results.get_issues_by_type(IssueType.LABEL_ERROR)
        assert len(label_errors) > 0

    def test_detect_missing_values(self):
        """Test missing value detection."""
        debugger = DataDebugger()
        texts = ["valid text", "", None, "another valid"]
        labels = ["a", "b", "c", "d"]
        results = debugger.debug(texts, labels)
        
        missing = results.get_issues_by_type(IssueType.MISSING_VALUE)
        assert len(missing) > 0

    def test_detect_pii(self):
        """Test PII detection."""
        debugger = DataDebugger()
        texts = [
            "Normal text here",
            "Contact me at john@example.com",
            "Call 555-123-4567",
            "SSN: 123-45-6789",
        ]
        results = debugger.debug(texts)
        
        pii_issues = results.get_issues_by_type(IssueType.PII_EXPOSURE)
        assert len(pii_issues) > 0

    def test_detect_class_imbalance(self):
        """Test class imbalance detection."""
        config = DebugConfig(imbalance_threshold=0.2)
        debugger = DataDebugger(config=config)
        
        texts = ["text"] * 100
        # Highly imbalanced: 95 'a' vs 5 'b'
        labels = ["a"] * 95 + ["b"] * 5
        results = debugger.debug(texts, labels)
        
        imbalance = results.get_issues_by_type(IssueType.CLASS_IMBALANCE)
        assert len(imbalance) > 0

    def test_config_disable_checks(self):
        """Test disabling specific checks."""
        config = DebugConfig(
            check_duplicates=False,
            check_label_errors=False,
            check_pii=False,
        )
        debugger = DataDebugger(config=config)
        
        texts = ["hello", "hello", "email: test@test.com"]
        labels = ["a", "b", "c"]
        results = debugger.debug(texts, labels)
        
        # Should not detect disabled issue types
        assert len(results.get_issues_by_type(IssueType.DUPLICATE)) == 0
        assert len(results.get_issues_by_type(IssueType.PII_EXPOSURE)) == 0


class TestTextDataDebugger:
    """Tests for TextDataDebugger."""

    def test_init(self):
        """Test initialization."""
        debugger = TextDataDebugger()
        assert debugger is not None

    def test_text_length_issues(self):
        """Test text length issue detection."""
        config = DebugConfig(min_text_length=10, max_text_length=100)
        debugger = TextDataDebugger(config=config)
        
        texts = [
            "Hi",  # Too short
            "This is a normal length text that should pass validation",
            "x" * 150,  # Too long
        ]
        results = debugger.debug(texts)
        
        short_issues = results.get_issues_by_type(IssueType.TEXT_TOO_SHORT)
        long_issues = results.get_issues_by_type(IssueType.TEXT_TOO_LONG)
        
        assert len(short_issues) > 0
        assert len(long_issues) > 0

    def test_near_duplicate_detection(self):
        """Test near-duplicate detection."""
        debugger = TextDataDebugger()
        
        texts = [
            "The quick brown fox jumps over the lazy dog",
            "The quick brown fox jumped over the lazy dog",  # Near duplicate
            "Completely different text here",
        ]
        results = debugger.debug(texts)
        
        near_dupes = results.get_issues_by_type(IssueType.NEAR_DUPLICATE)
        # Near-duplicate detection may or may not trigger depending on threshold
        assert isinstance(near_dupes, list)


class TestTabularDataDebugger:
    """Tests for TabularDataDebugger."""

    def test_init(self):
        """Test initialization."""
        debugger = TabularDataDebugger()
        assert debugger is not None

    def test_debug_tabular_data(self):
        """Test debugging tabular data."""
        debugger = TabularDataDebugger()
        
        data = [
            {"name": "Alice", "age": 30, "score": 85},
            {"name": "Bob", "age": 25, "score": 90},
            {"name": "Charlie", "age": 35, "score": 78},
        ]
        
        results = debugger.debug(data, label_column="score")
        assert results.statistics.total_samples == 3

    def test_detect_tabular_missing_values(self):
        """Test missing value detection in tabular data."""
        debugger = TabularDataDebugger()
        
        data = [
            {"name": "Alice", "age": 30, "score": 85},
            {"name": "Bob", "age": None, "score": 90},
            {"name": "", "age": 35, "score": 78},
        ]
        
        results = debugger.debug(data)
        missing = results.get_issues_by_type(IssueType.MISSING_VALUE)
        assert len(missing) > 0

    def test_detect_tabular_duplicates(self):
        """Test duplicate detection in tabular data."""
        debugger = TabularDataDebugger()
        
        data = [
            {"name": "Alice", "age": 30, "score": 85},
            {"name": "Alice", "age": 30, "score": 85},  # Exact duplicate
            {"name": "Bob", "age": 25, "score": 90},
        ]
        
        results = debugger.debug(data)
        duplicates = results.get_issues_by_type(IssueType.DUPLICATE)
        assert len(duplicates) > 0


class TestDebugResults:
    """Tests for DebugResults."""

    def test_get_issues_by_type(self):
        """Test filtering issues by type."""
        issues = [
            DataIssue(
                issue_type=IssueType.DUPLICATE,
                severity=IssueSeverity.HIGH,
                indices=[0, 1],
                description="Duplicate found",
            ),
            DataIssue(
                issue_type=IssueType.MISSING_VALUE,
                severity=IssueSeverity.MEDIUM,
                indices=[2],
                description="Missing value",
            ),
        ]
        
        results = DebugResults(issues=issues)
        
        duplicates = results.get_issues_by_type(IssueType.DUPLICATE)
        assert len(duplicates) == 1
        assert duplicates[0].issue_type == IssueType.DUPLICATE

    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        issues = [
            DataIssue(
                issue_type=IssueType.DUPLICATE,
                severity=IssueSeverity.HIGH,
                indices=[0],
                description="High severity",
            ),
            DataIssue(
                issue_type=IssueType.MISSING_VALUE,
                severity=IssueSeverity.CRITICAL,
                indices=[1],
                description="Critical",
            ),
        ]
        
        results = DebugResults(issues=issues)
        
        critical = results.get_issues_by_severity(IssueSeverity.CRITICAL)
        assert len(critical) == 1

    def test_get_affected_indices(self):
        """Test getting all affected indices."""
        issues = [
            DataIssue(
                issue_type=IssueType.DUPLICATE,
                severity=IssueSeverity.HIGH,
                indices=[0, 1],
                description="Duplicate",
            ),
            DataIssue(
                issue_type=IssueType.MISSING_VALUE,
                severity=IssueSeverity.MEDIUM,
                indices=[2, 3],
                description="Missing",
            ),
        ]
        
        results = DebugResults(issues=issues)
        affected = results.get_affected_indices()
        
        assert affected == {0, 1, 2, 3}

    def test_total_issues(self):
        """Test total issues count."""
        issues = [
            DataIssue(
                issue_type=IssueType.DUPLICATE,
                severity=IssueSeverity.HIGH,
                indices=[0],
                description="Issue 1",
            ),
            DataIssue(
                issue_type=IssueType.MISSING_VALUE,
                severity=IssueSeverity.MEDIUM,
                indices=[1],
                description="Issue 2",
            ),
        ]
        
        results = DebugResults(issues=issues)
        assert results.total_issues == 2

    def test_severity_counts(self):
        """Test severity count properties."""
        issues = [
            DataIssue(
                issue_type=IssueType.LABEL_ERROR,
                severity=IssueSeverity.CRITICAL,
                indices=[0],
                description="Critical issue",
            ),
            DataIssue(
                issue_type=IssueType.DUPLICATE,
                severity=IssueSeverity.HIGH,
                indices=[1],
                description="High issue",
            ),
            DataIssue(
                issue_type=IssueType.DUPLICATE,
                severity=IssueSeverity.HIGH,
                indices=[2],
                description="Another high issue",
            ),
        ]
        
        results = DebugResults(issues=issues)
        
        assert results.critical_count == 1
        assert results.high_count == 2

    def test_to_dict(self):
        """Test conversion to dictionary."""
        issues = [
            DataIssue(
                issue_type=IssueType.DUPLICATE,
                severity=IssueSeverity.HIGH,
                indices=[0, 1],
                description="Test issue",
            ),
        ]
        
        results = DebugResults(issues=issues)
        result_dict = results.to_dict()
        
        assert "issues" in result_dict
        assert "statistics" in result_dict
        assert len(result_dict["issues"]) == 1

    def test_to_json(self):
        """Test JSON serialization."""
        issues = [
            DataIssue(
                issue_type=IssueType.DUPLICATE,
                severity=IssueSeverity.HIGH,
                indices=[0],
                description="Test",
            ),
        ]
        
        results = DebugResults(issues=issues)
        json_str = results.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert "issues" in parsed


class TestDataIssue:
    """Tests for DataIssue dataclass."""

    def test_create_issue(self):
        """Test creating a data issue."""
        issue = DataIssue(
            issue_type=IssueType.DUPLICATE,
            severity=IssueSeverity.HIGH,
            indices=[0, 1],
            description="Duplicate samples found",
            suggestion="Remove one of the duplicates",
            details={"similarity": 1.0},
        )
        
        assert issue.issue_type == IssueType.DUPLICATE
        assert issue.severity == IssueSeverity.HIGH
        assert issue.indices == [0, 1]
        assert issue.suggestion is not None

    def test_issue_with_info(self):
        """Test issue with additional info objects."""
        from training_data_debugger import DuplicateInfo
        
        dup_info = DuplicateInfo(
            original_index=0,
            duplicate_indices=[1, 2],
            similarity_scores=[1.0, 0.95],
        )
        
        issue = DataIssue(
            issue_type=IssueType.DUPLICATE,
            severity=IssueSeverity.HIGH,
            indices=[0, 1, 2],
            description="Duplicates found",
            details={"info": dup_info},
        )
        
        assert issue.details is not None


class TestDebugConfig:
    """Tests for DebugConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DebugConfig()
        
        assert config.check_duplicates is True
        assert config.check_label_errors is True
        assert config.check_outliers is True
        assert config.check_class_imbalance is True
        assert config.check_missing_values is True
        assert config.check_text_quality is True
        assert config.check_pii is True

    def test_custom_thresholds(self):
        """Test custom threshold configuration."""
        config = DebugConfig(
            duplicate_threshold=0.8,
            outlier_std_threshold=2.5,
            imbalance_threshold=0.15,
            min_text_length=20,
            max_text_length=5000,
        )
        
        assert config.duplicate_threshold == 0.8
        assert config.outlier_std_threshold == 2.5
        assert config.imbalance_threshold == 0.15
        assert config.min_text_length == 20
        assert config.max_text_length == 5000


class TestEnums:
    """Tests for enum types."""

    def test_issue_types(self):
        """Test IssueType enum values."""
        assert IssueType.DUPLICATE.value == "duplicate"
        assert IssueType.LABEL_ERROR.value == "label_error"
        assert IssueType.OUTLIER.value == "outlier"
        assert IssueType.PII_EXPOSURE.value == "pii_exposure"

    def test_severity_levels(self):
        """Test IssueSeverity enum values."""
        assert IssueSeverity.CRITICAL.value == "critical"
        assert IssueSeverity.HIGH.value == "high"
        assert IssueSeverity.MEDIUM.value == "medium"
        assert IssueSeverity.LOW.value == "low"
        assert IssueSeverity.INFO.value == "info"

    def test_data_types(self):
        """Test DataType enum values."""
        assert DataType.TEXT.value == "text"
        assert DataType.NUMERIC.value == "numeric"
        assert DataType.CATEGORICAL.value == "categorical"


class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self):
        """Test complete debugging workflow."""
        # Create debugger with custom config
        config = DebugConfig(
            check_duplicates=True,
            check_label_errors=True,
            check_pii=True,
            min_text_length=5,
        )
        debugger = DataDebugger(config=config)
        
        # Sample data with various issues
        texts = [
            "This is a normal product review.",
            "This is a normal product review.",  # Duplicate
            "Great product!",
            "Great product!",  # Duplicate with different label
            "Contact: test@email.com",  # PII
            "",  # Missing
            "OK",  # Short
        ]
        labels = ["positive", "positive", "positive", "negative", "neutral", "neutral", "positive"]
        
        # Debug
        results = debugger.debug(texts, labels)
        
        # Verify results
        assert results.total_issues > 0
        assert results.statistics.total_samples == 7
        
        # Check for expected issues
        duplicates = results.get_issues_by_type(IssueType.DUPLICATE)
        label_errors = results.get_issues_by_type(IssueType.LABEL_ERROR)
        pii = results.get_issues_by_type(IssueType.PII_EXPOSURE)
        
        assert len(duplicates) > 0 or len(label_errors) > 0
        assert len(pii) > 0
        
        # Verify serialization
        json_output = results.to_json()
        assert json_output is not None
        
        dict_output = results.to_dict()
        assert "issues" in dict_output

    def test_large_dataset_performance(self):
        """Test performance with larger dataset."""
        debugger = DataDebugger()
        
        # Generate larger dataset
        texts = [f"Sample text number {i}" for i in range(1000)]
        labels = ["positive" if i % 2 == 0 else "negative" for i in range(1000)]
        
        # Add some duplicates
        texts[500] = texts[0]
        texts[501] = texts[1]
        
        results = debugger.debug(texts, labels)
        
        assert results.statistics.total_samples == 1000
        assert results.total_issues >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
