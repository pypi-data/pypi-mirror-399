"""Main data debugger for training data quality analysis."""

import time
import hashlib
from collections import Counter, defaultdict
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
import re

from .types import (
    IssueType,
    Severity,
    DataType,
    DataIssue,
    DataSample,
    LabelAnalysis,
    DuplicateGroup,
    OutlierResult,
    ClassBalance,
    DatasetStats,
    DebugReport,
    DebugConfig,
)


class DataDebugger:
    """
    Main data debugger for training data quality analysis.
    
    Example:
        >>> debugger = DataDebugger()
        >>> report = debugger.debug(texts, labels)
        >>> print(f"Found {report.total_issues} issues")
        >>> for issue in report.critical_issues:
        ...     print(f"  {issue.description}")
    """
    
    def __init__(self, config: Optional[DebugConfig] = None):
        """
        Initialize data debugger.
        
        Args:
            config: Optional configuration
        """
        self.config = config or DebugConfig()
    
    def debug(
        self,
        data: Union[List[str], List[Dict], Any],
        labels: Optional[List[Any]] = None,
        label_column: Optional[str] = None,
    ) -> DebugReport:
        """
        Debug training data for quality issues.
        
        Args:
            data: List of samples (texts, dicts) or DataFrame-like object
            labels: Optional list of labels
            label_column: Column name for labels if data is dict/DataFrame
            
        Returns:
            DebugReport with all findings
        """
        start_time = time.time()
        issues: List[DataIssue] = []
        
        # Convert data to standard format
        samples, labels_list, data_type = self._prepare_data(data, labels, label_column)
        
        # Compute dataset statistics
        stats = self._compute_stats(samples, labels_list, data_type, label_column)
        
        # Sample if needed
        if self.config.sample_size and len(samples) > self.config.sample_size:
            import random
            indices = random.sample(range(len(samples)), self.config.sample_size)
            samples = [samples[i] for i in indices]
            if labels_list:
                labels_list = [labels_list[i] for i in indices]
        
        # Detect duplicates
        duplicate_groups = []
        if self.config.detect_duplicates:
            duplicate_groups, dup_issues = self._detect_duplicates(samples, data_type)
            issues.extend(dup_issues)
        
        # Detect label errors
        label_analysis = None
        if self.config.detect_label_errors and labels_list:
            label_analysis, label_issues = self._analyze_labels(samples, labels_list, data_type)
            issues.extend(label_issues)
        
        # Detect outliers
        outlier_result = None
        if self.config.detect_outliers:
            outlier_result, outlier_issues = self._detect_outliers(samples, data_type)
            issues.extend(outlier_issues)
        
        # Analyze class balance
        class_balance = None
        if self.config.detect_class_imbalance and labels_list:
            class_balance, balance_issues = self._analyze_class_balance(labels_list)
            issues.extend(balance_issues)
        
        # Detect missing values
        if self.config.detect_missing_values:
            missing_issues = self._detect_missing_values(samples, data_type)
            issues.extend(missing_issues)
        
        # Text-specific checks
        if data_type == DataType.TEXT:
            text_issues = self._check_text_quality(samples)
            issues.extend(text_issues)
        
        # Detect PII if enabled
        if self.config.detect_pii and data_type == DataType.TEXT:
            pii_issues = self._detect_pii(samples)
            issues.extend(pii_issues)
        
        processing_time = (time.time() - start_time) * 1000
        
        return DebugReport(
            dataset_stats=stats,
            issues=issues,
            label_analysis=label_analysis,
            duplicate_groups=duplicate_groups,
            outlier_result=outlier_result,
            class_balance=class_balance,
            processing_time_ms=processing_time,
        )
    
    def _prepare_data(
        self,
        data: Union[List[str], List[Dict], Any],
        labels: Optional[List[Any]],
        label_column: Optional[str],
    ) -> Tuple[List[Any], Optional[List[Any]], DataType]:
        """Prepare data for analysis."""
        # Determine data type
        if isinstance(data, list):
            if len(data) == 0:
                return [], labels, DataType.TEXT
            
            if isinstance(data[0], str):
                return data, labels, DataType.TEXT
            elif isinstance(data[0], dict):
                samples = data
                if label_column and labels is None:
                    labels = [d.get(label_column) for d in data]
                return samples, labels, DataType.TABULAR
            else:
                return data, labels, DataType.TABULAR
        
        # Handle DataFrame-like objects
        try:
            # Try pandas DataFrame
            samples = data.to_dict('records')
            if label_column and labels is None:
                labels = data[label_column].tolist()
            return samples, labels, DataType.TABULAR
        except:
            pass
        
        return list(data), labels, DataType.TEXT
    
    def _compute_stats(
        self,
        samples: List[Any],
        labels: Optional[List[Any]],
        data_type: DataType,
        label_column: Optional[str],
    ) -> DatasetStats:
        """Compute dataset statistics."""
        total = len(samples)
        features = []
        missing_counts = {}
        unique_counts = {}
        numeric_stats = {}
        text_stats = None
        
        if data_type == DataType.TEXT:
            # Text statistics
            lengths = [len(s) if isinstance(s, str) else 0 for s in samples]
            word_counts = [len(s.split()) if isinstance(s, str) else 0 for s in samples]
            
            text_stats = {
                "avg_length": sum(lengths) / len(lengths) if lengths else 0,
                "min_length": min(lengths) if lengths else 0,
                "max_length": max(lengths) if lengths else 0,
                "avg_words": sum(word_counts) / len(word_counts) if word_counts else 0,
                "empty_count": sum(1 for s in samples if not s or (isinstance(s, str) and not s.strip())),
            }
            features = ["text"]
            missing_counts = {"text": text_stats["empty_count"]}
            unique_counts = {"text": len(set(samples))}
            
        elif data_type == DataType.TABULAR and samples and isinstance(samples[0], dict):
            # Tabular statistics
            features = list(samples[0].keys())
            
            for feat in features:
                values = [s.get(feat) for s in samples]
                missing = sum(1 for v in values if v is None or v == "")
                missing_counts[feat] = missing
                unique_counts[feat] = len(set(v for v in values if v is not None))
                
                # Numeric stats if applicable
                numeric_values = []
                for v in values:
                    try:
                        numeric_values.append(float(v))
                    except (TypeError, ValueError):
                        pass
                
                if len(numeric_values) > len(values) * 0.5:  # Mostly numeric
                    numeric_stats[feat] = {
                        "mean": sum(numeric_values) / len(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                    }
        
        return DatasetStats(
            total_samples=total,
            data_type=data_type,
            features=features,
            label_column=label_column,
            missing_counts=missing_counts,
            unique_counts=unique_counts,
            numeric_stats=numeric_stats,
            text_stats=text_stats,
        )
    
    def _detect_duplicates(
        self,
        samples: List[Any],
        data_type: DataType,
    ) -> Tuple[List[DuplicateGroup], List[DataIssue]]:
        """Detect duplicate and near-duplicate samples."""
        groups = []
        issues = []
        
        # Hash-based exact duplicate detection
        hash_to_indices: Dict[str, List[int]] = defaultdict(list)
        
        for idx, sample in enumerate(samples):
            if data_type == DataType.TEXT:
                content = sample if isinstance(sample, str) else str(sample)
            else:
                content = str(sample)
            
            hash_val = hashlib.md5(content.encode()).hexdigest()
            hash_to_indices[hash_val].append(idx)
        
        # Find exact duplicates
        exact_dup_indices = set()
        for hash_val, indices in hash_to_indices.items():
            if len(indices) > 1:
                groups.append(DuplicateGroup(
                    indices=indices,
                    similarity_scores=[1.0] * len(indices),
                    is_exact=True,
                    representative_index=indices[0],
                ))
                exact_dup_indices.update(indices[1:])  # All except first
        
        if exact_dup_indices:
            issues.append(DataIssue(
                issue_type=IssueType.DUPLICATE,
                severity=Severity.HIGH,
                description=f"Found {len(exact_dup_indices)} exact duplicate samples",
                affected_indices=list(exact_dup_indices),
                confidence=1.0,
                suggestion="Remove duplicate samples to prevent data leakage and inflated metrics",
            ))
        
        # Near-duplicate detection for text (using n-gram similarity)
        if data_type == DataType.TEXT and self.config.near_duplicate_threshold < 1.0:
            near_dups = self._find_near_duplicates_text(samples)
            
            if near_dups:
                for group_indices, similarities in near_dups:
                    if group_indices[0] not in exact_dup_indices:
                        groups.append(DuplicateGroup(
                            indices=group_indices,
                            similarity_scores=similarities,
                            is_exact=False,
                            representative_index=group_indices[0],
                        ))
                
                all_near_dup_indices = set()
                for group_indices, _ in near_dups:
                    all_near_dup_indices.update(group_indices[1:])
                
                if all_near_dup_indices:
                    issues.append(DataIssue(
                        issue_type=IssueType.NEAR_DUPLICATE,
                        severity=Severity.MEDIUM,
                        description=f"Found {len(all_near_dup_indices)} near-duplicate samples",
                        affected_indices=list(all_near_dup_indices)[:self.config.max_issues_per_type],
                        confidence=0.85,
                        suggestion="Review near-duplicates - they may be valid variations or redundant data",
                    ))
        
        return groups, issues
    
    def _find_near_duplicates_text(
        self,
        samples: List[str],
        n: int = 3,
    ) -> List[Tuple[List[int], List[float]]]:
        """Find near-duplicates using n-gram similarity."""
        def get_ngrams(text: str, n: int) -> Set[str]:
            text = text.lower()
            return set(text[i:i+n] for i in range(len(text) - n + 1))
        
        def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
            if not set1 or not set2:
                return 0.0
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            return intersection / union if union > 0 else 0.0
        
        # Only check subset for performance
        max_samples = min(len(samples), 5000)
        
        ngrams = []
        for i in range(max_samples):
            sample = samples[i] if isinstance(samples[i], str) else str(samples[i])
            ngrams.append(get_ngrams(sample, n))
        
        near_dups = []
        seen = set()
        
        for i in range(max_samples):
            if i in seen:
                continue
            
            group = [i]
            sims = [1.0]
            
            for j in range(i + 1, max_samples):
                if j in seen:
                    continue
                
                sim = jaccard_similarity(ngrams[i], ngrams[j])
                if sim >= self.config.near_duplicate_threshold:
                    group.append(j)
                    sims.append(sim)
                    seen.add(j)
            
            if len(group) > 1:
                near_dups.append((group, sims))
                seen.add(i)
        
        return near_dups
    
    def _analyze_labels(
        self,
        samples: List[Any],
        labels: List[Any],
        data_type: DataType,
    ) -> Tuple[LabelAnalysis, List[DataIssue]]:
        """Analyze label quality."""
        issues = []
        
        # Basic label statistics
        label_counts = Counter(labels)
        unique_labels = len(label_counts)
        total = len(labels)
        
        # Find potential label errors using heuristics
        potential_errors = []
        inconsistencies = []
        
        if data_type == DataType.TEXT:
            # Group similar texts and check for label consistency
            content_to_indices: Dict[str, List[int]] = defaultdict(list)
            
            for idx, sample in enumerate(samples):
                # Normalize text
                if isinstance(sample, str):
                    normalized = sample.lower().strip()
                    content_to_indices[normalized].append(idx)
            
            # Check for same content with different labels
            for content, indices in content_to_indices.items():
                if len(indices) > 1:
                    idx_labels = [labels[i] for i in indices]
                    if len(set(idx_labels)) > 1:
                        # Same content, different labels
                        most_common = Counter(idx_labels).most_common(1)[0][0]
                        for idx in indices:
                            if labels[idx] != most_common:
                                potential_errors.append((
                                    idx,
                                    labels[idx],
                                    most_common,
                                    0.8,
                                ))
                        inconsistencies.append((
                            indices,
                            f"Same content with different labels: {set(idx_labels)}"
                        ))
        
        # Estimate noise rate
        noise_rate = len(potential_errors) / total if total > 0 else 0.0
        
        label_analysis = LabelAnalysis(
            total_samples=total,
            unique_labels=unique_labels,
            label_distribution=dict(label_counts),
            potential_errors=potential_errors,
            inconsistencies=inconsistencies,
            noise_rate=noise_rate,
        )
        
        # Create issues
        if potential_errors:
            issues.append(DataIssue(
                issue_type=IssueType.LABEL_ERROR,
                severity=Severity.HIGH,
                description=f"Found {len(potential_errors)} potential label errors",
                affected_indices=[e[0] for e in potential_errors][:self.config.max_issues_per_type],
                confidence=0.75,
                suggestion="Review these samples - same content has different labels elsewhere",
                metadata={"errors": potential_errors[:100]},
            ))
        
        if inconsistencies:
            issues.append(DataIssue(
                issue_type=IssueType.LABEL_INCONSISTENCY,
                severity=Severity.MEDIUM,
                description=f"Found {len(inconsistencies)} label inconsistencies",
                affected_indices=[idx for group, _ in inconsistencies for idx in group][:self.config.max_issues_per_type],
                confidence=0.7,
                suggestion="Identical or very similar samples have different labels",
            ))
        
        return label_analysis, issues
    
    def _detect_outliers(
        self,
        samples: List[Any],
        data_type: DataType,
    ) -> Tuple[Optional[OutlierResult], List[DataIssue]]:
        """Detect outliers in the data."""
        issues = []
        
        if data_type == DataType.TEXT:
            # Use text length as a simple feature
            lengths = []
            for s in samples:
                if isinstance(s, str):
                    lengths.append(len(s))
                else:
                    lengths.append(len(str(s)))
            
            if not lengths:
                return None, issues
            
            # Z-score based outlier detection
            mean_len = sum(lengths) / len(lengths)
            variance = sum((x - mean_len) ** 2 for x in lengths) / len(lengths)
            std_len = variance ** 0.5 if variance > 0 else 1
            
            outlier_indices = []
            outlier_scores = []
            
            for idx, length in enumerate(lengths):
                z_score = abs(length - mean_len) / std_len if std_len > 0 else 0
                if z_score > self.config.outlier_threshold:
                    outlier_indices.append(idx)
                    outlier_scores.append(z_score)
            
            outlier_result = OutlierResult(
                outlier_indices=outlier_indices,
                outlier_scores=outlier_scores,
                threshold=self.config.outlier_threshold,
                method="z_score_length",
            )
            
            if outlier_indices:
                issues.append(DataIssue(
                    issue_type=IssueType.OUTLIER,
                    severity=Severity.LOW,
                    description=f"Found {len(outlier_indices)} length outliers",
                    affected_indices=outlier_indices[:self.config.max_issues_per_type],
                    confidence=0.7,
                    suggestion="Review outliers - may be data errors or legitimate edge cases",
                ))
            
            return outlier_result, issues
        
        return None, issues
    
    def _analyze_class_balance(
        self,
        labels: List[Any],
    ) -> Tuple[ClassBalance, List[DataIssue]]:
        """Analyze class balance."""
        issues = []
        
        label_counts = Counter(labels)
        total = len(labels)
        
        label_ratios = {k: v / total for k, v in label_counts.items()}
        
        counts = list(label_counts.values())
        max_count = max(counts)
        min_count = min(counts)
        imbalance_ratio = min_count / max_count if max_count > 0 else 1.0
        
        # Identify minority/majority classes
        threshold = total / len(label_counts) * 0.5  # Less than half of expected
        minority = [k for k, v in label_counts.items() if v < threshold]
        majority = [k for k, v in label_counts.items() if v > total / len(label_counts) * 1.5]
        
        # Compute suggested weights (inverse frequency)
        suggested_weights = {}
        for label, count in label_counts.items():
            suggested_weights[label] = total / (len(label_counts) * count)
        
        class_balance = ClassBalance(
            label_counts=dict(label_counts),
            label_ratios=label_ratios,
            imbalance_ratio=imbalance_ratio,
            minority_classes=minority,
            majority_classes=majority,
            suggested_weights=suggested_weights,
        )
        
        if imbalance_ratio < self.config.imbalance_threshold:
            issues.append(DataIssue(
                issue_type=IssueType.CLASS_IMBALANCE,
                severity=Severity.MEDIUM,
                description=f"Severe class imbalance detected (ratio: {imbalance_ratio:.3f})",
                affected_indices=[],
                confidence=0.95,
                suggestion=f"Consider oversampling minority classes {minority} or using class weights",
                metadata={"imbalance_ratio": imbalance_ratio, "minority": minority},
            ))
        
        return class_balance, issues
    
    def _detect_missing_values(
        self,
        samples: List[Any],
        data_type: DataType,
    ) -> List[DataIssue]:
        """Detect missing values."""
        issues = []
        missing_indices = []
        
        for idx, sample in enumerate(samples):
            if sample is None:
                missing_indices.append(idx)
            elif data_type == DataType.TEXT:
                if isinstance(sample, str) and not sample.strip():
                    missing_indices.append(idx)
            elif isinstance(sample, dict):
                if all(v is None or v == "" for v in sample.values()):
                    missing_indices.append(idx)
        
        if missing_indices:
            issues.append(DataIssue(
                issue_type=IssueType.MISSING_VALUE,
                severity=Severity.HIGH,
                description=f"Found {len(missing_indices)} samples with missing values",
                affected_indices=missing_indices[:self.config.max_issues_per_type],
                confidence=1.0,
                suggestion="Remove or impute missing values",
            ))
        
        return issues
    
    def _check_text_quality(self, samples: List[str]) -> List[DataIssue]:
        """Check text-specific quality issues."""
        issues = []
        
        too_short = []
        too_long = []
        encoding_issues = []
        
        for idx, sample in enumerate(samples):
            if not isinstance(sample, str):
                continue
            
            # Length checks
            if len(sample) < self.config.min_text_length:
                too_short.append(idx)
            if len(sample) > self.config.max_text_length:
                too_long.append(idx)
            
            # Encoding issues (control characters, etc.)
            if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', sample):
                encoding_issues.append(idx)
        
        if too_short:
            issues.append(DataIssue(
                issue_type=IssueType.LENGTH_ANOMALY,
                severity=Severity.LOW,
                description=f"Found {len(too_short)} samples below minimum length",
                affected_indices=too_short[:self.config.max_issues_per_type],
                confidence=1.0,
                suggestion=f"Review very short samples (< {self.config.min_text_length} chars)",
            ))
        
        if too_long:
            issues.append(DataIssue(
                issue_type=IssueType.LENGTH_ANOMALY,
                severity=Severity.LOW,
                description=f"Found {len(too_long)} samples above maximum length",
                affected_indices=too_long[:self.config.max_issues_per_type],
                confidence=1.0,
                suggestion=f"Review very long samples (> {self.config.max_text_length} chars)",
            ))
        
        if encoding_issues:
            issues.append(DataIssue(
                issue_type=IssueType.ENCODING_ERROR,
                severity=Severity.MEDIUM,
                description=f"Found {len(encoding_issues)} samples with encoding issues",
                affected_indices=encoding_issues[:self.config.max_issues_per_type],
                confidence=0.9,
                suggestion="Clean control characters from these samples",
            ))
        
        return issues
    
    def _detect_pii(self, samples: List[str]) -> List[DataIssue]:
        """Detect PII in text samples."""
        issues = []
        
        pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        }
        
        pii_indices = []
        
        for idx, sample in enumerate(samples):
            if not isinstance(sample, str):
                continue
            
            for pii_type, pattern in pii_patterns.items():
                if re.search(pattern, sample):
                    pii_indices.append(idx)
                    break
        
        if pii_indices:
            issues.append(DataIssue(
                issue_type=IssueType.PII_EXPOSURE,
                severity=Severity.CRITICAL,
                description=f"Found {len(pii_indices)} samples potentially containing PII",
                affected_indices=pii_indices[:self.config.max_issues_per_type],
                confidence=0.85,
                suggestion="Review and remove/anonymize PII before training",
            ))
        
        return issues


class TextDataDebugger(DataDebugger):
    """Specialized debugger for text data."""
    
    def debug_texts(
        self,
        texts: List[str],
        labels: Optional[List[Any]] = None,
    ) -> DebugReport:
        """Debug text training data."""
        return self.debug(texts, labels)


class TabularDataDebugger(DataDebugger):
    """Specialized debugger for tabular data."""
    
    def debug_dataframe(
        self,
        df: Any,
        label_column: Optional[str] = None,
    ) -> DebugReport:
        """Debug tabular training data from DataFrame."""
        return self.debug(df, label_column=label_column)
