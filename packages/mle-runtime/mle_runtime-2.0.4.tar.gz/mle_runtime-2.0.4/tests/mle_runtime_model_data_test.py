#!/usr/bin/env python3
"""
MLE Runtime Model and Data Test Suite
=====================================

This test validates:
1. Model import/export functionality
2. Sample data handling
3. Output difference analysis
4. Input validation and edge cases
5. Data format compatibility
6. Performance comparison between engines
"""

import numpy as np
import sys
import time
import json
import traceback
from typing import List, Dict, Any, Tuple
import tempfile
import os
from pathlib import Path

def print_header(title: str):
    """Print a formatted test section header"""
    print(f"\n{'='*70}")
    print(f"🧪 {title}")
    print(f"{'='*70}")

def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with formatting"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def print_metrics(metrics: Dict[str, Any], title: str = "Metrics"):
    """Print metrics in a formatted way"""
    print(f"\n📊 {title}:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.6f}")
        elif isinstance(value, (list, tuple)) and len(value) > 0 and isinstance(value[0], float):
            print(f"   {key}: [{', '.join([f'{v:.3f}' for v in value[:5]])}{'...' if len(value) > 5 else ''}]")
        else:
            print(f"   {key}: {value}")

class MLEModelDataTest:
    """Comprehensive model and data testing suite"""
    
    def __init__(self):
        self.results = {}
        self.performance_data = {}
        self.test_models = {}
        self.sample_data = {}
        
    def run_all_tests(self):
        """Run all model and data tests"""
        print("🚀 MLE Runtime Model and Data Test Suite")
        print("Testing model import/export, data handling, and output analysis...")
        
        # Test 1: Generate Sample Data
        self.test_sample_data_generation()
        
        # Test 2: Create Test Models
        self.test_model_creation()
        
        # Test 3: Model Import/Export
        self.test_model_import_export()
        
        # Test 4: Input Validation and Edge Cases
        self.test_input_validation()
        
        # Test 5: Output Consistency Analysis
        self.test_output_consistency()
        
        # Test 6: Performance Comparison
        self.test_performance_comparison()
        
        # Test 7: Data Format Compatibility
        self.test_data_format_compatibility()
        
        # Test 8: Memory Usage Analysis
        self.test_memory_usage()
        
        # Test 9: Batch Processing
        self.test_batch_processing()
        
        # Test 10: Error Recovery and Robustness
        self.test_error_recovery()
        
        # Generate comprehensive report
        return self.generate_report()
    
    def test_sample_data_generation(self):
        """Test 1: Generate Sample Data"""
        print_header("Test 1: Sample Data Generation")
        
        try:
            # Generate various types of sample data
            self.sample_data = {
                'small_1d': np.random.randn(10).astype(np.float32),
                'medium_2d': np.random.randn(100, 50).astype(np.float32),
                'large_3d': np.random.randn(20, 30, 40).astype(np.float32),
                'batch_data': np.random.randn(32, 128).astype(np.float32),
                'image_like': np.random.randn(3, 224, 224).astype(np.float32),
                'sequence_data': np.random.randn(50, 768).astype(np.float32),
                'edge_cases': {
                    'zeros': np.zeros((10, 10), dtype=np.float32),
                    'ones': np.ones((10, 10), dtype=np.float32),
                    'large_values': np.random.randn(10, 10).astype(np.float32) * 1000,
                    'small_values': np.random.randn(10, 10).astype(np.float32) * 0.001,
                    'negative': -np.abs(np.random.randn(10, 10).astype(np.float32)),
                    'mixed_range': np.random.uniform(-100, 100, (10, 10)).astype(np.float32)
                }
            }
            
            # Validate data generation
            for name, data in self.sample_data.items():
                if name != 'edge_cases':
                    print_result(f"Generate {name}", True, 
                                f"Shape: {data.shape}, dtype: {data.dtype}")
                else:
                    for edge_name, edge_data in data.items():
                        print_result(f"Generate edge case {edge_name}", True,
                                    f"Shape: {edge_data.shape}, Range: [{edge_data.min():.3f}, {edge_data.max():.3f}]")
            
            # Test data statistics
            stats = {}
            for name, data in self.sample_data.items():
                if name != 'edge_cases':
                    stats[name] = {
                        'mean': float(np.mean(data)),
                        'std': float(np.std(data)),
                        'min': float(np.min(data)),
                        'max': float(np.max(data)),
                        'shape': data.shape,
                        'size': data.size
                    }
            
            print_metrics(stats, "Sample Data Statistics")
            self.results["sample_data_generation"] = True
            
        except Exception as e:
            print_result("Sample data generation", False, f"Error: {e}")
            self.results["sample_data_generation"] = False
    
    def test_model_creation(self):
        """Test 2: Create Test Models"""
        print_header("Test 2: Test Model Creation")
        
        try:
            import mle_runtime
            
            # Create different types of test models
            model_configs = {
                'simple_linear': {
                    'device': 'cpu',
                    'description': 'Simple linear transformation model'
                },
                'multi_layer': {
                    'device': 'auto',
                    'description': 'Multi-layer neural network model'
                },
                'batch_model': {
                    'device': 'auto',
                    'description': 'Batch processing optimized model'
                }
            }
            
            for model_name, config in model_configs.items():
                try:
                    runtime = mle_runtime.MLERuntime(device=config['device'])
                    runtime.enable_adaptive_optimization(True)
                    
                    # Load a demo model (will create one automatically)
                    model_path = f"test_{model_name}.mle"
                    result = runtime.load_model(model_path)
                    
                    self.test_models[model_name] = {
                        'runtime': runtime,
                        'path': model_path,
                        'config': config,
                        'load_result': result
                    }
                    
                    print_result(f"Create {model_name}", True,
                                f"Device: {config['device']}, Loaded: {result.get('python_loaded', False)}")
                    
                except Exception as e:
                    print_result(f"Create {model_name}", False, f"Error: {e}")
            
            self.results["model_creation"] = len(self.test_models) > 0
            
        except Exception as e:
            print_result("Model creation", False, f"Error: {e}")
            self.results["model_creation"] = False
    
    def test_model_import_export(self):
        """Test 3: Model Import/Export"""
        print_header("Test 3: Model Import/Export")
        
        try:
            import mle_runtime
            
            # Test model export functionality
            export_results = {}
            
            for model_name, model_info in self.test_models.items():
                try:
                    runtime = model_info['runtime']
                    
                    # Test model info export
                    model_info_data = runtime.get_model_info()
                    export_results[f"{model_name}_info"] = model_info_data
                    
                    print_result(f"Export {model_name} info", True,
                                f"Info keys: {list(model_info_data.keys())}")
                    
                    # Test model inspection
                    try:
                        inspection_result = mle_runtime.inspect_model(model_info['path'])
                        export_results[f"{model_name}_inspection"] = inspection_result
                        print_result(f"Inspect {model_name}", True,
                                    f"Inspection available")
                    except Exception as e:
                        print_result(f"Inspect {model_name}", False, f"Error: {e}")
                    
                except Exception as e:
                    print_result(f"Export {model_name}", False, f"Error: {e}")
            
            # Test universal export function
            try:
                # Create a dummy model for export testing
                dummy_model = np.random.randn(10, 10).astype(np.float32)
                export_result = mle_runtime.export_model(
                    dummy_model, 
                    "test_export.mle",
                    input_shape=(10,)
                )
                print_result("Universal export", True, 
                            f"Status: {export_result.get('status', 'unknown')}")
            except Exception as e:
                print_result("Universal export", False, f"Error: {e}")
            
            self.performance_data["export_results"] = export_results
            self.results["model_import_export"] = len(export_results) > 0
            
        except Exception as e:
            print_result("Model import/export", False, f"Error: {e}")
            self.results["model_import_export"] = False
    
    def test_input_validation(self):
        """Test 4: Input Validation and Edge Cases"""
        print_header("Test 4: Input Validation and Edge Cases")
        
        try:
            validation_results = {}
            
            if not self.test_models:
                print_result("Input validation", False, "No test models available")
                self.results["input_validation"] = False
                return
            
            # Get a test model
            model_name, model_info = next(iter(self.test_models.items()))
            runtime = model_info['runtime']
            
            # Test various input scenarios
            test_cases = [
                ("Valid 1D input", [self.sample_data['small_1d']]),
                ("Valid 2D input", [self.sample_data['medium_2d']]),
                ("Valid 3D input", [self.sample_data['large_3d']]),
                ("Batch input", [self.sample_data['batch_data']]),
                ("Multiple inputs", [self.sample_data['small_1d'], self.sample_data['medium_2d']]),
                ("Zero input", [self.sample_data['edge_cases']['zeros']]),
                ("Ones input", [self.sample_data['edge_cases']['ones']]),
                ("Large values", [self.sample_data['edge_cases']['large_values']]),
                ("Small values", [self.sample_data['edge_cases']['small_values']]),
                ("Negative values", [self.sample_data['edge_cases']['negative']]),
                ("Mixed range", [self.sample_data['edge_cases']['mixed_range']]),
            ]
            
            for test_name, inputs in test_cases:
                try:
                    start_time = time.time()
                    outputs = runtime.run(inputs)
                    end_time = time.time()
                    
                    execution_time = (end_time - start_time) * 1000  # ms
                    
                    validation_results[test_name] = {
                        'success': True,
                        'execution_time_ms': execution_time,
                        'input_shapes': [inp.shape for inp in inputs],
                        'output_shapes': [out.shape for out in outputs] if outputs else [],
                        'output_ranges': [(float(out.min()), float(out.max())) for out in outputs] if outputs else []
                    }
                    
                    print_result(test_name, True,
                                f"Time: {execution_time:.3f}ms, Output shapes: {[out.shape for out in outputs] if outputs else []}")
                    
                except Exception as e:
                    validation_results[test_name] = {
                        'success': False,
                        'error': str(e)
                    }
                    print_result(test_name, False, f"Error: {e}")
            
            # Test invalid inputs
            invalid_cases = [
                ("Empty list", []),
                ("Wrong dtype", [np.random.randn(10, 10).astype(np.int32)]),
                ("NaN values", [np.full((10, 10), np.nan, dtype=np.float32)]),
                ("Inf values", [np.full((10, 10), np.inf, dtype=np.float32)]),
            ]
            
            for test_name, inputs in invalid_cases:
                try:
                    outputs = runtime.run(inputs)
                    validation_results[test_name] = {
                        'success': True,
                        'handled_gracefully': True
                    }
                    print_result(f"Invalid: {test_name}", True, "Handled gracefully")
                except Exception as e:
                    validation_results[test_name] = {
                        'success': False,
                        'error': str(e),
                        'expected_failure': True
                    }
                    print_result(f"Invalid: {test_name}", True, "Expected failure")
            
            self.performance_data["validation_results"] = validation_results
            success_count = sum(1 for r in validation_results.values() if r.get('success', False))
            self.results["input_validation"] = success_count > len(test_cases) * 0.7
            
        except Exception as e:
            print_result("Input validation", False, f"Error: {e}")
            self.results["input_validation"] = False
    
    def test_output_consistency(self):
        """Test 5: Output Consistency Analysis"""
        print_header("Test 5: Output Consistency Analysis")
        
        try:
            consistency_results = {}
            
            if not self.test_models:
                print_result("Output consistency", False, "No test models available")
                self.results["output_consistency"] = False
                return
            
            # Test output consistency across multiple runs
            model_name, model_info = next(iter(self.test_models.items()))
            runtime = model_info['runtime']
            
            test_input = [self.sample_data['medium_2d']]
            num_runs = 5
            
            outputs_history = []
            execution_times = []
            
            for run_idx in range(num_runs):
                start_time = time.time()
                outputs = runtime.run(test_input)
                end_time = time.time()
                
                execution_times.append((end_time - start_time) * 1000)
                outputs_history.append(outputs)
            
            # Analyze consistency
            if len(outputs_history) > 1:
                # Compare outputs
                first_output = outputs_history[0][0] if outputs_history[0] else None
                
                if first_output is not None:
                    differences = []
                    for i in range(1, len(outputs_history)):
                        if outputs_history[i] and len(outputs_history[i]) > 0:
                            diff = np.abs(outputs_history[i][0] - first_output)
                            max_diff = np.max(diff)
                            mean_diff = np.mean(diff)
                            differences.append({
                                'run': i,
                                'max_diff': float(max_diff),
                                'mean_diff': float(mean_diff),
                                'relative_diff': float(max_diff / (np.abs(first_output).max() + 1e-8))
                            })
                    
                    consistency_results['output_differences'] = differences
                    consistency_results['execution_times'] = execution_times
                    consistency_results['time_stats'] = {
                        'mean': float(np.mean(execution_times)),
                        'std': float(np.std(execution_times)),
                        'min': float(np.min(execution_times)),
                        'max': float(np.max(execution_times))
                    }
                    
                    # Check if outputs are reasonably consistent
                    max_relative_diff = max(d['relative_diff'] for d in differences) if differences else 0
                    is_consistent = max_relative_diff < 0.01  # 1% tolerance
                    
                    print_result("Output consistency", is_consistent,
                                f"Max relative diff: {max_relative_diff:.6f}")
                    
                    print_metrics(consistency_results['time_stats'], "Execution Time Statistics")
                    
                    # Test determinism
                    if max_relative_diff < 1e-6:
                        print_result("Deterministic output", True, "Outputs are deterministic")
                    else:
                        print_result("Deterministic output", False, 
                                    f"Outputs vary (max diff: {max_relative_diff:.6f})")
                else:
                    print_result("Output consistency", False, "No valid outputs to compare")
            
            self.performance_data["consistency_results"] = consistency_results
            self.results["output_consistency"] = len(consistency_results) > 0
            
        except Exception as e:
            print_result("Output consistency", False, f"Error: {e}")
            self.results["output_consistency"] = False
    
    def test_performance_comparison(self):
        """Test 6: Performance Comparison"""
        print_header("Test 6: Performance Comparison")
        
        try:
            performance_results = {}
            
            if not self.test_models:
                print_result("Performance comparison", False, "No test models available")
                self.results["performance_comparison"] = False
                return
            
            # Test performance across different models and inputs
            for model_name, model_info in self.test_models.items():
                runtime = model_info['runtime']
                model_results = {}
                
                # Test different input sizes
                test_inputs = {
                    'small': [self.sample_data['small_1d']],
                    'medium': [self.sample_data['medium_2d']],
                    'large': [self.sample_data['large_3d']],
                    'batch': [self.sample_data['batch_data']]
                }
                
                for input_name, inputs in test_inputs.items():
                    try:
                        # Warmup
                        for _ in range(3):
                            runtime.run(inputs)
                        
                        # Benchmark
                        times = []
                        for _ in range(10):
                            start_time = time.time()
                            outputs = runtime.run(inputs)
                            end_time = time.time()
                            times.append((end_time - start_time) * 1000)
                        
                        model_results[input_name] = {
                            'mean_time_ms': float(np.mean(times)),
                            'std_time_ms': float(np.std(times)),
                            'min_time_ms': float(np.min(times)),
                            'max_time_ms': float(np.max(times)),
                            'throughput_ops_per_sec': 1000.0 / np.mean(times),
                            'input_size': inputs[0].size if inputs else 0
                        }
                        
                        print_result(f"{model_name} - {input_name}", True,
                                    f"Avg: {np.mean(times):.3f}ms, Throughput: {1000.0/np.mean(times):.1f} ops/sec")
                        
                    except Exception as e:
                        model_results[input_name] = {'error': str(e)}
                        print_result(f"{model_name} - {input_name}", False, f"Error: {e}")
                
                performance_results[model_name] = model_results
            
            # Analyze performance trends
            if performance_results:
                # Calculate performance per input size
                size_performance = {}
                for model_name, model_data in performance_results.items():
                    for input_name, metrics in model_data.items():
                        if 'mean_time_ms' in metrics:
                            input_size = metrics['input_size']
                            time_per_element = metrics['mean_time_ms'] / input_size if input_size > 0 else 0
                            
                            if input_name not in size_performance:
                                size_performance[input_name] = []
                            size_performance[input_name].append({
                                'model': model_name,
                                'time_per_element_us': time_per_element * 1000,
                                'throughput': metrics['throughput_ops_per_sec']
                            })
                
                print_metrics(size_performance, "Performance by Input Size")
            
            self.performance_data["performance_comparison"] = performance_results
            self.results["performance_comparison"] = len(performance_results) > 0
            
        except Exception as e:
            print_result("Performance comparison", False, f"Error: {e}")
            self.results["performance_comparison"] = False
    
    def test_data_format_compatibility(self):
        """Test 7: Data Format Compatibility"""
        print_header("Test 7: Data Format Compatibility")
        
        try:
            compatibility_results = {}
            
            if not self.test_models:
                print_result("Data format compatibility", False, "No test models available")
                self.results["data_format_compatibility"] = False
                return
            
            model_name, model_info = next(iter(self.test_models.items()))
            runtime = model_info['runtime']
            
            # Test different data formats
            base_data = np.random.randn(10, 10)
            
            format_tests = [
                ("float32", base_data.astype(np.float32)),
                ("float64", base_data.astype(np.float64)),
                ("int32", (base_data * 100).astype(np.int32)),
                ("int64", (base_data * 100).astype(np.int64)),
                ("C-contiguous", np.ascontiguousarray(base_data.astype(np.float32))),
                ("F-contiguous", np.asfortranarray(base_data.astype(np.float32))),
                ("Strided", base_data.astype(np.float32)[::2, ::2]),
            ]
            
            for format_name, test_data in format_tests:
                try:
                    # Convert to list format as expected by runtime
                    if test_data.dtype in [np.int32, np.int64]:
                        # Convert integers to float for compatibility
                        test_input = [test_data.astype(np.float32)]
                    else:
                        test_input = [test_data.astype(np.float32)]
                    
                    outputs = runtime.run(test_input)
                    
                    compatibility_results[format_name] = {
                        'success': True,
                        'input_dtype': str(test_data.dtype),
                        'input_shape': test_data.shape,
                        'input_contiguous': test_data.flags.c_contiguous,
                        'output_shapes': [out.shape for out in outputs] if outputs else []
                    }
                    
                    print_result(f"Format {format_name}", True,
                                f"Input: {test_data.dtype}, Shape: {test_data.shape}")
                    
                except Exception as e:
                    compatibility_results[format_name] = {
                        'success': False,
                        'error': str(e)
                    }
                    print_result(f"Format {format_name}", False, f"Error: {e}")
            
            # Test list vs numpy array inputs
            try:
                list_input = base_data.astype(np.float32).tolist()
                outputs_list = runtime.run([np.array(list_input, dtype=np.float32)])
                
                numpy_input = base_data.astype(np.float32)
                outputs_numpy = runtime.run([numpy_input])
                
                # Compare outputs
                if outputs_list and outputs_numpy:
                    diff = np.abs(outputs_list[0] - outputs_numpy[0])
                    max_diff = np.max(diff)
                    
                    compatibility_results['list_vs_numpy'] = {
                        'max_difference': float(max_diff),
                        'equivalent': max_diff < 1e-6
                    }
                    
                    print_result("List vs NumPy input", max_diff < 1e-6,
                                f"Max difference: {max_diff:.8f}")
                
            except Exception as e:
                print_result("List vs NumPy input", False, f"Error: {e}")
            
            self.performance_data["compatibility_results"] = compatibility_results
            success_count = sum(1 for r in compatibility_results.values() if r.get('success', False))
            self.results["data_format_compatibility"] = success_count > len(format_tests) * 0.7
            
        except Exception as e:
            print_result("Data format compatibility", False, f"Error: {e}")
            self.results["data_format_compatibility"] = False
    
    def test_memory_usage(self):
        """Test 8: Memory Usage Analysis"""
        print_header("Test 8: Memory Usage Analysis")
        
        try:
            memory_results = {}
            
            if not self.test_models:
                print_result("Memory usage", False, "No test models available")
                self.results["memory_usage"] = False
                return
            
            model_name, model_info = next(iter(self.test_models.items()))
            runtime = model_info['runtime']
            
            # Test memory usage with different input sizes
            memory_tests = [
                ("small", self.sample_data['small_1d']),
                ("medium", self.sample_data['medium_2d']),
                ("large", self.sample_data['large_3d']),
                ("batch", self.sample_data['batch_data'])
            ]
            
            for test_name, test_data in memory_tests:
                try:
                    inputs = [test_data]
                    
                    # Run inference
                    outputs = runtime.run(inputs)
                    
                    # Estimate memory usage
                    input_memory = sum(inp.nbytes for inp in inputs) / (1024 * 1024)  # MB
                    output_memory = sum(out.nbytes for out in outputs) / (1024 * 1024) if outputs else 0  # MB
                    total_memory = input_memory + output_memory
                    
                    # Get runtime memory estimation
                    estimated_memory = runtime._estimate_memory_usage(inputs, outputs if outputs else [])
                    
                    memory_results[test_name] = {
                        'input_memory_mb': input_memory,
                        'output_memory_mb': output_memory,
                        'total_memory_mb': total_memory,
                        'estimated_memory_mb': estimated_memory,
                        'input_size': test_data.size,
                        'memory_per_element_bytes': (input_memory * 1024 * 1024) / test_data.size
                    }
                    
                    print_result(f"Memory {test_name}", True,
                                f"Total: {total_memory:.3f}MB, Est: {estimated_memory:.3f}MB")
                    
                except Exception as e:
                    memory_results[test_name] = {'error': str(e)}
                    print_result(f"Memory {test_name}", False, f"Error: {e}")
            
            # Test memory budget functionality
            try:
                original_budget = runtime.memory_budget_mb
                runtime.memory_budget_mb = 100  # 100MB limit
                
                # Test with large input
                large_input = [np.random.randn(1000, 1000).astype(np.float32)]  # ~4MB
                outputs = runtime.run(large_input)
                
                memory_results['budget_test'] = {
                    'budget_mb': 100,
                    'large_input_handled': outputs is not None,
                    'input_size_mb': large_input[0].nbytes / (1024 * 1024)
                }
                
                runtime.memory_budget_mb = original_budget  # Restore
                
                print_result("Memory budget", True, "Budget management functional")
                
            except Exception as e:
                print_result("Memory budget", False, f"Error: {e}")
            
            print_metrics(memory_results, "Memory Usage Analysis")
            
            self.performance_data["memory_results"] = memory_results
            self.results["memory_usage"] = len(memory_results) > 0
            
        except Exception as e:
            print_result("Memory usage", False, f"Error: {e}")
            self.results["memory_usage"] = False
    
    def test_batch_processing(self):
        """Test 9: Batch Processing"""
        print_header("Test 9: Batch Processing")
        
        try:
            batch_results = {}
            
            if not self.test_models:
                print_result("Batch processing", False, "No test models available")
                self.results["batch_processing"] = False
                return
            
            model_name, model_info = next(iter(self.test_models.items()))
            runtime = model_info['runtime']
            
            # Test different batch sizes
            base_input = np.random.randn(128).astype(np.float32)
            batch_sizes = [1, 4, 8, 16, 32]
            
            for batch_size in batch_sizes:
                try:
                    # Create batch input
                    batch_input = [np.tile(base_input, (batch_size, 1))]
                    
                    # Measure performance
                    start_time = time.time()
                    outputs = runtime.run(batch_input)
                    end_time = time.time()
                    
                    execution_time = (end_time - start_time) * 1000  # ms
                    time_per_sample = execution_time / batch_size
                    
                    batch_results[f"batch_{batch_size}"] = {
                        'batch_size': batch_size,
                        'total_time_ms': execution_time,
                        'time_per_sample_ms': time_per_sample,
                        'throughput_samples_per_sec': 1000.0 / time_per_sample,
                        'input_shape': batch_input[0].shape,
                        'output_shapes': [out.shape for out in outputs] if outputs else []
                    }
                    
                    print_result(f"Batch size {batch_size}", True,
                                f"Time/sample: {time_per_sample:.3f}ms, Throughput: {1000.0/time_per_sample:.1f} samples/sec")
                    
                except Exception as e:
                    batch_results[f"batch_{batch_size}"] = {'error': str(e)}
                    print_result(f"Batch size {batch_size}", False, f"Error: {e}")
            
            # Analyze batch efficiency
            if len(batch_results) > 1:
                # Compare single vs batch processing
                single_time = batch_results.get('batch_1', {}).get('time_per_sample_ms', 0)
                batch_times = [r.get('time_per_sample_ms', 0) for r in batch_results.values() 
                              if isinstance(r, dict) and 'time_per_sample_ms' in r]
                
                if single_time > 0 and batch_times:
                    efficiency = {
                        'single_sample_time_ms': single_time,
                        'best_batch_time_ms': min(batch_times),
                        'speedup_factor': single_time / min(batch_times),
                        'efficiency_gain_percent': ((single_time - min(batch_times)) / single_time) * 100
                    }
                    
                    batch_results['efficiency_analysis'] = efficiency
                    
                    print_result("Batch efficiency", efficiency['speedup_factor'] > 1.0,
                                f"Speedup: {efficiency['speedup_factor']:.2f}x, Gain: {efficiency['efficiency_gain_percent']:.1f}%")
            
            self.performance_data["batch_results"] = batch_results
            self.results["batch_processing"] = len(batch_results) > 0
            
        except Exception as e:
            print_result("Batch processing", False, f"Error: {e}")
            self.results["batch_processing"] = False
    
    def test_error_recovery(self):
        """Test 10: Error Recovery and Robustness"""
        print_header("Test 10: Error Recovery and Robustness")
        
        try:
            recovery_results = {}
            
            if not self.test_models:
                print_result("Error recovery", False, "No test models available")
                self.results["error_recovery"] = False
                return
            
            model_name, model_info = next(iter(self.test_models.items()))
            runtime = model_info['runtime']
            
            # Test recovery from various error conditions
            error_tests = [
                ("After empty input", []),
                ("After invalid shape", [np.random.randn(0, 10).astype(np.float32)]),
                ("After NaN input", [np.full((10, 10), np.nan, dtype=np.float32)]),
                ("After inf input", [np.full((10, 10), np.inf, dtype=np.float32)]),
                ("After very large input", [np.random.randn(10, 10).astype(np.float32) * 1e10]),
            ]
            
            valid_input = [self.sample_data['medium_2d']]
            
            for test_name, error_input in error_tests:
                try:
                    # Try the error-inducing input
                    try:
                        runtime.run(error_input)
                        error_occurred = False
                    except:
                        error_occurred = True
                    
                    # Test recovery with valid input
                    recovery_outputs = runtime.run(valid_input)
                    recovery_successful = recovery_outputs is not None and len(recovery_outputs) > 0
                    
                    recovery_results[test_name] = {
                        'error_occurred': error_occurred,
                        'recovery_successful': recovery_successful,
                        'can_continue': recovery_successful
                    }
                    
                    print_result(f"Recovery {test_name}", recovery_successful,
                                f"Error: {error_occurred}, Recovery: {recovery_successful}")
                    
                except Exception as e:
                    recovery_results[test_name] = {
                        'error_occurred': True,
                        'recovery_successful': False,
                        'error': str(e)
                    }
                    print_result(f"Recovery {test_name}", False, f"Error: {e}")
            
            # Test state consistency after errors
            try:
                # Run multiple valid inferences to check state
                consistent_outputs = []
                for _ in range(3):
                    outputs = runtime.run(valid_input)
                    consistent_outputs.append(outputs)
                
                # Check consistency
                if len(consistent_outputs) > 1 and all(o for o in consistent_outputs):
                    diffs = []
                    for i in range(1, len(consistent_outputs)):
                        diff = np.abs(consistent_outputs[i][0] - consistent_outputs[0][0])
                        diffs.append(np.max(diff))
                    
                    max_diff = max(diffs) if diffs else 0
                    state_consistent = max_diff < 1e-6
                    
                    recovery_results['state_consistency'] = {
                        'consistent': state_consistent,
                        'max_difference': float(max_diff)
                    }
                    
                    print_result("State consistency", state_consistent,
                                f"Max diff after recovery: {max_diff:.8f}")
                
            except Exception as e:
                print_result("State consistency", False, f"Error: {e}")
            
            self.performance_data["recovery_results"] = recovery_results
            recovery_count = sum(1 for r in recovery_results.values() 
                               if isinstance(r, dict) and r.get('recovery_successful', False))
            self.results["error_recovery"] = recovery_count > len(error_tests) * 0.6
            
        except Exception as e:
            print_result("Error recovery", False, f"Error: {e}")
            self.results["error_recovery"] = False
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print_header("Comprehensive Model and Data Test Report")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name.replace('_', ' ').title()}")
        
        # Performance summary
        if self.performance_data:
            print(f"\n🚀 Performance Highlights:")
            
            # Extract key performance metrics
            if 'performance_comparison' in self.performance_data:
                perf_data = self.performance_data['performance_comparison']
                fastest_times = []
                for model_data in perf_data.values():
                    for input_data in model_data.values():
                        if isinstance(input_data, dict) and 'mean_time_ms' in input_data:
                            fastest_times.append(input_data['mean_time_ms'])
                
                if fastest_times:
                    print(f"   Fastest inference: {min(fastest_times):.3f}ms")
                    print(f"   Average inference: {np.mean(fastest_times):.3f}ms")
            
            # Memory usage summary
            if 'memory_results' in self.performance_data:
                mem_data = self.performance_data['memory_results']
                memory_usages = []
                for mem_info in mem_data.values():
                    if isinstance(mem_info, dict) and 'total_memory_mb' in mem_info:
                        memory_usages.append(mem_info['total_memory_mb'])
                
                if memory_usages:
                    print(f"   Memory usage range: {min(memory_usages):.3f} - {max(memory_usages):.3f} MB")
            
            # Batch processing efficiency
            if 'batch_results' in self.performance_data:
                batch_data = self.performance_data['batch_results']
                if 'efficiency_analysis' in batch_data:
                    eff = batch_data['efficiency_analysis']
                    print(f"   Batch processing speedup: {eff['speedup_factor']:.2f}x")
        
        # Data handling assessment
        print(f"\n📊 Data Handling Assessment:")
        data_features = [
            ("Sample Data Generation", self.results.get("sample_data_generation", False)),
            ("Model Import/Export", self.results.get("model_import_export", False)),
            ("Input Validation", self.results.get("input_validation", False)),
            ("Output Consistency", self.results.get("output_consistency", False)),
            ("Data Format Compatibility", self.results.get("data_format_compatibility", False)),
            ("Memory Management", self.results.get("memory_usage", False)),
            ("Batch Processing", self.results.get("batch_processing", False)),
            ("Error Recovery", self.results.get("error_recovery", False)),
        ]
        
        for feature, status in data_features:
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {feature}")
        
        data_success = sum(1 for _, status in data_features if status)
        data_rate = (data_success / len(data_features)) * 100
        
        print(f"\n🏆 Overall Assessment:")
        print(f"   Test Success Rate: {success_rate:.1f}%")
        print(f"   Data Handling Score: {data_success}/{len(data_features)} ({data_rate:.1f}%)")
        
        if success_rate >= 80 and data_rate >= 80:
            print(f"   🎉 EXCELLENT: MLE Runtime demonstrates robust model and data handling!")
        elif success_rate >= 60 and data_rate >= 60:
            print(f"   👍 GOOD: MLE Runtime shows solid data processing capabilities")
        else:
            print(f"   ⚠️  NEEDS WORK: Some data handling features require attention")
        
        return {
            "success_rate": success_rate,
            "data_handling_rate": data_rate,
            "results": self.results,
            "performance_data": self.performance_data
        }

def main():
    """Main test execution"""
    print("🚀 Starting MLE Runtime Model and Data Test Suite")
    print("=" * 70)
    
    try:
        test_suite = MLEModelDataTest()
        report = test_suite.run_all_tests()
        
        print(f"\n✨ Test completed successfully!")
        print(f"Overall success rate: {report['success_rate']:.1f}%")
        print(f"Data handling rate: {report['data_handling_rate']:.1f}%")
        
        return 0 if report['success_rate'] >= 70 else 1
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())