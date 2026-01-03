"""
Core drift detection functionality.
"""

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import uuid

from .types import (
    DriftType,
    DriftSeverity,
    StatisticalTest,
    FeatureType,
    AlertLevel,
    DriftScore,
    FeatureDrift,
    PredictionDrift,
    PerformanceDrift,
    Alert,
    DriftConfig,
    ReferenceData,
    DriftReport,
    MonitoringWindow,
    DriftMetrics,
)


class StatisticalTests:
    """Statistical tests for drift detection (pure Python implementations)."""
    
    @staticmethod
    def ks_test(reference: List[float], current: List[float]) -> Tuple[float, float]:
        """
        Kolmogorov-Smirnov test for two samples.
        Returns (statistic, p_value).
        """
        if not reference or not current:
            return 0.0, 1.0
        
        # Sort both samples
        ref_sorted = sorted(reference)
        cur_sorted = sorted(current)
        
        n1, n2 = len(ref_sorted), len(cur_sorted)
        
        # Combine and sort all values
        all_values = sorted(set(ref_sorted + cur_sorted))
        
        # Calculate empirical CDFs
        max_diff = 0.0
        
        for val in all_values:
            # CDF for reference
            cdf1 = sum(1 for x in ref_sorted if x <= val) / n1
            # CDF for current
            cdf2 = sum(1 for x in cur_sorted if x <= val) / n2
            
            diff = abs(cdf1 - cdf2)
            if diff > max_diff:
                max_diff = diff
        
        # Approximate p-value using asymptotic formula
        en = math.sqrt(n1 * n2 / (n1 + n2))
        p_value = 2 * math.exp(-2 * (max_diff * en) ** 2)
        p_value = min(1.0, max(0.0, p_value))
        
        return max_diff, p_value
    
    @staticmethod
    def chi_square_test(reference: Dict[str, int], current: Dict[str, int]) -> Tuple[float, float]:
        """
        Chi-square test for categorical distributions.
        Returns (statistic, p_value).
        """
        all_categories = set(reference.keys()) | set(current.keys())
        
        if not all_categories:
            return 0.0, 1.0
        
        n_ref = sum(reference.values())
        n_cur = sum(current.values())
        
        if n_ref == 0 or n_cur == 0:
            return 0.0, 1.0
        
        chi2 = 0.0
        df = len(all_categories) - 1
        
        for cat in all_categories:
            obs_ref = reference.get(cat, 0)
            obs_cur = current.get(cat, 0)
            
            # Expected frequencies under null hypothesis
            total = obs_ref + obs_cur
            exp_ref = total * n_ref / (n_ref + n_cur)
            exp_cur = total * n_cur / (n_ref + n_cur)
            
            if exp_ref > 0:
                chi2 += (obs_ref - exp_ref) ** 2 / exp_ref
            if exp_cur > 0:
                chi2 += (obs_cur - exp_cur) ** 2 / exp_cur
        
        # Approximate p-value using chi-square distribution
        # Using simple approximation for p-value
        if df <= 0:
            return chi2, 1.0
        
        p_value = StatisticalTests._chi2_sf(chi2, df)
        return chi2, p_value
    
    @staticmethod
    def _chi2_sf(x: float, df: int) -> float:
        """Survival function for chi-square distribution (approximation)."""
        if x <= 0:
            return 1.0
        if df <= 0:
            return 0.0
        
        # Using Wilson-Hilferty approximation
        if df > 2:
            z = ((x / df) ** (1/3) - (1 - 2/(9*df))) / math.sqrt(2/(9*df))
            # Standard normal CDF approximation
            p = 0.5 * (1 + math.erf(-z / math.sqrt(2)))
            return max(0.0, min(1.0, p))
        
        # For small df, use simple approximation
        return math.exp(-x / 2)
    
    @staticmethod
    def psi(reference: List[float], current: List[float], buckets: int = 10) -> float:
        """
        Population Stability Index.
        Returns PSI score (no p-value).
        """
        if not reference or not current:
            return 0.0
        
        # Create bucket boundaries from reference
        ref_sorted = sorted(reference)
        n = len(ref_sorted)
        
        boundaries = []
        for i in range(1, buckets):
            idx = int(i * n / buckets)
            boundaries.append(ref_sorted[min(idx, n-1)])
        
        # Count samples in each bucket
        def get_bucket_counts(data: List[float]) -> List[int]:
            counts = [0] * buckets
            for val in data:
                bucket = 0
                for b_idx, boundary in enumerate(boundaries):
                    if val > boundary:
                        bucket = b_idx + 1
                counts[bucket] += 1
            return counts
        
        ref_counts = get_bucket_counts(reference)
        cur_counts = get_bucket_counts(current)
        
        n_ref = len(reference)
        n_cur = len(current)
        
        psi_value = 0.0
        for ref_c, cur_c in zip(ref_counts, cur_counts):
            ref_pct = max(ref_c / n_ref, 0.0001)
            cur_pct = max(cur_c / n_cur, 0.0001)
            psi_value += (cur_pct - ref_pct) * math.log(cur_pct / ref_pct)
        
        return psi_value
    
    @staticmethod
    def js_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
        """Jensen-Shannon divergence between two distributions."""
        all_keys = set(p.keys()) | set(q.keys())
        
        # Normalize distributions
        p_sum = sum(p.values()) or 1
        q_sum = sum(q.values()) or 1
        
        p_norm = {k: p.get(k, 0) / p_sum for k in all_keys}
        q_norm = {k: q.get(k, 0) / q_sum for k in all_keys}
        
        # Calculate midpoint distribution
        m = {k: (p_norm[k] + q_norm[k]) / 2 for k in all_keys}
        
        # KL divergences
        def kl_div(a: Dict[str, float], b: Dict[str, float]) -> float:
            kl = 0.0
            for k in all_keys:
                if a[k] > 0 and b[k] > 0:
                    kl += a[k] * math.log(a[k] / b[k])
            return kl
        
        js = (kl_div(p_norm, m) + kl_div(q_norm, m)) / 2
        return js
    
    @staticmethod
    def wasserstein_distance(reference: List[float], current: List[float]) -> float:
        """Wasserstein (Earth Mover's) distance between distributions."""
        if not reference or not current:
            return 0.0
        
        ref_sorted = sorted(reference)
        cur_sorted = sorted(current)
        
        # Create CDFs and calculate area between them
        all_values = sorted(set(ref_sorted + cur_sorted))
        
        distance = 0.0
        prev_val = all_values[0] if all_values else 0
        
        n_ref = len(ref_sorted)
        n_cur = len(cur_sorted)
        
        for val in all_values:
            cdf_ref = sum(1 for x in ref_sorted if x <= val) / n_ref
            cdf_cur = sum(1 for x in cur_sorted if x <= val) / n_cur
            
            distance += abs(cdf_ref - cdf_cur) * (val - prev_val)
            prev_val = val
        
        return distance


class DriftDetector:
    """
    Main class for detecting model drift.
    
    Example:
        >>> detector = DriftDetector()
        >>> detector.set_reference(reference_data)
        >>> report = detector.detect(current_data)
        >>> if report.overall_drift_detected:
        ...     print(f"Drift detected in {report.drift_count} features")
    """
    
    def __init__(self, config: Optional[DriftConfig] = None):
        """Initialize drift detector."""
        self.config = config or DriftConfig()
        self.reference: Optional[ReferenceData] = None
        self.metrics = DriftMetrics()
        self._alert_handlers: List[Callable[[Alert], None]] = []
        self._stats = StatisticalTests()
    
    def set_reference(
        self,
        data: Any,
        feature_names: Optional[List[str]] = None,
        predictions: Optional[Any] = None,
        labels: Optional[Any] = None,
    ) -> ReferenceData:
        """
        Set reference (baseline) data for drift comparison.
        
        Args:
            data: Reference data (list of dicts, 2D list, or compatible format)
            feature_names: Names of features
            predictions: Model predictions on reference data
            labels: True labels for reference data
            
        Returns:
            ReferenceData object
        """
        # Convert data to standard format
        processed_data, names = self._process_data(data, feature_names)
        
        # Detect feature types
        feature_types = {}
        for name in names:
            values = self._get_feature_values(processed_data, name, names)
            feature_types[name] = self._detect_feature_type(values)
        
        # Calculate statistics
        statistics = {}
        for name in names:
            values = self._get_feature_values(processed_data, name, names)
            statistics[name] = self._calculate_statistics(values, feature_types[name])
        
        self.reference = ReferenceData(
            data=processed_data,
            feature_names=names,
            feature_types=feature_types,
            statistics=statistics,
            predictions=predictions,
            labels=labels,
        )
        
        self.metrics.features_monitored = len(names)
        
        return self.reference
    
    def detect(
        self,
        data: Any,
        predictions: Optional[Any] = None,
        labels: Optional[Any] = None,
        feature_names: Optional[List[str]] = None,
    ) -> DriftReport:
        """
        Detect drift between reference and current data.
        
        Args:
            data: Current data to compare against reference
            predictions: Current model predictions
            labels: Current true labels
            feature_names: Feature names (if not provided, uses reference names)
            
        Returns:
            DriftReport with detection results
        """
        if self.reference is None:
            raise ValueError("Reference data not set. Call set_reference() first.")
        
        # Process current data
        names = feature_names or self.reference.feature_names
        processed_data, names = self._process_data(data, names)
        
        # Generate report ID
        report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now()
        
        # Detect feature drift
        feature_drifts = []
        for name in names:
            if self.config.features_to_ignore and name in self.config.features_to_ignore:
                continue
            if self.config.features_to_monitor and name not in self.config.features_to_monitor:
                continue
            
            drift = self._detect_feature_drift(processed_data, name, names)
            if drift:
                feature_drifts.append(drift)
        
        # Detect prediction drift
        prediction_drift = None
        if predictions is not None and self.reference.predictions is not None:
            prediction_drift = self._detect_prediction_drift(predictions)
        
        # Detect performance drift (if labels available)
        performance_drifts = []
        if labels is not None and self.reference.labels is not None:
            performance_drifts = self._detect_performance_drift(predictions, labels)
        
        # Determine overall drift status
        overall_drift = any(f.drift_score.is_drifted for f in feature_drifts)
        if prediction_drift and prediction_drift.drift_score.is_drifted:
            overall_drift = True
        if any(p.is_degraded for p in performance_drifts):
            overall_drift = True
        
        # Determine severity
        overall_severity = self._determine_overall_severity(
            feature_drifts, prediction_drift, performance_drifts
        )
        
        # Generate alerts
        alerts = []
        if self.config.enable_alerts and overall_drift:
            alerts = self._generate_alerts(
                feature_drifts, prediction_drift, performance_drifts, overall_severity
            )
        
        # Generate summary and recommendations
        summary = self._generate_summary(feature_drifts, prediction_drift, performance_drifts)
        recommendations = self._generate_recommendations(
            feature_drifts, prediction_drift, performance_drifts
        )
        
        # Create report
        report = DriftReport(
            report_id=report_id,
            timestamp=timestamp,
            reference_period=self.reference.created_at.isoformat(),
            current_period=timestamp.isoformat(),
            overall_drift_detected=overall_drift,
            overall_severity=overall_severity,
            feature_drifts=feature_drifts,
            prediction_drift=prediction_drift,
            performance_drifts=performance_drifts,
            alerts=alerts,
            summary=summary,
            recommendations=recommendations,
            metadata={
                "reference_samples": self.reference.sample_count,
                "current_samples": len(processed_data) if hasattr(processed_data, '__len__') else 0,
                "features_checked": len(feature_drifts),
            },
        )
        
        # Update metrics
        self._update_metrics(report)
        
        # Notify alert handlers
        for alert in alerts:
            for handler in self._alert_handlers:
                try:
                    handler(alert)
                except Exception:
                    pass
        
        return report
    
    def add_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """Add a callback for alerts."""
        self._alert_handlers.append(handler)
    
    def get_metrics(self) -> DriftMetrics:
        """Get aggregated drift metrics."""
        return self.metrics
    
    def _process_data(
        self, data: Any, feature_names: Optional[List[str]]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Convert data to list of dicts format."""
        if isinstance(data, list):
            if len(data) == 0:
                return [], feature_names or []
            
            if isinstance(data[0], dict):
                names = feature_names or list(data[0].keys())
                return data, names
            elif isinstance(data[0], (list, tuple)):
                names = feature_names or [f"feature_{i}" for i in range(len(data[0]))]
                return [dict(zip(names, row)) for row in data], names
        
        # Handle other formats
        try:
            if hasattr(data, 'to_dict'):
                records = data.to_dict(orient='records')
                names = feature_names or list(records[0].keys()) if records else []
                return records, names
        except Exception:
            pass
        
        return [], feature_names or []
    
    def _get_feature_values(
        self, data: List[Dict[str, Any]], feature_name: str, all_names: List[str]
    ) -> List[Any]:
        """Extract values for a specific feature."""
        values = []
        for row in data:
            if isinstance(row, dict):
                values.append(row.get(feature_name))
            elif isinstance(row, (list, tuple)):
                idx = all_names.index(feature_name) if feature_name in all_names else -1
                if 0 <= idx < len(row):
                    values.append(row[idx])
        return values
    
    def _detect_feature_type(self, values: List[Any]) -> FeatureType:
        """Detect the type of a feature from its values."""
        non_null = [v for v in values if v is not None]
        
        if not non_null:
            return FeatureType.UNKNOWN
        
        # Check if numeric
        numeric_count = 0
        for v in non_null[:100]:  # Sample first 100
            try:
                float(v)
                numeric_count += 1
            except (TypeError, ValueError):
                pass
        
        if numeric_count / len(non_null[:100]) > 0.9:
            # Check if binary
            unique = set(non_null)
            if len(unique) == 2:
                return FeatureType.BINARY
            return FeatureType.NUMERICAL
        
        # Check if datetime
        sample = str(non_null[0])
        if re.match(r'\d{4}-\d{2}-\d{2}', sample):
            return FeatureType.DATETIME
        
        # Check unique ratio for categorical
        unique_ratio = len(set(non_null)) / len(non_null)
        if unique_ratio < 0.5:
            return FeatureType.CATEGORICAL
        
        # Likely text
        if any(len(str(v)) > 50 for v in non_null[:10]):
            return FeatureType.TEXT
        
        return FeatureType.CATEGORICAL
    
    def _calculate_statistics(
        self, values: List[Any], feature_type: FeatureType
    ) -> Dict[str, Any]:
        """Calculate statistics for a feature."""
        non_null = [v for v in values if v is not None]
        
        stats = {
            "count": len(values),
            "null_count": len(values) - len(non_null),
            "null_rate": (len(values) - len(non_null)) / len(values) if values else 0,
        }
        
        if not non_null:
            return stats
        
        if feature_type in (FeatureType.NUMERICAL, FeatureType.BINARY):
            numeric_values = []
            for v in non_null:
                try:
                    numeric_values.append(float(v))
                except (TypeError, ValueError):
                    pass
            
            if numeric_values:
                stats["mean"] = sum(numeric_values) / len(numeric_values)
                stats["min"] = min(numeric_values)
                stats["max"] = max(numeric_values)
                
                # Standard deviation
                mean = stats["mean"]
                variance = sum((x - mean) ** 2 for x in numeric_values) / len(numeric_values)
                stats["std"] = math.sqrt(variance)
                
                # Percentiles (approximate)
                sorted_vals = sorted(numeric_values)
                n = len(sorted_vals)
                stats["p25"] = sorted_vals[int(n * 0.25)]
                stats["p50"] = sorted_vals[int(n * 0.50)]
                stats["p75"] = sorted_vals[int(n * 0.75)]
        
        elif feature_type == FeatureType.CATEGORICAL:
            counter = Counter(non_null)
            stats["unique_count"] = len(counter)
            stats["distribution"] = dict(counter.most_common(self.config.max_categories))
            stats["mode"] = counter.most_common(1)[0][0] if counter else None
        
        return stats
    
    def _detect_feature_drift(
        self, current_data: List[Dict[str, Any]], feature_name: str, all_names: List[str]
    ) -> Optional[FeatureDrift]:
        """Detect drift for a single feature."""
        if feature_name not in self.reference.feature_names:
            return None
        
        ref_values = self._get_feature_values(
            self.reference.data, feature_name, self.reference.feature_names
        )
        cur_values = self._get_feature_values(current_data, feature_name, all_names)
        
        # Filter nulls
        ref_non_null = [v for v in ref_values if v is not None]
        cur_non_null = [v for v in cur_values if v is not None]
        
        if len(ref_non_null) < self.config.min_samples_for_test:
            return None
        if len(cur_non_null) < self.config.min_samples_for_test:
            return None
        
        feature_type = self.reference.feature_types.get(feature_name, FeatureType.UNKNOWN)
        
        # Choose appropriate test
        if feature_type in (FeatureType.NUMERICAL, FeatureType.BINARY):
            drift_score = self._numerical_drift_test(ref_non_null, cur_non_null)
        elif feature_type == FeatureType.CATEGORICAL:
            drift_score = self._categorical_drift_test(ref_non_null, cur_non_null)
        else:
            drift_score = DriftScore(score=0.0, is_drifted=False)
        
        # Determine severity
        severity = self._score_to_severity(drift_score)
        
        # Get statistics
        ref_stats = self.reference.statistics.get(feature_name, {})
        cur_stats = self._calculate_statistics(cur_values, feature_type)
        
        # Generate description
        description = self._generate_feature_description(
            feature_name, drift_score, ref_stats, cur_stats
        )
        
        return FeatureDrift(
            feature_name=feature_name,
            feature_type=feature_type,
            drift_score=drift_score,
            severity=severity,
            reference_stats=ref_stats,
            current_stats=cur_stats,
            description=description,
            suggestion=self._generate_feature_suggestion(feature_name, drift_score, severity),
        )
    
    def _numerical_drift_test(
        self, reference: List[Any], current: List[Any]
    ) -> DriftScore:
        """Run drift test for numerical features."""
        ref_float = [float(v) for v in reference]
        cur_float = [float(v) for v in current]
        
        # KS test
        statistic, p_value = self._stats.ks_test(ref_float, cur_float)
        
        # Also calculate PSI
        psi_score = self._stats.psi(ref_float, cur_float)
        
        return DriftScore(
            score=statistic,
            p_value=p_value,
            test_used=StatisticalTest.KS_TEST,
            threshold=self.config.significance_level,
            details={"psi": psi_score},
        )
    
    def _categorical_drift_test(
        self, reference: List[Any], current: List[Any]
    ) -> DriftScore:
        """Run drift test for categorical features."""
        ref_counts = dict(Counter(reference))
        cur_counts = dict(Counter(current))
        
        # Chi-square test
        statistic, p_value = self._stats.chi_square_test(ref_counts, cur_counts)
        
        # Also calculate JS divergence
        js_div = self._stats.js_divergence(ref_counts, cur_counts)
        
        return DriftScore(
            score=statistic,
            p_value=p_value,
            test_used=StatisticalTest.CHI_SQUARE,
            threshold=self.config.significance_level,
            details={"js_divergence": js_div},
        )
    
    def _detect_prediction_drift(self, current_predictions: Any) -> PredictionDrift:
        """Detect drift in model predictions."""
        ref_preds = list(self.reference.predictions)
        cur_preds = list(current_predictions)
        
        # Calculate distributions
        ref_dist = dict(Counter(ref_preds))
        cur_dist = dict(Counter(cur_preds))
        
        # Normalize
        ref_total = sum(ref_dist.values())
        cur_total = sum(cur_dist.values())
        ref_dist = {k: v / ref_total for k, v in ref_dist.items()}
        cur_dist = {k: v / cur_total for k, v in cur_dist.items()}
        
        # Test for drift
        statistic, p_value = self._stats.chi_square_test(
            Counter(ref_preds), Counter(cur_preds)
        )
        
        drift_score = DriftScore(
            score=statistic,
            p_value=p_value,
            test_used=StatisticalTest.CHI_SQUARE,
            threshold=self.config.significance_level,
        )
        
        severity = self._score_to_severity(drift_score)
        
        return PredictionDrift(
            drift_score=drift_score,
            severity=severity,
            reference_distribution=ref_dist,
            current_distribution=cur_dist,
            description="Prediction distribution has shifted" if drift_score.is_drifted else "Predictions stable",
        )
    
    def _detect_performance_drift(
        self, predictions: Any, labels: Any
    ) -> List[PerformanceDrift]:
        """Detect drift in performance metrics."""
        drifts = []
        
        cur_preds = list(predictions) if predictions is not None else []
        cur_labels = list(labels)
        ref_preds = list(self.reference.predictions) if self.reference.predictions is not None else []
        ref_labels = list(self.reference.labels) if self.reference.labels is not None else []
        
        if not cur_preds or not ref_preds:
            return drifts
        
        # Calculate accuracy
        ref_accuracy = sum(1 for p, l in zip(ref_preds, ref_labels) if p == l) / len(ref_preds)
        cur_accuracy = sum(1 for p, l in zip(cur_preds, cur_labels) if p == l) / len(cur_preds)
        
        change = (cur_accuracy - ref_accuracy) / ref_accuracy if ref_accuracy > 0 else 0
        
        severity = DriftSeverity.NONE
        if abs(change) > self.config.performance_threshold_critical:
            severity = DriftSeverity.CRITICAL
        elif abs(change) > self.config.performance_threshold_warning:
            severity = DriftSeverity.HIGH
        
        drifts.append(PerformanceDrift(
            metric_name="accuracy",
            reference_value=ref_accuracy,
            current_value=cur_accuracy,
            change_percent=change,
            severity=severity,
            threshold=self.config.performance_threshold_warning,
            description=f"Accuracy changed from {ref_accuracy:.3f} to {cur_accuracy:.3f}",
        ))
        
        return drifts
    
    def _score_to_severity(self, drift_score: DriftScore) -> DriftSeverity:
        """Convert drift score to severity level."""
        if not drift_score.is_drifted:
            return DriftSeverity.NONE
        
        # Use p-value or score for severity
        if drift_score.p_value is not None:
            if drift_score.p_value < 0.001:
                return DriftSeverity.CRITICAL
            elif drift_score.p_value < 0.01:
                return DriftSeverity.HIGH
            elif drift_score.p_value < 0.05:
                return DriftSeverity.MEDIUM
            else:
                return DriftSeverity.LOW
        
        # Use PSI if available
        psi = drift_score.details.get("psi", 0)
        if psi > self.config.psi_threshold_high:
            return DriftSeverity.CRITICAL
        elif psi > self.config.psi_threshold_low:
            return DriftSeverity.HIGH
        
        return DriftSeverity.MEDIUM
    
    def _determine_overall_severity(
        self,
        feature_drifts: List[FeatureDrift],
        prediction_drift: Optional[PredictionDrift],
        performance_drifts: List[PerformanceDrift],
    ) -> DriftSeverity:
        """Determine overall severity from all drifts."""
        severities = []
        
        for fd in feature_drifts:
            if fd.drift_score.is_drifted:
                severities.append(fd.severity)
        
        if prediction_drift and prediction_drift.drift_score.is_drifted:
            severities.append(prediction_drift.severity)
        
        for pd in performance_drifts:
            if pd.is_degraded:
                severities.append(pd.severity)
        
        if not severities:
            return DriftSeverity.NONE
        
        severity_order = [
            DriftSeverity.CRITICAL,
            DriftSeverity.HIGH,
            DriftSeverity.MEDIUM,
            DriftSeverity.LOW,
        ]
        
        for severity in severity_order:
            if severity in severities:
                return severity
        
        return DriftSeverity.NONE
    
    def _generate_alerts(
        self,
        feature_drifts: List[FeatureDrift],
        prediction_drift: Optional[PredictionDrift],
        performance_drifts: List[PerformanceDrift],
        overall_severity: DriftSeverity,
    ) -> List[Alert]:
        """Generate alerts for detected drift."""
        alerts = []
        
        # Overall drift alert
        if overall_severity in (DriftSeverity.CRITICAL, DriftSeverity.HIGH):
            alert_level = AlertLevel.EMERGENCY if overall_severity == DriftSeverity.CRITICAL else AlertLevel.ALERT
            
            drifted = [f.feature_name for f in feature_drifts if f.drift_score.is_drifted]
            
            alerts.append(Alert(
                alert_id=str(uuid.uuid4())[:8],
                level=alert_level,
                drift_type=DriftType.DATA_DRIFT,
                message=f"Significant drift detected in {len(drifted)} features: {', '.join(drifted[:5])}",
                details={"drifted_features": drifted},
            ))
        
        # Performance degradation alert
        for pd in performance_drifts:
            if pd.is_degraded and pd.severity in (DriftSeverity.CRITICAL, DriftSeverity.HIGH):
                alerts.append(Alert(
                    alert_id=str(uuid.uuid4())[:8],
                    level=AlertLevel.EMERGENCY if pd.severity == DriftSeverity.CRITICAL else AlertLevel.ALERT,
                    drift_type=DriftType.CONCEPT_DRIFT,
                    message=f"Performance degradation: {pd.metric_name} dropped by {abs(pd.change_percent)*100:.1f}%",
                    details={"metric": pd.metric_name, "change": pd.change_percent},
                ))
        
        return alerts
    
    def _generate_feature_description(
        self,
        feature_name: str,
        drift_score: DriftScore,
        ref_stats: Dict[str, Any],
        cur_stats: Dict[str, Any],
    ) -> str:
        """Generate description for feature drift."""
        if not drift_score.is_drifted:
            return f"No significant drift in '{feature_name}'"
        
        parts = [f"Drift detected in '{feature_name}'"]
        
        if drift_score.p_value is not None:
            parts.append(f"p-value: {drift_score.p_value:.4f}")
        
        # Add stat changes
        if "mean" in ref_stats and "mean" in cur_stats:
            ref_mean = ref_stats["mean"]
            cur_mean = cur_stats["mean"]
            change = ((cur_mean - ref_mean) / ref_mean * 100) if ref_mean != 0 else 0
            parts.append(f"mean changed by {change:.1f}%")
        
        return "; ".join(parts)
    
    def _generate_feature_suggestion(
        self,
        feature_name: str,
        drift_score: DriftScore,
        severity: DriftSeverity,
    ) -> str:
        """Generate suggestion for feature drift."""
        if not drift_score.is_drifted:
            return "No action needed"
        
        if severity == DriftSeverity.CRITICAL:
            return f"Urgent: Investigate '{feature_name}' immediately. Consider retraining model."
        elif severity == DriftSeverity.HIGH:
            return f"Investigate '{feature_name}' data source. Monitor closely."
        elif severity == DriftSeverity.MEDIUM:
            return f"Monitor '{feature_name}' for continued drift."
        else:
            return f"Minor drift in '{feature_name}'. Continue monitoring."
    
    def _generate_summary(
        self,
        feature_drifts: List[FeatureDrift],
        prediction_drift: Optional[PredictionDrift],
        performance_drifts: List[PerformanceDrift],
    ) -> str:
        """Generate overall summary."""
        drifted = [f for f in feature_drifts if f.drift_score.is_drifted]
        degraded = [p for p in performance_drifts if p.is_degraded]
        
        parts = []
        
        if drifted:
            parts.append(f"Drift detected in {len(drifted)}/{len(feature_drifts)} features")
            critical = [f.feature_name for f in drifted if f.severity == DriftSeverity.CRITICAL]
            if critical:
                parts.append(f"Critical: {', '.join(critical)}")
        else:
            parts.append("No significant feature drift detected")
        
        if prediction_drift and prediction_drift.drift_score.is_drifted:
            parts.append("Prediction distribution has shifted")
        
        if degraded:
            parts.append(f"Performance degraded: {', '.join(p.metric_name for p in degraded)}")
        
        return ". ".join(parts)
    
    def _generate_recommendations(
        self,
        feature_drifts: List[FeatureDrift],
        prediction_drift: Optional[PredictionDrift],
        performance_drifts: List[PerformanceDrift],
    ) -> List[str]:
        """Generate recommendations based on drift."""
        recommendations = []
        
        critical = [f for f in feature_drifts if f.severity == DriftSeverity.CRITICAL]
        if critical:
            recommendations.append(
                f"Immediately investigate critical drift in: {', '.join(f.feature_name for f in critical)}"
            )
        
        if any(p.is_degraded for p in performance_drifts):
            recommendations.append("Consider retraining the model with recent data")
        
        drifted_count = sum(1 for f in feature_drifts if f.drift_score.is_drifted)
        if drifted_count > len(feature_drifts) * 0.3:
            recommendations.append("Significant portion of features drifted - review data pipeline")
        
        if prediction_drift and prediction_drift.drift_score.is_drifted:
            recommendations.append("Review prediction distribution shift and validate model calibration")
        
        if not recommendations:
            recommendations.append("No immediate action required - continue monitoring")
        
        return recommendations
    
    def _update_metrics(self, report: DriftReport) -> None:
        """Update aggregated metrics."""
        self.metrics.total_checks += 1
        self.metrics.last_check_time = report.timestamp
        
        if report.overall_drift_detected:
            self.metrics.drift_detected_count += 1
        
        self.metrics.alerts_generated += len(report.alerts)
        
        # Update drift scores
        scores = [f.drift_score.score for f in report.feature_drifts if f.drift_score.score > 0]
        if scores:
            self.metrics.avg_drift_score = sum(scores) / len(scores)
            self.metrics.max_drift_score = max(scores)
            
            max_feature = max(report.feature_drifts, key=lambda f: f.drift_score.score)
            self.metrics.most_drifted_feature = max_feature.feature_name
        
        # Add to history
        self.metrics.history.append({
            "timestamp": report.timestamp.isoformat(),
            "drift_detected": report.overall_drift_detected,
            "drift_count": report.drift_count,
            "severity": report.overall_severity.value,
        })
        
        # Keep last 100 entries
        if len(self.metrics.history) > 100:
            self.metrics.history = self.metrics.history[-100:]


class DataDriftMonitor:
    """
    Continuous monitoring for data drift.
    
    Example:
        >>> monitor = DataDriftMonitor(detector)
        >>> monitor.start()
        >>> # Add new data as it arrives
        >>> monitor.add_samples(new_data)
        >>> # Check current status
        >>> status = monitor.get_status()
    """
    
    def __init__(
        self,
        detector: DriftDetector,
        window_size: int = 1000,
    ):
        """Initialize monitor."""
        self.detector = detector
        self.window_size = window_size
        self._buffer: List[Dict[str, Any]] = []
        self._windows: List[MonitoringWindow] = []
        self._running = False
    
    def add_samples(
        self,
        data: Any,
        predictions: Optional[Any] = None,
        labels: Optional[Any] = None,
    ) -> Optional[DriftReport]:
        """
        Add new samples to monitoring buffer.
        Returns report if window threshold reached.
        """
        processed, _ = self.detector._process_data(data, None)
        self._buffer.extend(processed)
        
        if len(self._buffer) >= self.window_size:
            return self._process_window(predictions, labels)
        
        return None
    
    def _process_window(
        self,
        predictions: Optional[Any],
        labels: Optional[Any],
    ) -> DriftReport:
        """Process accumulated window of data."""
        window_data = self._buffer[:self.window_size]
        self._buffer = self._buffer[self.window_size:]
        
        # Create window record
        window = MonitoringWindow(
            window_id=str(uuid.uuid4())[:8],
            start_time=datetime.now(),
            end_time=datetime.now(),
            sample_count=len(window_data),
            data=window_data,
        )
        self._windows.append(window)
        
        # Keep last 10 windows
        if len(self._windows) > 10:
            self._windows = self._windows[-10:]
        
        # Run detection
        return self.detector.detect(window_data, predictions, labels)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            "buffer_size": len(self._buffer),
            "window_size": self.window_size,
            "windows_processed": len(self._windows),
            "metrics": self.detector.get_metrics().to_dict(),
        }
    
    def clear_buffer(self) -> None:
        """Clear the sample buffer."""
        self._buffer = []
