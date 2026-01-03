"""
Model Drift Detector - Production monitoring for ML model drift.

Detect data drift, concept drift, and performance degradation in your
deployed ML models with statistical tests and continuous monitoring.

Example:
    >>> from model_drift_detector import DriftDetector
    >>> detector = DriftDetector()
    >>> detector.set_reference(training_data)
    >>> report = detector.detect(production_data)
    >>> if report.overall_drift_detected:
    ...     print(f"Alert: {report.summary}")
"""

from .types import (
    # Enums
    DriftType,
    DriftSeverity,
    StatisticalTest,
    FeatureType,
    AlertLevel,
    # Data classes
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
    WebhookConfig,
    MonitoringConfig,
)

from .detector import (
    DriftDetector,
    DataDriftMonitor,
    StatisticalTests,
)

__version__ = "0.1.0"
__author__ = "Pranay M"
__email__ = "pranay@example.com"

__all__ = [
    # Main classes
    "DriftDetector",
    "DataDriftMonitor",
    "StatisticalTests",
    # Enums
    "DriftType",
    "DriftSeverity",
    "StatisticalTest",
    "FeatureType",
    "AlertLevel",
    # Data classes
    "DriftScore",
    "FeatureDrift",
    "PredictionDrift",
    "PerformanceDrift",
    "Alert",
    "DriftConfig",
    "ReferenceData",
    "DriftReport",
    "MonitoringWindow",
    "DriftMetrics",
    "WebhookConfig",
    "MonitoringConfig",
]
