#!/usr/bin/env python3
"""
MLE Runtime Command Line Interface

Provides command-line tools for working with MLE models.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from . import (
    load_model, 
    export_model, 
    inspect_model, 
    benchmark_model,
    get_version_info,
    get_supported_operators,
    get_system_performance_info
)


def cmd_version():
    """Show version information"""
    info = get_version_info()
    print(f"MLE Runtime {info['version']}")
    print(f"C++ Core Available: {info['cpp_core_available']}")
    
    if 'system_info' in info:
        sys_info = info['system_info']
        print(f"CPU: {sys_info.get('cpu_name', 'Unknown')}")
        print(f"Cores: {sys_info.get('cpu_cores', 'Unknown')}")
        print(f"CUDA Available: {sys_info.get('cuda_available', False)}")


def cmd_inspect(model_path: str):
    """Inspect a model file"""
    try:
        info = inspect_model(model_path)
        print(f"Model: {model_path}")
        print(f"File Size: {info.get('file_size_bytes', 0)} bytes")
        print(f"Version: {info.get('version', 'Unknown')}")
        
        metadata = info.get('model_metadata', {})
        if metadata:
            print("Metadata:")
            for key, value in metadata.items():
                if isinstance(value, (list, dict)):
                    print(f"  {key}: {type(value).__name__} ({len(value)} items)")
                else:
                    print(f"  {key}: {value}")
        
        engines = info.get('engines_available', {})
        print(f"Engines Available:")
        print(f"  C++: {engines.get('cpp', False)}")
        print(f"  Python: {engines.get('python', False)}")
        
    except Exception as e:
        print(f"Error inspecting model: {e}", file=sys.stderr)
        return 1
    
    return 0


def cmd_benchmark(model_path: str, num_runs: int = 100):
    """Benchmark a model"""
    try:
        import numpy as np
        
        # Create dummy input data
        test_input = [np.random.randn(10, 20).astype(np.float32)]
        
        print(f"Benchmarking {model_path} with {num_runs} runs...")
        results = benchmark_model(model_path, test_input, num_runs)
        
        if 'python_results' in results:
            py_results = results['python_results']
            print(f"Python Engine:")
            print(f"  Mean Time: {py_results['mean_time_ms']:.2f} ms")
            print(f"  Std Dev: {py_results['std_time_ms']:.2f} ms")
            print(f"  Min Time: {py_results['min_time_ms']:.2f} ms")
            print(f"  Max Time: {py_results['max_time_ms']:.2f} ms")
            print(f"  Throughput: {py_results['throughput_ops_per_sec']:.1f} ops/sec")
        
        if 'cpp_results' in results and results['cpp_results']:
            cpp_results = results['cpp_results']
            print(f"C++ Engine:")
            print(f"  Mean Time: {cpp_results['mean_time_ms']:.2f} ms")
            print(f"  Std Dev: {cpp_results['std_time_ms']:.2f} ms")
            print(f"  Min Time: {cpp_results['min_time_ms']:.2f} ms")
            print(f"  Max Time: {cpp_results['max_time_ms']:.2f} ms")
            print(f"  Throughput: {cpp_results['throughput_ops_per_sec']:.1f} ops/sec")
        
        if 'comparison' in results and results['comparison']:
            comp = results['comparison']
            print(f"Performance Comparison:")
            print(f"  Speedup Factor: {comp['speedup_factor']:.1f}x")
            print(f"  C++ Faster: {comp['cpp_faster']}")
            print(f"  Performance Gain: {comp['performance_gain_percent']:.1f}%")
        
    except Exception as e:
        print(f"Error benchmarking model: {e}", file=sys.stderr)
        return 1
    
    return 0


def cmd_operators():
    """List supported operators"""
    operators = get_supported_operators()
    print(f"Supported Operators ({len(operators)}):")
    
    # Group operators by category
    categories = {
        'Neural Network': [],
        'Classical ML': [],
        'Advanced': []
    }
    
    for op in operators:
        if op in ['Linear', 'ReLU', 'GELU', 'Softmax', 'LayerNorm', 'MatMul', 'Add', 'Mul',
                  'Conv2D', 'MaxPool2D', 'BatchNorm', 'Dropout', 'Embedding', 'Attention']:
            categories['Neural Network'].append(op)
        elif op in ['DecisionTree', 'TreeEnsemble', 'GradientBoosting', 'SVM', 'NaiveBayes',
                    'KNN', 'Clustering', 'DBSCAN', 'Decomposition']:
            categories['Classical ML'].append(op)
        else:
            categories['Advanced'].append(op)
    
    for category, ops in categories.items():
        if ops:
            print(f"\n{category}:")
            for op in sorted(ops):
                print(f"  - {op}")


def cmd_system_info():
    """Show system information"""
    info = get_system_performance_info()
    
    print("System Information:")
    print(f"  C++ Core Available: {info['cpp_core_available']}")
    print(f"  Fallback Active: {info['fallback_active']}")
    
    if 'system_info' in info:
        sys_info = info['system_info']
        print(f"  CPU: {sys_info.get('cpu_name', 'Unknown')}")
        print(f"  CPU Cores: {sys_info.get('cpu_cores', 'Unknown')}")
        print(f"  AVX2 Support: {sys_info.get('avx2_support', False)}")
        print(f"  CUDA Available: {sys_info.get('cuda_available', False)}")
    
    perf_monitor = info.get('performance_monitor', {})
    if perf_monitor:
        print(f"\nPerformance Monitor:")
        print(f"  Total Executions: {perf_monitor.get('total_executions', 0)}")
        if 'average_execution_time_ms' in perf_monitor:
            print(f"  Average Execution Time: {perf_monitor['average_execution_time_ms']:.2f} ms")
        if 'cpp_core_usage_rate' in perf_monitor:
            print(f"  C++ Core Usage Rate: {perf_monitor['cpp_core_usage_rate']:.1%}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='mle-runtime',
        description='MLE Runtime - High-Performance Machine Learning Inference Engine'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Version command
    subparsers.add_parser('version', help='Show version information')
    
    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect a model file')
    inspect_parser.add_argument('model_path', help='Path to the .mle model file')
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser('benchmark', help='Benchmark a model')
    benchmark_parser.add_argument('model_path', help='Path to the .mle model file')
    benchmark_parser.add_argument('--runs', type=int, default=100, help='Number of benchmark runs')
    
    # Operators command
    subparsers.add_parser('operators', help='List supported operators')
    
    # System info command
    subparsers.add_parser('system-info', help='Show system information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'version':
            cmd_version()
            return 0
        elif args.command == 'inspect':
            return cmd_inspect(args.model_path)
        elif args.command == 'benchmark':
            return cmd_benchmark(args.model_path, args.runs)
        elif args.command == 'operators':
            cmd_operators()
            return 0
        elif args.command == 'system-info':
            cmd_system_info()
            return 0
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
    
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())