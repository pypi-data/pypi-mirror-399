import time
import psutil
import os
from typing import Callable, Dict, Any
from functools import wraps
import json

class PerformanceProfiler:
    """Performance profiling tool"""
    
    def __init__(self):
        self.results = {}
        self.process = psutil.Process(os.getpid())
    
    def profile_4d(self, func: Callable = None, name: str = None):
        """Profile 4D operation"""
        
        def decorator(f:  Callable):
            @wraps(f)
            def wrapper(*args, **kwargs):
                profile_name = name or f.__name__
                
                start_time = time.time()
                start_memory = self.process.memory_info().rss / 1024 / 1024
                
                result = f(*args, **kwargs)
                
                end_time = time.time()
                end_memory = self.process.memory_info().rss / 1024 / 1024
                
                elapsed = end_time - start_time
                memory_used = end_memory - start_memory
                
                self.results[profile_name] = {
                    "execution_time_seconds": elapsed,
                    "memory_used_mb": memory_used,
                }
                
                return result
            
            return wrapper
        
        if func is None:
            return decorator
        else:
            return decorator(func)
    
    def print_report(self) -> None:
        """Print performance report"""
        
        print("\n" + "=" * 80)
        print("PERFORMANCE REPORT")
        print("=" * 80 + "\n")
        
        for func_name, metrics in sorted(
            self.results.items(),
            key=lambda x: x[1]["execution_time_seconds"],
            reverse=True,
        ):
            print(f"{func_name}:")
            print(f"  Time: {metrics['execution_time_seconds']:.4f}s")
            print(f"  Memory: {metrics['memory_used_mb']:.2f} MB\n")
        
        print("=" * 80 + "\n")
    
    def export_report(self, filename: str = "profile_report.json") -> None:
        """Export performance report"""
        
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)

profiler = PerformanceProfiler()

def profile_function(name: str = None):
    """Decorator to profile a function"""
    return profiler.profile_4d(name=name)