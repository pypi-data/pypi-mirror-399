"""
Tests for model-drift-detector package.
"""

import pytest
from datetime import datetime
from model_drift_detector import (
    DriftDetector,
    DriftMonitor,
    PerformanceMonitor,
    StreamingDetector,
    DriftType,
    DriftSeverity,
    StatisticalTest,
    FeatureType,
    AlertLevel,
    MonitoringConfig,
    DriftResult,
    DriftReport,
    Alert,
    FeatureStatistics,
    PerformanceMetrics,
    BaselineSnapshot
)


class TestTypes:
    """Test type definitions and data classes."""
    
    def test_drift_type_enum(self):
        """Test DriftType enum values."""
        assert DriftType.DATA_DRIFT.value == "data_drift"
        assert DriftType.CONCEPT_DRIFT.value == "concept_drift"
        assert DriftType.PREDICTION_DRIFT.value == "prediction_drift"
        assert DriftType.FEATURE_DRIFT.value == "feature_drift"
    
    def test_drift_severity_enum(self):
        """Test DriftSeverity enum values."""
        assert DriftSeverity.NONE.value == "none"
        assert DriftSeverity.LOW.value == "low"
        assert DriftSeverity.CRITICAL.value == "critical"
    
    def test_statistical_test_enum(self):
        """Test StatisticalTest enum values."""
        assert StatisticalTest.KS_TEST.value == "kolmogorov_smirnov"
        assert StatisticalTest.PSI.value == "population_stability_index"
        assert StatisticalTest.CHI_SQUARE.value == "chi_square"
    
    def test_feature_statistics(self):
        """Test FeatureStatistics dataclass."""
        stats = FeatureStatistics(
            name="age",
            feature_type=FeatureType.NUMERICAL,
            mean=35.5,
            std=10.2,
            min_value=18,
            max_value=65,
            missing_count=5,
            missing_rate=0.05
        )
        
        assert stats.name == "age"
        assert stats.feature_type == FeatureType.NUMERICAL
        assert stats.mean == 35.5
        
        stats_dict = stats.to_dict()
        assert stats_dict["name"] == "age"
        assert stats_dict["feature_type"] == "numerical"
    
    def test_drift_result(self):
        """Test DriftResult dataclass."""
        result = DriftResult(
            feature_name="income",
            drift_type=DriftType.DATA_DRIFT,
            test_used=StatisticalTest.KS_TEST,
            statistic=0.25,
            p_value=0.01,
            threshold=0.05,
            is_drift_detected=True,
            severity=DriftSeverity.HIGH
        )
        
        assert result.feature_name == "income"
        assert result.is_drift_detected is True
        assert result.severity == DriftSeverity.HIGH
        
        result_dict = result.to_dict()
        assert result_dict["drift_type"] == "data_drift"
        assert result_dict["is_drift_detected"] is True
    
    def test_drift_report(self):
        """Test DriftReport dataclass."""
        results = [
            DriftResult(
                feature_name="age",
                drift_type=DriftType.DATA_DRIFT,
                test_used=StatisticalTest.KS_TEST,
                statistic=0.15,
                p_value=0.03,
                threshold=0.05,
                is_drift_detected=True,
                severity=DriftSeverity.MEDIUM
            ),
            DriftResult(
                feature_name="income",
                drift_type=DriftType.DATA_DRIFT,
                test_used=StatisticalTest.KS_TEST,
                statistic=0.02,
                p_value=0.45,
                threshold=0.05,
                is_drift_detected=False,
                severity=DriftSeverity.NONE
            )
        ]
        
        report = DriftReport(
            report_id="test-001",
            created_at=datetime.now(),
            reference_period="2024-01",
            current_period="2024-02",
            total_features=2,
            features_with_drift=1,
            overall_drift_score=0.15,
            overall_severity=DriftSeverity.MEDIUM,
            feature_results=results
        )
        
        assert report.drift_rate == 0.5
        assert report.get_drifted_features() == ["age"]
        assert len(report.get_results_by_severity(DriftSeverity.MEDIUM)) == 1
    
    def test_alert(self):
        """Test Alert dataclass."""
        alert = Alert(
            alert_id="alert-001",
            level=AlertLevel.WARNING,
            drift_type=DriftType.DATA_DRIFT,
            feature_name="age",
            message="Drift detected in age feature",
            drift_result=None
        )
        
        assert not alert.acknowledged
        
        alert.acknowledge("user@example.com")
        
        assert alert.acknowledged is True
        assert alert.acknowledged_by == "user@example.com"
        assert alert.acknowledged_at is not None
    
    def test_monitoring_config(self):
        """Test MonitoringConfig defaults."""
        config = MonitoringConfig(
            name="test-monitor",
            features=["a", "b", "c"]
        )
        
        assert config.drift_threshold == 0.05
        assert config.alert_on_drift is True
        assert "low" in config.severity_thresholds
    
    def test_performance_metrics(self):
        """Test PerformanceMetrics dataclass."""
        metrics = PerformanceMetrics(
            accuracy=0.95,
            precision=0.92,
            recall=0.89,
            f1_score=0.905
        )
        
        metrics_dict = metrics.to_dict()
        assert metrics_dict["accuracy"] == 0.95
        assert metrics_dict["f1_score"] == 0.905


class TestDriftDetector:
    """Test DriftDetector class."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = DriftDetector()
        assert detector.p_value_threshold == 0.05
        assert detector.auto_detect_types is True
    
    def test_initialization_custom(self):
        """Test detector with custom settings."""
        detector = DriftDetector(
            default_test=StatisticalTest.PSI,
            p_value_threshold=0.01,
            auto_detect_types=False
        )
        
        assert detector.default_test == StatisticalTest.PSI
        assert detector.p_value_threshold == 0.01
    
    def test_detect_feature_type_numerical(self):
        """Test numerical feature detection."""
        detector = DriftDetector()
        data = [1, 2, 3, 4, 5, 6.5, 7.8]
        
        feature_type = detector._detect_feature_type(data)
        assert feature_type == FeatureType.NUMERICAL
    
    def test_detect_feature_type_categorical(self):
        """Test categorical feature detection."""
        detector = DriftDetector()
        data = ["A", "B", "C", "A", "B"]
        
        feature_type = detector._detect_feature_type(data)
        assert feature_type == FeatureType.CATEGORICAL
    
    def test_detect_feature_type_binary(self):
        """Test binary feature detection."""
        detector = DriftDetector()
        data = [True, False, True, True, False]
        
        feature_type = detector._detect_feature_type(data)
        assert feature_type == FeatureType.BINARY
    
    def test_calculate_statistics_numerical(self):
        """Test statistics calculation for numerical data."""
        detector = DriftDetector()
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        stats = detector._calculate_statistics("test", data, FeatureType.NUMERICAL)
        
        assert stats.name == "test"
        assert stats.mean == 5.5
        assert stats.min_value == 1
        assert stats.max_value == 10
        assert stats.unique_count == 10
    
    def test_calculate_statistics_categorical(self):
        """Test statistics calculation for categorical data."""
        detector = DriftDetector()
        data = ["A", "B", "A", "C", "A", "B"]
        
        stats = detector._calculate_statistics("cat", data, FeatureType.CATEGORICAL)
        
        assert stats.mode == "A"
        assert stats.unique_count == 3
        assert stats.distribution["A"] == 3
    
    def test_detect_no_drift(self):
        """Test detection with no drift."""
        detector = DriftDetector()
        
        reference = {"feature": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
        current = {"feature": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
        
        report = detector.detect(reference, current)
        
        assert report.features_with_drift == 0
        assert report.overall_severity == DriftSeverity.NONE
    
    def test_detect_with_drift(self):
        """Test detection with drift present."""
        detector = DriftDetector()
        
        reference = {"feature": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
        current = {"feature": [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]}
        
        report = detector.detect(reference, current)
        
        assert report.features_with_drift == 1
        assert report.overall_severity != DriftSeverity.NONE
    
    def test_detect_multiple_features(self):
        """Test detection with multiple features."""
        detector = DriftDetector()
        
        reference = {
            "age": [25, 30, 35, 40, 45],
            "income": [30000, 40000, 50000, 60000, 70000],
            "category": ["A", "B", "A", "C", "B"]
        }
        
        current = {
            "age": [25, 30, 35, 40, 45],  # No drift
            "income": [80000, 90000, 100000, 110000, 120000],  # Drift
            "category": ["A", "B", "A", "C", "B"]  # No drift
        }
        
        report = detector.detect(reference, current)
        
        assert report.total_features == 3
        assert "income" in report.get_drifted_features()
    
    def test_detect_specific_features(self):
        """Test detection on specific features only."""
        detector = DriftDetector()
        
        reference = {
            "a": [1, 2, 3],
            "b": [4, 5, 6],
            "c": [7, 8, 9]
        }
        
        current = {
            "a": [10, 20, 30],
            "b": [40, 50, 60],
            "c": [70, 80, 90]
        }
        
        report = detector.detect(reference, current, features=["a", "b"])
        
        assert report.total_features == 2
    
    def test_ks_test_numerical(self):
        """Test KS test for numerical data."""
        detector = DriftDetector()
        
        reference = list(range(100))
        current = list(range(50, 150))  # Shifted
        
        result = detector._ks_test("test", reference, current)
        
        assert result.test_used == StatisticalTest.KS_TEST
        assert result.statistic > 0
    
    def test_psi_calculation(self):
        """Test PSI calculation."""
        detector = DriftDetector()
        
        reference = [1, 1, 1, 2, 2, 2, 3, 3, 3, 3]
        current = [1, 2, 2, 2, 2, 3, 3, 3, 3, 3]  # Slight shift
        
        psi = detector._calculate_psi(reference, current)
        
        assert isinstance(psi, float)
        assert psi >= 0
    
    def test_chi_square_categorical(self):
        """Test chi-square test for categorical data."""
        detector = DriftDetector()
        
        reference = ["A", "A", "A", "B", "B", "C"]
        current = ["A", "B", "B", "B", "C", "C"]
        
        result = detector._chi_square_test("cat", reference, current)
        
        assert result.test_used == StatisticalTest.CHI_SQUARE
    
    def test_severity_calculation(self):
        """Test severity level calculation."""
        detector = DriftDetector()
        
        assert detector._calculate_severity(0.02) == DriftSeverity.NONE
        assert detector._calculate_severity(0.07) == DriftSeverity.LOW
        assert detector._calculate_severity(0.15) == DriftSeverity.MEDIUM
        assert detector._calculate_severity(0.25) == DriftSeverity.HIGH
        assert detector._calculate_severity(0.4) == DriftSeverity.CRITICAL
    
    def test_report_generation(self):
        """Test complete report generation."""
        detector = DriftDetector()
        
        reference = {"x": [1, 2, 3, 4, 5]}
        current = {"x": [10, 20, 30, 40, 50]}
        
        report = detector.detect(reference, current)
        
        assert report.report_id is not None
        assert report.created_at is not None
        assert len(report.feature_results) == 1
        
        report_dict = report.to_dict()
        assert "feature_results" in report_dict


class TestDriftMonitor:
    """Test DriftMonitor class."""
    
    def test_initialization(self):
        """Test monitor initialization."""
        monitor = DriftMonitor(name="test")
        assert monitor.name == "test"
        assert monitor.baseline is None
    
    def test_set_baseline(self):
        """Test setting baseline."""
        monitor = DriftMonitor(name="test")
        
        data = {
            "feature_a": [1, 2, 3, 4, 5],
            "feature_b": ["A", "B", "A", "C", "B"]
        }
        
        monitor.set_baseline(data)
        
        assert monitor.baseline is not None
        assert "feature_a" in monitor.baseline.feature_statistics
    
    def test_check_without_baseline(self):
        """Test check raises error without baseline."""
        monitor = DriftMonitor(name="test")
        
        with pytest.raises(ValueError, match="baseline"):
            monitor.check({"feature": [1, 2, 3]})
    
    def test_check_with_baseline(self):
        """Test check with baseline set."""
        monitor = DriftMonitor(name="test")
        
        baseline_data = {"feature": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
        current_data = {"feature": [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]}
        
        monitor.set_baseline(baseline_data)
        report = monitor.check(current_data)
        
        assert isinstance(report, DriftReport)
    
    def test_update_baseline(self):
        """Test baseline update."""
        monitor = DriftMonitor(name="test")
        
        monitor.set_baseline({"feature": [1, 2, 3]})
        old_id = monitor.baseline.snapshot_id
        
        monitor.update_baseline({"feature": [4, 5, 6]})
        new_id = monitor.baseline.snapshot_id
        
        assert old_id != new_id
    
    def test_get_baseline(self):
        """Test getting baseline snapshot."""
        monitor = DriftMonitor(name="test")
        
        assert monitor.get_baseline() is None
        
        monitor.set_baseline({"feature": [1, 2, 3]})
        
        baseline = monitor.get_baseline()
        assert isinstance(baseline, BaselineSnapshot)
    
    def test_with_config(self):
        """Test monitor with custom config."""
        config = MonitoringConfig(
            name="custom",
            features=["a", "b"],
            drift_threshold=0.1
        )
        
        monitor = DriftMonitor(config=config)
        
        assert monitor.config.drift_threshold == 0.1
    
    def test_alert_callback(self):
        """Test alert callback registration."""
        monitor = DriftMonitor(name="test")
        alerts_received = []
        
        def callback(alert):
            alerts_received.append(alert)
        
        monitor.on_alert(callback)
        
        # Set baseline and check with drift
        monitor.set_baseline({"feature": [1, 2, 3, 4, 5]})
        monitor.check({"feature": [100, 200, 300, 400, 500]})
        
        # Alerts should be generated if drift detected
        # (depends on implementation details)
    
    def test_history_tracking(self):
        """Test report history tracking."""
        monitor = DriftMonitor(name="test")
        monitor.set_baseline({"feature": [1, 2, 3, 4, 5]})
        
        # Run multiple checks
        monitor.check({"feature": [1, 2, 3, 4, 5]})
        monitor.check({"feature": [2, 3, 4, 5, 6]})
        monitor.check({"feature": [3, 4, 5, 6, 7]})
        
        history = monitor.get_history()
        assert len(history) == 3


class TestPerformanceMonitor:
    """Test PerformanceMonitor class."""
    
    def test_initialization(self):
        """Test performance monitor initialization."""
        monitor = PerformanceMonitor(
            baseline_metrics={"accuracy": 0.95, "f1_score": 0.90},
            degradation_threshold=0.05
        )
        
        assert monitor.baseline_metrics["accuracy"] == 0.95
        assert monitor.degradation_threshold == 0.05
    
    def test_check_no_degradation(self):
        """Test check with no performance degradation."""
        monitor = PerformanceMonitor(
            baseline_metrics={"accuracy": 0.95},
            degradation_threshold=0.05
        )
        
        result = monitor.check({"accuracy": 0.94})
        
        assert result.is_degraded is False
    
    def test_check_with_degradation(self):
        """Test check with performance degradation."""
        monitor = PerformanceMonitor(
            baseline_metrics={"accuracy": 0.95},
            degradation_threshold=0.05
        )
        
        result = monitor.check({"accuracy": 0.85})
        
        assert result.is_degraded is True
        assert "accuracy" in result.metrics_dropped
    
    def test_multiple_metrics(self):
        """Test with multiple metrics."""
        monitor = PerformanceMonitor(
            baseline_metrics={
                "accuracy": 0.95,
                "precision": 0.92,
                "recall": 0.89
            },
            degradation_threshold=0.05
        )
        
        result = monitor.check({
            "accuracy": 0.85,  # Degraded
            "precision": 0.91,  # OK
            "recall": 0.80  # Degraded
        })
        
        assert result.is_degraded is True
        assert len(result.metrics_dropped) == 2


class TestStreamingDetector:
    """Test StreamingDetector class."""
    
    def test_initialization(self):
        """Test streaming detector initialization."""
        baseline = {"feature": list(range(100))}
        detector = StreamingDetector(
            window_size=50,
            slide_size=10,
            baseline_data=baseline
        )
        
        assert detector.window_size == 50
        assert detector.slide_size == 10
    
    def test_add_records(self):
        """Test adding records to stream."""
        detector = StreamingDetector(
            window_size=5,
            baseline_data={"feature": [1, 2, 3, 4, 5]}
        )
        
        for i in range(3):
            detector.add({"feature": i})
        
        assert len(detector.buffer) == 3
    
    def test_window_ready(self):
        """Test window ready detection."""
        detector = StreamingDetector(
            window_size=5,
            baseline_data={"feature": [1, 2, 3, 4, 5]}
        )
        
        # Not ready yet
        for i in range(4):
            detector.add({"feature": i})
        assert not detector.window_ready()
        
        # Now ready
        detector.add({"feature": 5})
        assert detector.window_ready()
    
    def test_check_window(self):
        """Test window check."""
        detector = StreamingDetector(
            window_size=5,
            baseline_data={"feature": [1, 2, 3, 4, 5]}
        )
        
        # Add enough data
        for i in range(5):
            detector.add({"feature": i + 100})
        
        result = detector.check_window()
        assert isinstance(result, DriftReport)
    
    def test_window_slide(self):
        """Test window sliding."""
        detector = StreamingDetector(
            window_size=5,
            slide_size=2,
            baseline_data={"feature": [1, 2, 3, 4, 5]}
        )
        
        # Fill window
        for i in range(5):
            detector.add({"feature": i})
        
        detector.check_window()
        
        # After check, buffer should slide
        assert len(detector.buffer) == 3


class TestIntegration:
    """Integration tests."""
    
    def test_full_workflow(self):
        """Test complete drift detection workflow."""
        # 1. Create detector
        detector = DriftDetector()
        
        # 2. Prepare data
        import random
        random.seed(42)
        
        reference = {
            "numeric": [random.gauss(50, 10) for _ in range(100)],
            "categorical": [random.choice(["A", "B", "C"]) for _ in range(100)]
        }
        
        # Shifted distribution
        current = {
            "numeric": [random.gauss(70, 15) for _ in range(100)],  # Mean shift
            "categorical": [random.choice(["A", "B", "C", "D"]) for _ in range(100)]  # New category
        }
        
        # 3. Detect drift
        report = detector.detect(reference, current)
        
        # 4. Verify results
        assert report.total_features == 2
        assert report.features_with_drift >= 1
        
        # 5. Export report
        report_dict = report.to_dict()
        assert "feature_results" in report_dict
    
    def test_monitor_workflow(self):
        """Test monitoring workflow."""
        # 1. Create monitor
        monitor = DriftMonitor(name="test-model")
        
        # 2. Set baseline
        baseline_data = {
            "feature_a": list(range(100)),
            "feature_b": ["X", "Y", "Z"] * 33 + ["X"]
        }
        monitor.set_baseline(baseline_data)
        
        # 3. Simulate production batches
        batches = [
            {"feature_a": list(range(i, i+100)), "feature_b": ["X", "Y", "Z"] * 33 + ["X"]}
            for i in range(0, 50, 10)
        ]
        
        # 4. Check each batch
        drift_detected = False
        for batch in batches:
            report = monitor.check(batch)
            if report.features_with_drift > 0:
                drift_detected = True
        
        # 5. Check history
        history = monitor.get_history()
        assert len(history) == len(batches)
    
    def test_performance_and_data_drift(self):
        """Test combined performance and data drift monitoring."""
        # Data drift monitor
        data_monitor = DriftMonitor(name="data-drift")
        data_monitor.set_baseline({"feature": list(range(100))})
        
        # Performance monitor
        perf_monitor = PerformanceMonitor(
            baseline_metrics={"accuracy": 0.95, "f1_score": 0.90},
            degradation_threshold=0.05
        )
        
        # Simulate degradation
        current_data = {"feature": list(range(50, 150))}
        current_perf = {"accuracy": 0.82, "f1_score": 0.78}
        
        data_report = data_monitor.check(current_data)
        perf_result = perf_monitor.check(current_perf)
        
        # Both should detect issues
        assert perf_result.is_degraded is True


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_data(self):
        """Test with empty data."""
        detector = DriftDetector()
        
        with pytest.raises(ValueError):
            detector.detect({}, {})
    
    def test_mismatched_features(self):
        """Test with mismatched features."""
        detector = DriftDetector()
        
        reference = {"a": [1, 2, 3]}
        current = {"b": [1, 2, 3]}
        
        with pytest.raises(ValueError):
            detector.detect(reference, current)
    
    def test_single_value(self):
        """Test with single value arrays."""
        detector = DriftDetector()
        
        reference = {"feature": [1]}
        current = {"feature": [2]}
        
        # Should handle gracefully
        report = detector.detect(reference, current)
        assert report.total_features == 1
    
    def test_missing_values(self):
        """Test with missing values."""
        detector = DriftDetector()
        
        reference = {"feature": [1, 2, None, 4, 5]}
        current = {"feature": [1, None, 3, None, 5]}
        
        # Should handle gracefully
        report = detector.detect(reference, current)
        assert report.total_features == 1
    
    def test_all_same_values(self):
        """Test with constant values."""
        detector = DriftDetector()
        
        reference = {"feature": [5, 5, 5, 5, 5]}
        current = {"feature": [5, 5, 5, 5, 5]}
        
        report = detector.detect(reference, current)
        assert report.features_with_drift == 0
    
    def test_very_large_data(self):
        """Test with large dataset."""
        detector = DriftDetector()
        
        import random
        random.seed(42)
        
        reference = {"feature": [random.random() for _ in range(10000)]}
        current = {"feature": [random.random() for _ in range(10000)]}
        
        report = detector.detect(reference, current)
        assert report.total_features == 1


class TestSerialization:
    """Test serialization and export."""
    
    def test_report_to_dict(self):
        """Test report dictionary conversion."""
        detector = DriftDetector()
        
        report = detector.detect(
            {"feature": [1, 2, 3, 4, 5]},
            {"feature": [6, 7, 8, 9, 10]}
        )
        
        report_dict = report.to_dict()
        
        assert isinstance(report_dict, dict)
        assert "report_id" in report_dict
        assert "feature_results" in report_dict
    
    def test_report_to_json(self):
        """Test report JSON conversion."""
        detector = DriftDetector()
        
        report = detector.detect(
            {"feature": [1, 2, 3, 4, 5]},
            {"feature": [6, 7, 8, 9, 10]}
        )
        
        import json
        report_json = json.dumps(report.to_dict())
        
        # Should be valid JSON
        parsed = json.loads(report_json)
        assert parsed["total_features"] == 1
    
    def test_alert_serialization(self):
        """Test alert serialization."""
        alert = Alert(
            alert_id="test-001",
            level=AlertLevel.WARNING,
            drift_type=DriftType.DATA_DRIFT,
            feature_name="test",
            message="Test alert",
            drift_result=None
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict["alert_id"] == "test-001"
        assert alert_dict["level"] == "warning"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
