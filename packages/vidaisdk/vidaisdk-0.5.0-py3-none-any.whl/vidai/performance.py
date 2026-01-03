"""Performance tracking utilities for Vidai."""

import time
from typing import Any, Dict, Optional, Tuple, TypeVar, Callable
from dataclasses import dataclass

from .exceptions import PerformanceError

T = TypeVar("T")


@dataclass
class PerformanceInfo:
    """Performance tracking information."""
    request_transformation_time_ms: Optional[float] = None
    json_repair_time_ms: Optional[float] = None
    total_sdk_overhead_ms: Optional[float] = None


class PerformanceTracker:
    """Tracks performance metrics for SDK operations."""
    
    def __init__(self, enabled: bool = True) -> None:
        """Initialize performance tracker.
        
        Args:
            enabled: Whether performance tracking is enabled
        """
        self.enabled = enabled
        self._start_time: Optional[float] = None
        self._operation_start_times: Dict[str, float] = {}
    
    def start_tracking(self) -> None:
        """Start tracking total SDK overhead."""
        if not self.enabled:
            return
        
        self._start_time = time.perf_counter()
    
    def start_operation(self, operation_name: str) -> None:
        """Start timing a specific operation.
        
        Args:
            operation_name: Name of the operation to track
        """
        if not self.enabled:
            return
        
        self._operation_start_times[operation_name] = time.perf_counter()
    
    def end_operation(self, operation_name: str) -> float:
        """End timing a specific operation and return duration in milliseconds.
        
        Args:
            operation_name: Name of the operation to end
            
        Returns:
            Duration in milliseconds, or 0 if tracking disabled
            
        Raises:
            PerformanceError: If operation was not started
        """
        if not self.enabled:
            return 0.0
        
        if operation_name not in self._operation_start_times:
            raise PerformanceError(
                f"Operation {operation_name!r} was not started",
                operation=operation_name
            )
        
        start_time = self._operation_start_times.pop(operation_name)
        end_time = time.perf_counter()
        return (end_time - start_time) * 1000
    
    def end_tracking(self) -> PerformanceInfo:
        """End tracking and return performance information.
        
        Returns:
            PerformanceInfo with timing data
        """
        if not self.enabled:
            return PerformanceInfo()
        
        if self._start_time is None:
            raise PerformanceError("Tracking was not started")
        
        end_time = time.perf_counter()
        total_overhead = (end_time - self._start_time) * 1000
        self._start_time = None
        
        return PerformanceInfo(
            total_sdk_overhead_ms=total_overhead
        )
    
    def track_function(
        self,
        operation_name: str,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> Tuple[T, float]:
        """Track execution time of a function.
        
        Args:
            operation_name: Name of the operation for tracking
            func: Function to execute and track
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Tuple of (function_result, execution_time_ms)
        """
        if not self.enabled:
            return func(*args, **kwargs), 0.0
        
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
        
        execution_time_ms = (end_time - start_time) * 1000
        return result, execution_time_ms


def track_performance(operation_name: str, enabled: bool = True):
    """Decorator to track function performance.
    
    Args:
        operation_name: Name of the operation for tracking
        enabled: Whether tracking is enabled
        
    Returns:
        Decorated function that returns (result, timing_ms)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Tuple[T, float]]:
        def wrapper(*args, **kwargs) -> Tuple[T, float]:
            if not enabled:
                return func(*args, **kwargs), 0.0
            
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            finally:
                end_time = time.perf_counter()
            
            execution_time_ms = (end_time - start_time) * 1000
            return result, execution_time_ms
        
        return wrapper
    return decorator