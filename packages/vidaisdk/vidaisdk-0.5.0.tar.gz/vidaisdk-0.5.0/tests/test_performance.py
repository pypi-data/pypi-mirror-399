"""Tests for performance tracking."""

import pytest
import time
from unittest.mock import patch

from vidai.performance import PerformanceTracker, PerformanceInfo, track_performance
from vidai.exceptions import PerformanceError


class TestPerformanceTracker:
    """Test PerformanceTracker class."""
    
    def test_init_enabled(self):
        """Test initializing enabled tracker."""
        tracker = PerformanceTracker(enabled=True)
        assert tracker.enabled is True
        assert tracker._start_time is None
        assert tracker._operation_start_times == {}
    
    def test_init_disabled(self):
        """Test initializing disabled tracker."""
        tracker = PerformanceTracker(enabled=False)
        assert tracker.enabled is False
        assert tracker._start_time is None
        assert tracker._operation_start_times == {}
    
    def test_start_tracking_enabled(self):
        """Test starting tracking when enabled."""
        tracker = PerformanceTracker(enabled=True)
        
        tracker.start_tracking()
        
        assert tracker._start_time is not None
        assert isinstance(tracker._start_time, float)
    
    def test_start_tracking_disabled(self):
        """Test starting tracking when disabled."""
        tracker = PerformanceTracker(enabled=False)
        
        tracker.start_tracking()
        
        assert tracker._start_time is None
    
    def test_start_operation_enabled(self):
        """Test starting operation when enabled."""
        tracker = PerformanceTracker(enabled=True)
        
        tracker.start_operation("test_operation")
        
        assert "test_operation" in tracker._operation_start_times
        assert isinstance(tracker._operation_start_times["test_operation"], float)
    
    def test_start_operation_disabled(self):
        """Test starting operation when disabled."""
        tracker = PerformanceTracker(enabled=False)
        
        tracker.start_operation("test_operation")
        
        assert "test_operation" not in tracker._operation_start_times
    
    def test_end_operation_success(self):
        """Test ending operation successfully."""
        tracker = PerformanceTracker(enabled=True)
        tracker.start_operation("test_operation")
        
        # Small delay to ensure measurable time
        time.sleep(0.001)
        
        duration = tracker.end_operation("test_operation")
        
        assert duration > 0
        assert "test_operation" not in tracker._operation_start_times
        assert isinstance(duration, float)
    
    def test_end_operation_disabled(self):
        """Test ending operation when disabled."""
        tracker = PerformanceTracker(enabled=False)
        
        duration = tracker.end_operation("test_operation")
        
        assert duration == 0.0
    
    def test_end_operation_not_started(self):
        """Test ending operation that was not started."""
        tracker = PerformanceTracker(enabled=True)
        
        with pytest.raises(PerformanceError, match="Operation 'test_operation' was not started"):
            tracker.end_operation("test_operation")
    
    def test_end_tracking_enabled(self):
        """Test ending tracking when enabled."""
        tracker = PerformanceTracker(enabled=True)
        tracker.start_tracking()
        
        # Small delay to ensure measurable time
        time.sleep(0.001)
        
        perf_info = tracker.end_tracking()
        
        assert isinstance(perf_info, PerformanceInfo)
        assert perf_info.total_sdk_overhead_ms is not None
        assert perf_info.total_sdk_overhead_ms > 0
        assert tracker._start_time is None
    
    def test_end_tracking_disabled(self):
        """Test ending tracking when disabled."""
        tracker = PerformanceTracker(enabled=False)
        tracker.start_tracking()  # Should do nothing
        
        perf_info = tracker.end_tracking()
        
        assert isinstance(perf_info, PerformanceInfo)
        assert perf_info.total_sdk_overhead_ms is None
    
    def test_end_tracking_not_started(self):
        """Test ending tracking when not started."""
        tracker = PerformanceTracker(enabled=True)
        
        with pytest.raises(PerformanceError, match="Tracking was not started"):
            tracker.end_tracking()
    
    def test_track_function_enabled(self):
        """Test tracking function when enabled."""
        tracker = PerformanceTracker(enabled=True)
        
        def test_function(x, y):
            return x + y
        
        result, duration = tracker.track_function("test_op", test_function, 2, 3)
        
        assert result == 5
        assert duration > 0
        assert isinstance(duration, float)
    
    def test_track_function_disabled(self):
        """Test tracking function when disabled."""
        tracker = PerformanceTracker(enabled=False)
        
        def test_function(x, y):
            return x + y
        
        result, duration = tracker.track_function("test_op", test_function, 2, 3)
        
        assert result == 5
        assert duration == 0.0
    
    def test_track_function_exception(self):
        """Test tracking function that raises exception."""
        tracker = PerformanceTracker(enabled=True)
        
        def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            tracker.track_function("test_op", test_function)
    
    def test_multiple_operations(self):
        """Test tracking multiple operations."""
        tracker = PerformanceTracker(enabled=True)
        tracker.start_tracking()
        
        # Start multiple operations
        tracker.start_operation("op1")
        time.sleep(0.001)
        tracker.start_operation("op2")
        time.sleep(0.001)
        
        # End operations in reverse order
        duration2 = tracker.end_operation("op2")
        duration1 = tracker.end_operation("op1")
        
        assert duration1 > 0
        assert duration2 > 0
        assert duration2 < duration1  # op2 was shorter
        
        # End overall tracking
        perf_info = tracker.end_tracking()
        assert perf_info.total_sdk_overhead_ms > duration1


class TestTrackPerformanceDecorator:
    """Test track_performance decorator."""
    
    def test_decorator_enabled(self):
        """Test decorator when enabled."""
        @track_performance("test_operation", enabled=True)
        def test_function(x, y):
            time.sleep(0.001)
            return x + y
        
        result, duration = test_function(2, 3)
        
        assert result == 5
        assert duration > 0
        assert isinstance(duration, float)
    
    def test_decorator_disabled(self):
        """Test decorator when disabled."""
        @track_performance("test_operation", enabled=False)
        def test_function(x, y):
            return x + y
        
        result, duration = test_function(2, 3)
        
        assert result == 5
        assert duration == 0.0
    
    def test_decorator_exception(self):
        """Test decorator with function exception."""
        @track_performance("test_operation", enabled=True)
        def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            test_function()
    
    def test_decorator_no_args(self):
        """Test decorator with no arguments."""
        @track_performance("test_operation", enabled=True)
        def test_function():
            return "test"
        
        result, duration = test_function()
        
        assert result == "test"
        assert duration >= 0
    
    def test_decorator_with_args_kwargs(self):
        """Test decorator with various arguments."""
        @track_performance("test_operation", enabled=True)
        def test_function(a, b, c=None, d=None):
            return a + b + (c or 0) + (d or 0)
        
        result, duration = test_function(1, 2, c=3, d=4)
        
        assert result == 10
        assert duration >= 0


class TestPerformanceInfo:
    """Test PerformanceInfo class."""
    
    def test_default_init(self):
        """Test default initialization."""
        perf_info = PerformanceInfo()
        
        assert perf_info.request_transformation_time_ms is None
        assert perf_info.json_repair_time_ms is None
        assert perf_info.total_sdk_overhead_ms is None
    
    def test_init_with_values(self):
        """Test initialization with values."""
        perf_info = PerformanceInfo(
            request_transformation_time_ms=1.5,
            json_repair_time_ms=2.3,
            total_sdk_overhead_ms=5.8
        )
        
        assert perf_info.request_transformation_time_ms == 1.5
        assert perf_info.json_repair_time_ms == 2.3
        assert perf_info.total_sdk_overhead_ms == 5.8
    
    def test_equality(self):
        """Test PerformanceInfo equality."""
        perf1 = PerformanceInfo(total_sdk_overhead_ms=5.0)
        perf2 = PerformanceInfo(total_sdk_overhead_ms=5.0)
        perf3 = PerformanceInfo(total_sdk_overhead_ms=6.0)
        
        # PerformanceInfo is a dataclass, so they should be equal
        assert perf1 == perf2
        assert perf1 != perf3
    
    def test_repr(self):
        """Test PerformanceInfo string representation."""
        perf_info = PerformanceInfo(
            request_transformation_time_ms=1.5,
            json_repair_time_ms=2.3,
            total_sdk_overhead_ms=5.8
        )
        
        repr_str = repr(perf_info)
        assert "PerformanceInfo(" in repr_str
        assert "request_transformation_time_ms=1.5" in repr_str
        assert "json_repair_time_ms=2.3" in repr_str
        assert "total_sdk_overhead_ms=5.8" in repr_str