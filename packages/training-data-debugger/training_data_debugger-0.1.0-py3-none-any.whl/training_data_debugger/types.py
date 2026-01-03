"""Type definitions for training-data-debugger package."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime
import uuid


class IssueType(Enum):
    """Types of data quality issues."""
    DUPLICATE = "duplicate"
    NEAR_DUPLICATE = "near_duplicate"
    LABEL_ERROR = "label_error"
    LABEL_INCONSISTENCY = "label_inconsistency"
    MISSING_VALUE = "missing_value"
    OUTLIER = "outlier"
    CLASS_IMBALANCE = "class_imbalance"
    DATA_LEAKAGE = "data_leakage"
    NOISY_LABEL = "noisy_label"
    AMBIGUOUS_SAMPLE = "ambiguous_sample"
    CORRUPTED_DATA = "corrupted_data"
    FORMAT_ERROR = "format_error"
    ENCODING_ERROR = "encoding_error"
    LENGTH_ANOMALY = "length_anomaly"
    DISTRIBUTION_SHIFT = "distribution_shift"
    BIAS = "bias"
    TOXIC_CONTENT = "toxic_content"
    PII_EXPOSURE = "pii_exposure"


class Severity(Enum):
    """Severity levels for issues."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataType(Enum):
    """Types of data being analyzed."""
    TEXT = "text"
    IMAGE = "image"
    TABULAR = "tabular"
    AUDIO = "audio"
    TIME_SERIES = "time_series"
    MULTIMODAL = "multimodal"


@dataclass
class DataIssue:
    """Represents a detected data quality issue."""
    issue_type: IssueType
    severity: Severity
    description: str
    affected_indices: List[int]
    confidence: float
    suggestion: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    issue_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def affected_count(self) -> int:
        """Number of affected samples."""
        return len(self.affected_indices)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "issue_id": self.issue_id,
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "affected_indices": self.affected_indices,
            "affected_count": self.affected_count,
            "confidence": self.confidence,
            "suggestion": self.suggestion,
            "metadata": self.metadata,
        }


@dataclass
class DataSample:
    """Represents a single data sample."""
    index: int
    content: Any
    label: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    predicted_label: Optional[Any] = None
    confidence_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "index": self.index,
            "content": self.content,
            "label": self.label,
            "metadata": self.metadata,
            "predicted_label": self.predicted_label,
            "confidence_score": self.confidence_score,
        }


@dataclass
class LabelAnalysis:
    """Analysis of label quality."""
    total_samples: int
    unique_labels: int
    label_distribution: Dict[Any, int]
    potential_errors: List[Tuple[int, Any, Any, float]]  # (idx, current, suggested, conf)
    inconsistencies: List[Tuple[List[int], str]]  # (indices, description)
    noise_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_samples": self.total_samples,
            "unique_labels": self.unique_labels,
            "label_distribution": {str(k): v for k, v in self.label_distribution.items()},
            "potential_errors_count": len(self.potential_errors),
            "inconsistencies_count": len(self.inconsistencies),
            "noise_rate": self.noise_rate,
        }


@dataclass
class DuplicateGroup:
    """Group of duplicate or near-duplicate samples."""
    indices: List[int]
    similarity_scores: List[float]
    is_exact: bool
    representative_index: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "indices": self.indices,
            "similarity_scores": self.similarity_scores,
            "is_exact": self.is_exact,
            "representative_index": self.representative_index,
            "count": len(self.indices),
        }


@dataclass
class OutlierResult:
    """Result of outlier detection."""
    outlier_indices: List[int]
    outlier_scores: List[float]
    threshold: float
    method: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "outlier_indices": self.outlier_indices,
            "outlier_scores": self.outlier_scores,
            "threshold": self.threshold,
            "method": self.method,
            "count": len(self.outlier_indices),
        }


@dataclass
class ClassBalance:
    """Class balance analysis."""
    label_counts: Dict[Any, int]
    label_ratios: Dict[Any, float]
    imbalance_ratio: float
    minority_classes: List[Any]
    majority_classes: List[Any]
    suggested_weights: Dict[Any, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "label_counts": {str(k): v for k, v in self.label_counts.items()},
            "label_ratios": {str(k): v for k, v in self.label_ratios.items()},
            "imbalance_ratio": self.imbalance_ratio,
            "minority_classes": [str(c) for c in self.minority_classes],
            "majority_classes": [str(c) for c in self.majority_classes],
            "suggested_weights": {str(k): v for k, v in self.suggested_weights.items()},
        }


@dataclass
class DatasetStats:
    """Statistics about the dataset."""
    total_samples: int
    data_type: DataType
    features: List[str]
    label_column: Optional[str]
    missing_counts: Dict[str, int]
    unique_counts: Dict[str, int]
    numeric_stats: Dict[str, Dict[str, float]]
    text_stats: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_samples": self.total_samples,
            "data_type": self.data_type.value,
            "features": self.features,
            "label_column": self.label_column,
            "missing_counts": self.missing_counts,
            "unique_counts": self.unique_counts,
            "numeric_stats": self.numeric_stats,
            "text_stats": self.text_stats,
        }


@dataclass 
class DebugReport:
    """Complete debug report for a dataset."""
    dataset_stats: DatasetStats
    issues: List[DataIssue]
    label_analysis: Optional[LabelAnalysis]
    duplicate_groups: List[DuplicateGroup]
    outlier_result: Optional[OutlierResult]
    class_balance: Optional[ClassBalance]
    processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    @property
    def total_issues(self) -> int:
        """Total number of issues."""
        return len(self.issues)
    
    @property
    def critical_issues(self) -> List[DataIssue]:
        """Get critical issues."""
        return [i for i in self.issues if i.severity == Severity.CRITICAL]
    
    @property
    def high_issues(self) -> List[DataIssue]:
        """Get high severity issues."""
        return [i for i in self.issues if i.severity == Severity.HIGH]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp.isoformat(),
            "processing_time_ms": self.processing_time_ms,
            "dataset_stats": self.dataset_stats.to_dict(),
            "total_issues": self.total_issues,
            "issues": [i.to_dict() for i in self.issues],
            "label_analysis": self.label_analysis.to_dict() if self.label_analysis else None,
            "duplicate_groups": [d.to_dict() for d in self.duplicate_groups],
            "outlier_result": self.outlier_result.to_dict() if self.outlier_result else None,
            "class_balance": self.class_balance.to_dict() if self.class_balance else None,
        }


@dataclass
class DebugConfig:
    """Configuration for data debugging."""
    # Detection toggles
    detect_duplicates: bool = True
    detect_label_errors: bool = True
    detect_outliers: bool = True
    detect_class_imbalance: bool = True
    detect_missing_values: bool = True
    detect_data_leakage: bool = False
    detect_pii: bool = False
    detect_toxicity: bool = False
    
    # Thresholds
    duplicate_threshold: float = 0.95
    near_duplicate_threshold: float = 0.85
    outlier_threshold: float = 3.0
    imbalance_threshold: float = 0.1
    label_error_confidence: float = 0.7
    
    # Text-specific
    min_text_length: int = 1
    max_text_length: int = 100000
    
    # Performance
    sample_size: Optional[int] = None
    n_jobs: int = -1
    batch_size: int = 1000
    
    # Output
    max_issues_per_type: int = 1000
    include_suggestions: bool = True
