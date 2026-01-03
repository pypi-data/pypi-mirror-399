# Model Drift Detector

[![PyPI version](https://badge.fury.io/py/model-drift-detector.svg)](https://badge.fury.io/py/model-drift-detector)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python library for detecting and monitoring model drift in production ML systems. Supports data drift, concept drift, prediction drift, and performance degradation detection with multiple statistical tests.

## Features

- **Multiple Drift Types**: Data drift, concept drift, prediction drift, feature drift, label drift, and covariate shift
- **Statistical Tests**: KS test, Chi-square, PSI, JS divergence, Wasserstein distance, and more
- **Performance Monitoring**: Track accuracy, precision, recall, F1, AUC, MSE, and custom metrics
- **Alerting System**: Configurable alerts with multiple severity levels
- **Baseline Management**: Create and manage reference data snapshots
- **Zero Dependencies Core**: Works with pure Python, optional NumPy/pandas support
- **Async Support**: Non-blocking drift detection for high-throughput systems
- **Comprehensive Reporting**: Detailed reports with recommendations

## Installation

```bash
pip install model-drift-detector
```

With optional dependencies:

```bash
# With NumPy/SciPy for advanced statistical tests
pip install model-drift-detector[numpy]

# With pandas for DataFrame support  
pip install model-drift-detector[pandas]

# Full installation
pip install model-drift-detector[all]
```

## Quick Start

### Basic Drift Detection

```python
from model_drift_detector import DriftDetector

# Initialize detector
detector = DriftDetector()

# Reference data (training distribution)
reference_data = {
    "age": [25, 30, 35, 40, 45, 50, 55, 60],
    "income": [30000, 45000, 55000, 65000, 75000, 85000, 95000, 105000],
    "category": ["A", "B", "A", "C", "B", "A", "C", "B"]
}

# Current production data
current_data = {
    "age": [35, 40, 45, 50, 55, 60, 65, 70],  # Shifted older
    "income": [35000, 50000, 60000, 70000, 80000, 90000, 100000, 110000],
    "category": ["B", "C", "C", "C", "B", "C", "C", "C"]  # Category shift
}

# Detect drift
report = detector.detect(reference_data, current_data)

# Check results
print(f"Drift detected: {report.features_with_drift}/{report.total_features} features")
print(f"Overall severity: {report.overall_severity.value}")

for result in report.feature_results:
    if result.is_drift_detected:
        print(f"  - {result.feature_name}: {result.drift_type.value} "
              f"(severity: {result.severity.value})")
```

### Monitor with Baseline

```python
from model_drift_detector import DriftMonitor

# Create monitor with baseline
monitor = DriftMonitor(name="production-model-v1")

# Set baseline from training data
monitor.set_baseline(training_data)

# Monitor incoming data batches
for batch in production_batches:
    report = monitor.check(batch)
    
    if report.features_with_drift > 0:
        print(f"⚠️ Drift detected in batch!")
        for feature in report.get_drifted_features():
            print(f"  - {feature}")
```

### Configure Alerts

```python
from model_drift_detector import DriftMonitor, MonitoringConfig, AlertLevel

# Custom configuration
config = MonitoringConfig(
    name="critical-model",
    features=["age", "income", "category"],
    drift_threshold=0.05,
    severity_thresholds={
        "low": 0.05,
        "medium": 0.1,
        "high": 0.2,
        "critical": 0.3
    },
    alert_on_drift=True
)

# Alert callback
def handle_alert(alert):
    if alert.level == AlertLevel.CRITICAL:
        send_pager_duty_alert(alert.message)
    elif alert.level == AlertLevel.ERROR:
        send_slack_notification(alert.message)
    else:
        log_alert(alert)

monitor = DriftMonitor(config=config)
monitor.on_alert(handle_alert)
```

### Performance Drift Detection

```python
from model_drift_detector import PerformanceMonitor

# Track model performance over time
perf_monitor = PerformanceMonitor(
    baseline_metrics={
        "accuracy": 0.95,
        "f1_score": 0.92,
        "auc_roc": 0.98
    },
    degradation_threshold=0.05
)

# Check current performance
current_metrics = {
    "accuracy": 0.89,  # Degraded
    "f1_score": 0.85,  # Degraded
    "auc_roc": 0.96
}

degradation = perf_monitor.check(current_metrics)

if degradation.is_degraded:
    print(f"Performance degradation detected!")
    for metric, drop in degradation.metrics_dropped.items():
        print(f"  - {metric}: dropped {drop:.2%}")
```

## API Reference

### DriftDetector

Main class for drift detection.

```python
from model_drift_detector import DriftDetector, StatisticalTest

detector = DriftDetector(
    default_test=StatisticalTest.KS_TEST,  # Default statistical test
    p_value_threshold=0.05,                 # Significance threshold
    auto_detect_types=True                  # Auto-detect feature types
)

# Detect drift between two datasets
report = detector.detect(
    reference_data,    # Reference/baseline data
    current_data,      # Current production data
    features=None,     # Specific features (None = all)
    tests=None         # Override tests per feature
)
```

### DriftMonitor

Continuous monitoring with baseline management.

```python
from model_drift_detector import DriftMonitor

monitor = DriftMonitor(
    name="my-model",
    config=None,           # Optional MonitoringConfig
    baseline=None          # Optional initial baseline
)

# Set baseline
monitor.set_baseline(data, sample_size=10000)

# Check for drift
report = monitor.check(current_data)

# Get baseline info
baseline = monitor.get_baseline()

# Update baseline (e.g., after retraining)
monitor.update_baseline(new_data)
```

### Statistical Tests

Available statistical tests for drift detection:

| Test | Use Case | Data Type |
|------|----------|-----------|
| `KS_TEST` | Distribution comparison | Numerical |
| `CHI_SQUARE` | Category frequency | Categorical |
| `PSI` | Population stability | Both |
| `JS_DIVERGENCE` | Distribution similarity | Both |
| `KL_DIVERGENCE` | Information loss | Both |
| `WASSERSTEIN` | Distribution distance | Numerical |
| `T_TEST` | Mean comparison | Numerical |
| `MANN_WHITNEY` | Rank comparison | Numerical |
| `CRAMERS_V` | Association strength | Categorical |

```python
from model_drift_detector import StatisticalTest

# Use specific tests per feature
detector.detect(
    reference_data,
    current_data,
    tests={
        "age": StatisticalTest.KS_TEST,
        "income": StatisticalTest.WASSERSTEIN,
        "category": StatisticalTest.CHI_SQUARE
    }
)
```

### DriftReport

Comprehensive drift analysis report.

```python
report = detector.detect(reference, current)

# Access report properties
report.report_id              # Unique identifier
report.created_at             # Timestamp
report.total_features         # Number of features analyzed
report.features_with_drift    # Number with detected drift
report.drift_rate             # Ratio of drifted features
report.overall_drift_score    # Combined drift score
report.overall_severity       # Overall severity level
report.feature_results        # List of DriftResult objects
report.recommendations        # Suggested actions

# Filter results
drifted = report.get_drifted_features()
critical = report.get_results_by_severity(DriftSeverity.CRITICAL)

# Export
report_dict = report.to_dict()
report_json = report.to_json()
```

### Severity Levels

```python
from model_drift_detector import DriftSeverity

DriftSeverity.NONE      # No drift detected
DriftSeverity.LOW       # Minor drift, monitor
DriftSeverity.MEDIUM    # Moderate drift, investigate
DriftSeverity.HIGH      # Significant drift, action needed
DriftSeverity.CRITICAL  # Severe drift, immediate action
```

## Advanced Usage

### Custom Statistical Tests

```python
from model_drift_detector import DriftDetector, DriftResult

class CustomDriftDetector(DriftDetector):
    def custom_test(self, reference, current, feature_name):
        """Implement custom drift test."""
        # Your custom logic
        statistic = calculate_custom_statistic(reference, current)
        
        return DriftResult(
            feature_name=feature_name,
            drift_type=DriftType.DATA_DRIFT,
            test_used=StatisticalTest.KS_TEST,  # Or custom
            statistic=statistic,
            p_value=None,
            threshold=0.1,
            is_drift_detected=statistic > 0.1,
            severity=self._calculate_severity(statistic)
        )
```

### Streaming Detection

```python
from model_drift_detector import StreamingDetector

# Window-based streaming detection
stream_detector = StreamingDetector(
    window_size=1000,
    slide_size=100,
    baseline_data=training_data
)

# Process streaming data
for record in data_stream:
    stream_detector.add(record)
    
    if stream_detector.window_ready():
        result = stream_detector.check_window()
        if result.is_drift_detected:
            handle_drift(result)
```

### Multi-Model Monitoring

```python
from model_drift_detector import DriftMonitorRegistry

# Central registry for multiple models
registry = DriftMonitorRegistry()

# Register monitors
registry.register("model-a", DriftMonitor(name="model-a"))
registry.register("model-b", DriftMonitor(name="model-b"))

# Set baselines
for name, monitor in registry.items():
    monitor.set_baseline(baselines[name])

# Check all models
for name, monitor in registry.items():
    report = monitor.check(current_data[name])
    if report.features_with_drift > 0:
        alert_team(name, report)
```

### Integration with MLflow

```python
import mlflow
from model_drift_detector import DriftMonitor

monitor = DriftMonitor(name="mlflow-tracked-model")
monitor.set_baseline(training_data)

# Log drift metrics to MLflow
with mlflow.start_run():
    report = monitor.check(production_data)
    
    mlflow.log_metric("drift_score", report.overall_drift_score)
    mlflow.log_metric("features_drifted", report.features_with_drift)
    mlflow.log_metric("drift_rate", report.drift_rate)
    
    for result in report.feature_results:
        mlflow.log_metric(
            f"drift_{result.feature_name}", 
            result.statistic
        )
```

### Database Baseline Storage

```python
from model_drift_detector import DriftMonitor, BaselineStore

# Custom baseline storage
class SQLBaselineStore(BaselineStore):
    def __init__(self, connection_string):
        self.conn = create_connection(connection_string)
    
    def save(self, snapshot):
        # Save to database
        pass
    
    def load(self, snapshot_id):
        # Load from database
        pass

# Use custom storage
store = SQLBaselineStore("postgresql://...")
monitor = DriftMonitor(name="db-backed", baseline_store=store)
```

## Comparison with Other Libraries

| Feature | model-drift-detector | evidently | alibi-detect |
|---------|---------------------|-----------|--------------|
| Zero dependencies | ✅ | ❌ | ❌ |
| Streaming support | ✅ | ❌ | ✅ |
| Custom tests | ✅ | ✅ | ✅ |
| Built-in alerting | ✅ | ❌ | ❌ |
| Async support | ✅ | ❌ | ❌ |
| Pure Python | ✅ | ❌ | ❌ |

## Best Practices

1. **Set Representative Baselines**: Use diverse, representative training data
2. **Monitor Multiple Drift Types**: Combine data drift and performance drift
3. **Tune Thresholds**: Adjust based on your tolerance for false positives
4. **Regular Baseline Updates**: Update after model retraining
5. **Feature-Specific Tests**: Use appropriate tests for each feature type
6. **Alert Thoughtfully**: Avoid alert fatigue with proper severity mapping

## Troubleshooting

### High False Positive Rate

- Increase `drift_threshold` (e.g., 0.05 → 0.1)
- Use larger sample sizes for comparison
- Consider domain-specific thresholds

### Missing Drift Detection

- Decrease `drift_threshold`
- Use more sensitive tests (e.g., Wasserstein)
- Check feature type detection

### Performance Issues

- Reduce `window_size` for streaming
- Use batch processing for large datasets
- Enable sampling for very large datasets

## License

MIT License - Pranay M

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

### 1.0.0
- Initial release
- Core drift detection with 9 statistical tests
- Monitoring and alerting system
- Baseline management
- Streaming support
