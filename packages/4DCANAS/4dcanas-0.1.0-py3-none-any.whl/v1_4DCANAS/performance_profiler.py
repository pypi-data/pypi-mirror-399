"""
محلل الأداء الشامل
Comprehensive Performance Profiler

الإصدار: 1.0.0
Version: 1.0.0

المطور:  MERO
Developer: MERO

جميع الحقوق محفوظة © 2025 MERO
All Rights Reserved © 2025 MERO
"""

import time
import psutil
import os
import tracemalloc
from typing import Callable, Dict, Any, List, Optional
from functools import wraps
import numpy as np
import json
from datetime import datetime

class PerformanceProfiler: 
    
    def __init__(self):
        self.results = {}
        self.process = psutil.Process(os.getpid())
        self.version = "1.0.0"
        self.developer = "MERO"
    
    def profile_4d(self, func: Callable = None, name: Optional[str] = None):
        
        def decorator(f:  Callable):
            @wraps(f)
            def wrapper(*args, **kwargs):
                profile_name = name or f.__name__
                
                tracemalloc.start()
                start_time = time.time()
                start_cpu = self.process.cpu_percent()
                start_memory = self.process.memory_info().rss / 1024 / 1024
                
                result = f(*args, **kwargs)
                
                end_time = time.time()
                end_cpu = self.process.cpu_percent()
                end_memory = self.process.memory_info().rss / 1024 / 1024
                
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                elapsed = end_time - start_time
                cpu_used = end_cpu - start_cpu
                memory_used = end_memory - start_memory
                memory_peak = peak / 1024 / 1024
                
                self.results[profile_name] = {
                    'execution_time_seconds': elapsed,
                    'cpu_percent': cpu_used,
                    'memory_used_mb': memory_used,
                    'peak_memory_mb': memory_peak,
                    'timestamp': datetime.now().isoformat()
                }
                
                return result
            
            return wrapper
        
        if func is None:
            return decorator
        else:
            return decorator(func)
    
    def get_report(self) -> Dict[str, Any]:
        
        report = {
            'profiling_results': self.results,
            'summary': {
                'total_functions': len(self.results),
                'total_time':  sum(r['execution_time_seconds'] for r in self.results.values()),
                'total_memory': sum(r['memory_used_mb'] for r in self. results.values()),
                'peak_memory': max([r['peak_memory_mb'] for r in self.results.values()], default=0)
            },
            'bottlenecks': self._find_bottlenecks(),
            'optimization_suggestions': self._suggest_optimizations()
        }
        
        return report
    
    def _find_bottlenecks(self) -> List[Dict[str, Any]]:
        
        bottlenecks = []
        
        for func_name, metrics in self.results.items():
            if metrics['execution_time_seconds'] > 1.0:
                bottlenecks.append({
                    'function': func_name,
                    'time':  metrics['execution_time_seconds'],
                    'issue': 'بطء في التنفيذ | Slow execution'
                })
            
            if metrics['peak_memory_mb'] > 500:
                bottlenecks. append({
                    'function':  func_name,
                    'memory': metrics['peak_memory_mb'],
                    'issue': 'استهلاك عالي للذاكرة | High memory usage'
                })
        
        return bottlenecks
    
    def _suggest_optimizations(self) -> List[str]:
        
        suggestions = []
        
        slow_functions = [
            name for name, metrics in self.results.items()
            if metrics['execution_time_seconds'] > 1.0
        ]
        
        if slow_functions: 
            suggestions.append(
                f"تحسين الدوال البطيئة: {', '.join(slow_functions)} | "
                f"Optimize slow functions: {', '.join(slow_functions)}"
            )
        
        high_memory = [
            name for name, metrics in self.results.items()
            if metrics['peak_memory_mb'] > 500
        ]
        
        if high_memory:
            suggestions. append(
                f"تقليل استهلاك الذاكرة في:  {', '.join(high_memory)} | "
                f"Reduce memory usage in: {', '. join(high_memory)}"
            )
        
        if len(self.results) > 20:
            suggestions.append(
                "قسّم العمليات الكبيرة إلى وحدات أصغر | Break large operations into smaller units"
            )
        
        return suggestions
    
    def print_report(self):
        
        report = self.get_report()
        
        print("\n" + "="*80)
        print("تقرير الأداء | PERFORMANCE REPORT")
        print("="*80 + "\n")
        
        print(f"إجمالي الوقت | Total Time: {report['summary']['total_time']:.3f} ثانية | seconds")
        print(f"إجمالي الذاكرة | Total Memory: {report['summary']['total_memory']:. 2f} MB")
        print(f"ذاكرة الذروة | Peak Memory: {report['summary']['peak_memory']:.2f} MB\n")
        
        print("تفاصيل الدوال | FUNCTION DETAILS:")
        print("-" * 80)
        
        for func_name, metrics in sorted(report['profiling_results']. items(),
                                        key=lambda x: x[1]['execution_time_seconds'],
                                        reverse=True):
            print(f"\n{func_name}:")
            print(f"  الوقت | Time: {metrics['execution_time_seconds']:.4f}s")
            print(f"  وحدة المعالجة المركزية | CPU: {metrics['cpu_percent']:.2f}%")
            print(f"  الذاكرة | Memory: {metrics['memory_used_mb']:.2f} MB")
        
        if report['bottlenecks']: 
            print("\n\nنقاط الاختناق | BOTTLENECKS:")
            print("-" * 80)
            for bn in report['bottlenecks']: 
                print(f"  {bn['function']}: {bn['issue']}")
        
        if report['optimization_suggestions']:
            print("\n\nاقتراحات التحسين | OPTIMIZATION SUGGESTIONS:")
            print("-" * 80)
            for i, sugg in enumerate(report['optimization_suggestions'], 1):
                print(f"  {i}.  {sugg}")
        
        print("\n" + "="*80 + "\n")
    
    def export_report(self, filename: str = "profile_report.json"):
        
        report = self.get_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


profiler = PerformanceProfiler()


def profile_function(name: Optional[str] = None):
    return profiler.profile_4d(name=name)