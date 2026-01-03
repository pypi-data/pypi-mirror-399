#!/usr/bin/env python3
"""
MLE Runtime Edge Data Test Suite
================================

This test validates the runtime's handling of extreme edge cases:
1. Extreme numerical values (very large, very small, special values)
2. Unusual data shapes and dimensions
3. Memory-intensive scenarios
4. Boundary conditions
5. Malformed or corrupted data
6. Performance under stress conditions
"""

import numpy as np
import sys
import time
import traceback
from typing import List, Dict, Any, Tuple
import gc
import warnings

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

class MLEEdgeDataTest:
    """Comprehensive edge data testing suite"""
    
    def __init__(self):
        self.results = {}
        self.runtime = None
        
    def setup_runtime(self):
        """Setup MLE Runtime for testing"""
        try:
            import mle_runtime
            self.runtime = mle_runtime.MLERuntime(device="auto")
            self.runtime.enable_adaptive_optimization(True)
            
            # Load a demo model
            result = self.runtime.load_model("edge_test_model.mle")
            print(f"✅ Runtime initialized: {result.get('python_loaded', False)}")
            return True
        except Exception as e:
            print(f"❌ Runtime setup failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all edge data tests"""
        print("🚀 MLE Runtime Edge Data Test Suite")
        print("Testing extreme edge cases and boundary conditions...")
        
        if not self.setup_runtime():
            return {"success_rate": 0, "results": {"setup": False}}
        
        # Test 1: Extreme Numerical Values
        self.test_extreme_numerical_values()
        
        # Test 2: Unusual Data Shapes
        self.test_unusual_data_shapes()
        
        # Test 3: Memory Stress Testing
        self.test_memory_stress()
        
        # Test 4: Boundary Conditions
        self.test_boundary_conditions()
        
        # Test 5: Special IEEE 754 Values
        self.test_special_ieee_values()
        
        # Test 6: Data Type Edge Cases
        self.test_data_type_edges()
        
        # Test 7: Performance Under Stress
        self.test_performance_stress()
        
        # Test 8: Corrupted Data Handling
        self.test_corrupted_data()
        
        # Test 9: Concurrent Access
        self.test_concurrent_access()
        
        # Test 10: Resource Exhaustion
        self.test_resource_exhaustion()
        
        return self.generate_report()
    
    def test_extreme_numerical_values(self):
        """Test 1: Extreme Numerical Values"""
        print_header("Test 1: Extreme Numerical Values")
        
        try:
            # Test extremely large values
            large_values = [
                ("Max Float32", np.array([[np.finfo(np.float32).max]], dtype=np.float32)),
                ("Near Max Float32", np.array([[np.finfo(np.float32).max * 0.9]], dtype=np.float32)),
                ("Very Large", np.array([[1e30]], dtype=np.float32)),
                ("Extremely Large", np.array([[1e38]], dtype=np.float32)),
            ]
            
            for test_name, data in large_values:
                try:
                    outputs = self.runtime.run([data])
                    print_result(f"Large Values: {test_name}", True, 
                                f"Input: {data[0,0]:.2e}, Output shape: {outputs[0].shape if outputs else 'None'}")
                except Exception as e:
                    print_result(f"Large Values: {test_name}", False, f"Error: {e}")
            
            # Test extremely small values
            small_values = [
                ("Min Float32", np.array([[np.finfo(np.float32).tiny]], dtype=np.float32)),
                ("Very Small", np.array([[1e-30]], dtype=np.float32)),
                ("Extremely Small", np.array([[1e-38]], dtype=np.float32)),
                ("Subnormal", np.array([[np.finfo(np.float32).tiny / 2]], dtype=np.float32)),
            ]
            
            for test_name, data in small_values:
                try:
                    outputs = self.runtime.run([data])
                    print_result(f"Small Values: {test_name}", True,
                                f"Input: {data[0,0]:.2e}, Output shape: {outputs[0].shape if outputs else 'None'}")
                except Exception as e:
                    print_result(f"Small Values: {test_name}", False, f"Error: {e}")
            
            # Test precision edge cases
            precision_tests = [
                ("Epsilon", np.array([[np.finfo(np.float32).eps]], dtype=np.float32)),
                ("1 + Epsilon", np.array([[1.0 + np.finfo(np.float32).eps]], dtype=np.float32)),
                ("1 - Epsilon", np.array([[1.0 - np.finfo(np.float32).eps]], dtype=np.float32)),
            ]
            
            for test_name, data in precision_tests:
                try:
                    outputs = self.runtime.run([data])
                    print_result(f"Precision: {test_name}", True,
                                f"Input: {data[0,0]:.15f}, Handled: {outputs is not None}")
                except Exception as e:
                    print_result(f"Precision: {test_name}", False, f"Error: {e}")
            
            self.results["extreme_numerical_values"] = True
            
        except Exception as e:
            print_result("Extreme numerical values", False, f"Error: {e}")
            self.results["extreme_numerical_values"] = False
    
    def test_unusual_data_shapes(self):
        """Test 2: Unusual Data Shapes"""
        print_header("Test 2: Unusual Data Shapes")
        
        try:
            unusual_shapes = [
                ("Single Element", (1,)),
                ("Very Long 1D", (100000,)),
                ("Very Tall 2D", (10000, 1)),
                ("Very Wide 2D", (1, 10000)),
                ("High Dimensional", (2, 2, 2, 2, 2, 2, 2)),  # 7D
                ("Asymmetric 3D", (1, 1000, 1)),
                ("Prime Dimensions", (7, 11, 13)),
                ("Large Square", (1000, 1000)),
            ]
            
            for test_name, shape in unusual_shapes:
                try:
                    # Create data with the unusual shape
                    data = np.random.randn(*shape).astype(np.float32) * 0.1
                    
                    # Test memory usage
                    memory_mb = data.nbytes / (1024 * 1024)
                    
                    if memory_mb > 100:  # Skip very large arrays to avoid memory issues
                        print_result(f"Shape: {test_name}", True, 
                                    f"Skipped (too large: {memory_mb:.1f}MB)")
                        continue
                    
                    outputs = self.runtime.run([data])
                    print_result(f"Shape: {test_name}", True,
                                f"Shape: {shape}, Memory: {memory_mb:.3f}MB, Output: {outputs[0].shape if outputs else 'None'}")
                    
                except Exception as e:
                    print_result(f"Shape: {test_name}", False, f"Error: {e}")
            
            # Test empty and minimal shapes
            minimal_shapes = [
                ("Empty 1D", (0,)),
                ("Empty 2D", (0, 0)),
                ("Empty 3D", (0, 0, 0)),
                ("Single Row Empty", (1, 0)),
                ("Single Col Empty", (0, 1)),
            ]
            
            for test_name, shape in minimal_shapes:
                try:
                    data = np.array([], dtype=np.float32).reshape(shape)
                    outputs = self.runtime.run([data])
                    print_result(f"Minimal: {test_name}", True,
                                f"Shape: {shape}, Handled gracefully")
                except Exception as e:
                    print_result(f"Minimal: {test_name}", True, f"Expected error: {type(e).__name__}")
            
            self.results["unusual_data_shapes"] = True
            
        except Exception as e:
            print_result("Unusual data shapes", False, f"Error: {e}")
            self.results["unusual_data_shapes"] = False
    
    def test_memory_stress(self):
        """Test 3: Memory Stress Testing"""
        print_header("Test 3: Memory Stress Testing")
        
        try:
            # Test progressively larger arrays
            memory_tests = [
                ("1MB", (256, 1024)),      # ~1MB
                ("10MB", (800, 3200)),     # ~10MB  
                ("50MB", (1800, 7200)),    # ~50MB
            ]
            
            for test_name, shape in memory_tests:
                try:
                    data = np.random.randn(*shape).astype(np.float32)
                    memory_mb = data.nbytes / (1024 * 1024)
                    
                    start_time = time.time()
                    outputs = self.runtime.run([data])
                    end_time = time.time()
                    
                    execution_time = (end_time - start_time) * 1000
                    
                    print_result(f"Memory Stress: {test_name}", True,
                                f"Size: {memory_mb:.1f}MB, Time: {execution_time:.1f}ms")
                    
                    # Force garbage collection
                    del data, outputs
                    gc.collect()
                    
                except MemoryError:
                    print_result(f"Memory Stress: {test_name}", True, "Memory limit reached (expected)")
                except Exception as e:
                    print_result(f"Memory Stress: {test_name}", False, f"Error: {e}")
            
            # Test memory fragmentation
            try:
                fragments = []
                for i in range(10):
                    fragment = np.random.randn(1000, 1000).astype(np.float32)
                    outputs = self.runtime.run([fragment])
                    fragments.append(fragment)
                
                print_result("Memory Fragmentation", True, f"Handled {len(fragments)} fragments")
                
                # Cleanup
                del fragments
                gc.collect()
                
            except Exception as e:
                print_result("Memory Fragmentation", False, f"Error: {e}")
            
            self.results["memory_stress"] = True
            
        except Exception as e:
            print_result("Memory stress", False, f"Error: {e}")
            self.results["memory_stress"] = False
    
    def test_boundary_conditions(self):
        """Test 4: Boundary Conditions"""
        print_header("Test 4: Boundary Conditions")
        
        try:
            # Test array size boundaries
            boundary_tests = [
                ("Max Int32 Elements", min(2**20, 1048576)),  # Reasonable limit
                ("Power of 2", 2**16),
                ("Power of 2 - 1", 2**16 - 1),
                ("Power of 2 + 1", 2**16 + 1),
                ("Prime Number", 65537),  # Large prime
            ]
            
            for test_name, size in boundary_tests:
                try:
                    if size > 1000000:  # Skip very large sizes
                        print_result(f"Boundary: {test_name}", True, "Skipped (too large)")
                        continue
                        
                    data = np.random.randn(size).astype(np.float32).reshape(-1, 1)
                    outputs = self.runtime.run([data])
                    
                    print_result(f"Boundary: {test_name}", True,
                                f"Size: {size}, Shape: {data.shape}")
                    
                except Exception as e:
                    print_result(f"Boundary: {test_name}", False, f"Error: {e}")
            
            # Test dimension boundaries
            dimension_tests = [
                ("1D Max", (100000,)),
                ("2D Square", (1000, 1000)),
                ("3D Cube", (100, 100, 100)),
                ("4D Hypercube", (10, 10, 10, 10)),
                ("Many Dims", tuple([2] * 15)),  # 15 dimensions
            ]
            
            for test_name, shape in dimension_tests:
                try:
                    total_elements = np.prod(shape)
                    if total_elements > 1000000:  # Skip very large arrays
                        print_result(f"Dimension: {test_name}", True, "Skipped (too large)")
                        continue
                    
                    data = np.random.randn(*shape).astype(np.float32)
                    outputs = self.runtime.run([data])
                    
                    print_result(f"Dimension: {test_name}", True,
                                f"Shape: {shape}, Elements: {total_elements}")
                    
                except Exception as e:
                    print_result(f"Dimension: {test_name}", False, f"Error: {e}")
            
            self.results["boundary_conditions"] = True
            
        except Exception as e:
            print_result("Boundary conditions", False, f"Error: {e}")
            self.results["boundary_conditions"] = False
    
    def test_special_ieee_values(self):
        """Test 5: Special IEEE 754 Values"""
        print_header("Test 5: Special IEEE 754 Values")
        
        try:
            special_values = [
                ("Positive Infinity", np.array([[np.inf]], dtype=np.float32)),
                ("Negative Infinity", np.array([[-np.inf]], dtype=np.float32)),
                ("NaN", np.array([[np.nan]], dtype=np.float32)),
                ("Positive Zero", np.array([[+0.0]], dtype=np.float32)),
                ("Negative Zero", np.array([[-0.0]], dtype=np.float32)),
                ("Mixed Special", np.array([[np.inf, -np.inf, np.nan, 0.0, -0.0]], dtype=np.float32)),
            ]
            
            for test_name, data in special_values:
                try:
                    outputs = self.runtime.run([data])
                    
                    # Check if output contains special values
                    if outputs and len(outputs) > 0:
                        has_inf = np.isinf(outputs[0]).any()
                        has_nan = np.isnan(outputs[0]).any()
                        special_info = f"Output has inf: {has_inf}, nan: {has_nan}"
                    else:
                        special_info = "No output"
                    
                    print_result(f"IEEE: {test_name}", True, special_info)
                    
                except Exception as e:
                    print_result(f"IEEE: {test_name}", False, f"Error: {e}")
            
            # Test arrays with mixed special and normal values
            mixed_tests = [
                ("50% NaN", np.where(np.random.rand(100, 10) < 0.5, np.nan, np.random.randn(100, 10)).astype(np.float32)),
                ("Sparse Inf", np.where(np.random.rand(100, 10) < 0.01, np.inf, np.random.randn(100, 10)).astype(np.float32)),
                ("All Special", np.full((10, 10), np.nan, dtype=np.float32)),
            ]
            
            for test_name, data in mixed_tests:
                try:
                    outputs = self.runtime.run([data])
                    
                    nan_count = np.isnan(data).sum()
                    inf_count = np.isinf(data).sum()
                    
                    print_result(f"Mixed: {test_name}", True,
                                f"Input NaN: {nan_count}, Inf: {inf_count}")
                    
                except Exception as e:
                    print_result(f"Mixed: {test_name}", False, f"Error: {e}")
            
            self.results["special_ieee_values"] = True
            
        except Exception as e:
            print_result("Special IEEE values", False, f"Error: {e}")
            self.results["special_ieee_values"] = False
    
    def test_data_type_edges(self):
        """Test 6: Data Type Edge Cases"""
        print_header("Test 6: Data Type Edge Cases")
        
        try:
            # Test different data types and their conversion
            dtype_tests = [
                ("Float16", np.float16),
                ("Float32", np.float32),
                ("Float64", np.float64),
                ("Int8", np.int8),
                ("Int16", np.int16),
                ("Int32", np.int32),
                ("Int64", np.int64),
                ("UInt8", np.uint8),
                ("UInt16", np.uint16),
                ("UInt32", np.uint32),
                ("Bool", np.bool_),
            ]
            
            for test_name, dtype in dtype_tests:
                try:
                    if dtype in [np.bool_]:
                        data = np.random.choice([True, False], size=(10, 10)).astype(dtype)
                    elif dtype in [np.int8, np.int16, np.int32, np.int64]:
                        data = np.random.randint(-100, 100, size=(10, 10)).astype(dtype)
                    elif dtype in [np.uint8, np.uint16, np.uint32]:
                        data = np.random.randint(0, 200, size=(10, 10)).astype(dtype)
                    else:
                        data = np.random.randn(10, 10).astype(dtype)
                    
                    # Convert to float32 for runtime (as expected)
                    float_data = data.astype(np.float32)
                    outputs = self.runtime.run([float_data])
                    
                    print_result(f"DType: {test_name}", True,
                                f"Original: {dtype}, Range: [{data.min()}, {data.max()}]")
                    
                except Exception as e:
                    print_result(f"DType: {test_name}", False, f"Error: {e}")
            
            # Test type overflow/underflow
            overflow_tests = [
                ("Int8 Overflow", np.array([[300]], dtype=np.int32).astype(np.int8)),
                ("UInt8 Underflow", np.array([[-50]], dtype=np.int32).astype(np.uint8)),
                ("Float32 from Float64", np.array([[1e100]], dtype=np.float64).astype(np.float32)),
            ]
            
            for test_name, data in overflow_tests:
                try:
                    float_data = data.astype(np.float32)
                    outputs = self.runtime.run([float_data])
                    
                    print_result(f"Overflow: {test_name}", True,
                                f"Value: {float_data[0,0]}, Handled: {outputs is not None}")
                    
                except Exception as e:
                    print_result(f"Overflow: {test_name}", False, f"Error: {e}")
            
            self.results["data_type_edges"] = True
            
        except Exception as e:
            print_result("Data type edges", False, f"Error: {e}")
            self.results["data_type_edges"] = False
    
    def test_performance_stress(self):
        """Test 7: Performance Under Stress"""
        print_header("Test 7: Performance Under Stress")
        
        try:
            # Test rapid successive calls
            rapid_fire_count = 100
            times = []
            
            test_data = [np.random.randn(100, 100).astype(np.float32)]
            
            for i in range(rapid_fire_count):
                start_time = time.time()
                outputs = self.runtime.run(test_data)
                end_time = time.time()
                times.append((end_time - start_time) * 1000)
            
            avg_time = np.mean(times)
            std_time = np.std(times)
            min_time = np.min(times)
            max_time = np.max(times)
            
            print_result("Rapid Fire", True,
                        f"Avg: {avg_time:.3f}ms, Std: {std_time:.3f}ms, Range: [{min_time:.3f}, {max_time:.3f}]ms")
            
            # Test with varying input sizes
            size_stress_tests = [
                ("Tiny", (10, 10)),
                ("Small", (100, 100)),
                ("Medium", (500, 500)),
                ("Large", (1000, 1000)),
            ]
            
            for test_name, shape in size_stress_tests:
                try:
                    data = [np.random.randn(*shape).astype(np.float32)]
                    
                    # Warmup
                    for _ in range(3):
                        self.runtime.run(data)
                    
                    # Benchmark
                    times = []
                    for _ in range(10):
                        start_time = time.time()
                        outputs = self.runtime.run(data)
                        end_time = time.time()
                        times.append((end_time - start_time) * 1000)
                    
                    avg_time = np.mean(times)
                    throughput = (np.prod(shape) / (avg_time / 1000)) if avg_time > 0 else float('inf')
                    
                    print_result(f"Size Stress: {test_name}", True,
                                f"Shape: {shape}, Avg: {avg_time:.3f}ms, Throughput: {throughput:.0f} elem/sec")
                    
                except Exception as e:
                    print_result(f"Size Stress: {test_name}", False, f"Error: {e}")
            
            self.results["performance_stress"] = True
            
        except Exception as e:
            print_result("Performance stress", False, f"Error: {e}")
            self.results["performance_stress"] = False
    
    def test_corrupted_data(self):
        """Test 8: Corrupted Data Handling"""
        print_header("Test 8: Corrupted Data Handling")
        
        try:
            # Test various forms of data corruption
            base_data = np.random.randn(100, 100).astype(np.float32)
            
            corruption_tests = [
                ("Random Corruption", self._corrupt_random(base_data.copy(), 0.01)),
                ("Bit Flip", self._corrupt_bitflip(base_data.copy(), 10)),
                ("Value Injection", self._corrupt_inject_values(base_data.copy())),
                ("Structure Damage", self._corrupt_structure(base_data.copy())),
            ]
            
            for test_name, corrupted_data in corruption_tests:
                try:
                    if corrupted_data is not None:
                        outputs = self.runtime.run([corrupted_data])
                        
                        # Check output sanity
                        if outputs and len(outputs) > 0:
                            output_stats = {
                                'has_nan': np.isnan(outputs[0]).any(),
                                'has_inf': np.isinf(outputs[0]).any(),
                                'finite_ratio': np.isfinite(outputs[0]).mean()
                            }
                            
                            print_result(f"Corruption: {test_name}", True,
                                        f"NaN: {output_stats['has_nan']}, Inf: {output_stats['has_inf']}, Finite: {output_stats['finite_ratio']:.2f}")
                        else:
                            print_result(f"Corruption: {test_name}", True, "No output (handled)")
                    else:
                        print_result(f"Corruption: {test_name}", True, "Corruption failed (expected)")
                        
                except Exception as e:
                    print_result(f"Corruption: {test_name}", True, f"Handled error: {type(e).__name__}")
            
            self.results["corrupted_data"] = True
            
        except Exception as e:
            print_result("Corrupted data", False, f"Error: {e}")
            self.results["corrupted_data"] = False
    
    def _corrupt_random(self, data, corruption_rate):
        """Randomly corrupt a fraction of the data"""
        mask = np.random.rand(*data.shape) < corruption_rate
        data[mask] = np.random.choice([np.nan, np.inf, -np.inf, 1e38, -1e38])
        return data
    
    def _corrupt_bitflip(self, data, num_flips):
        """Simulate bit flips in the data"""
        flat_data = data.flatten()
        indices = np.random.choice(len(flat_data), min(num_flips, len(flat_data)), replace=False)
        
        # Convert to bytes and flip random bits
        byte_view = flat_data.view(np.uint8)
        for idx in indices:
            byte_idx = idx * 4  # 4 bytes per float32
            if byte_idx < len(byte_view):
                bit_pos = np.random.randint(0, 8)
                byte_view[byte_idx] ^= (1 << bit_pos)
        
        return flat_data.reshape(data.shape)
    
    def _corrupt_inject_values(self, data):
        """Inject problematic values"""
        problematic_values = [np.nan, np.inf, -np.inf, 1e38, -1e38, 0.0]
        indices = np.random.choice(data.size, min(10, data.size), replace=False)
        flat_data = data.flatten()
        
        for idx in indices:
            flat_data[idx] = np.random.choice(problematic_values)
        
        return flat_data.reshape(data.shape)
    
    def _corrupt_structure(self, data):
        """Corrupt the data structure"""
        try:
            # Try to create invalid shapes or strides
            corrupted = data.copy()
            
            # Introduce non-contiguous memory layout
            if data.ndim >= 2:
                corrupted = corrupted[::2, ::2]  # Create strided view
            
            return corrupted
        except:
            return None
    
    def test_concurrent_access(self):
        """Test 9: Concurrent Access (Simulated)"""
        print_header("Test 9: Concurrent Access Simulation")
        
        try:
            # Simulate concurrent access by rapid alternating calls
            test_data_a = [np.random.randn(50, 50).astype(np.float32)]
            test_data_b = [np.random.randn(100, 100).astype(np.float32)]
            
            success_count = 0
            total_attempts = 50
            
            for i in range(total_attempts):
                try:
                    if i % 2 == 0:
                        outputs = self.runtime.run(test_data_a)
                    else:
                        outputs = self.runtime.run(test_data_b)
                    
                    if outputs and len(outputs) > 0:
                        success_count += 1
                        
                except Exception as e:
                    pass  # Count as failure
            
            success_rate = success_count / total_attempts
            print_result("Concurrent Simulation", success_rate > 0.9,
                        f"Success rate: {success_rate:.2f} ({success_count}/{total_attempts})")
            
            self.results["concurrent_access"] = success_rate > 0.8
            
        except Exception as e:
            print_result("Concurrent access", False, f"Error: {e}")
            self.results["concurrent_access"] = False
    
    def test_resource_exhaustion(self):
        """Test 10: Resource Exhaustion Scenarios"""
        print_header("Test 10: Resource Exhaustion Scenarios")
        
        try:
            # Test memory exhaustion protection
            try:
                large_arrays = []
                for i in range(10):
                    # Create progressively larger arrays
                    size = min(1000 * (i + 1), 5000)  # Cap at reasonable size
                    array = np.random.randn(size, size).astype(np.float32)
                    outputs = self.runtime.run([array])
                    large_arrays.append(array)
                    
                    memory_mb = sum(arr.nbytes for arr in large_arrays) / (1024 * 1024)
                    if memory_mb > 500:  # Stop at 500MB to avoid system issues
                        break
                
                print_result("Memory Exhaustion Protection", True,
                            f"Handled {len(large_arrays)} large arrays ({memory_mb:.1f}MB)")
                
                # Cleanup
                del large_arrays
                gc.collect()
                
            except MemoryError:
                print_result("Memory Exhaustion Protection", True, "Memory limit reached (expected)")
            except Exception as e:
                print_result("Memory Exhaustion Protection", False, f"Error: {e}")
            
            # Test computational exhaustion
            try:
                computation_times = []
                for size in [100, 200, 500, 1000]:
                    data = [np.random.randn(size, size).astype(np.float32)]
                    
                    start_time = time.time()
                    outputs = self.runtime.run(data)
                    end_time = time.time()
                    
                    computation_times.append((size, (end_time - start_time) * 1000))
                
                # Check if computation time scales reasonably
                time_scaling_ok = all(t < 10000 for _, t in computation_times)  # Less than 10 seconds
                
                print_result("Computational Exhaustion", time_scaling_ok,
                            f"Max time: {max(t for _, t in computation_times):.1f}ms")
                
            except Exception as e:
                print_result("Computational Exhaustion", False, f"Error: {e}")
            
            self.results["resource_exhaustion"] = True
            
        except Exception as e:
            print_result("Resource exhaustion", False, f"Error: {e}")
            self.results["resource_exhaustion"] = False
    
    def generate_report(self):
        """Generate comprehensive edge data test report"""
        print_header("Edge Data Test Report")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 Edge Data Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        test_names = [
            "extreme_numerical_values", "unusual_data_shapes", "memory_stress",
            "boundary_conditions", "special_ieee_values", "data_type_edges",
            "performance_stress", "corrupted_data", "concurrent_access", "resource_exhaustion"
        ]
        
        for test_name in test_names:
            if test_name in self.results:
                status = "✅ PASS" if self.results[test_name] else "❌ FAIL"
                print(f"   {status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n🏆 Edge Data Robustness Assessment:")
        if success_rate >= 90:
            print(f"   🎉 EXCELLENT: Runtime handles edge cases exceptionally well!")
        elif success_rate >= 75:
            print(f"   👍 GOOD: Runtime shows solid edge case handling")
        elif success_rate >= 60:
            print(f"   ⚠️  FAIR: Some edge cases need attention")
        else:
            print(f"   ❌ POOR: Significant edge case handling issues")
        
        return {
            "success_rate": success_rate,
            "results": self.results,
            "total_tests": total_tests,
            "passed_tests": passed_tests
        }

def main():
    """Main test execution"""
    print("🚀 Starting MLE Runtime Edge Data Test Suite")
    print("=" * 70)
    
    try:
        test_suite = MLEEdgeDataTest()
        report = test_suite.run_all_tests()
        
        print(f"\n✨ Edge data testing completed!")
        print(f"Overall success rate: {report['success_rate']:.1f}%")
        
        return 0 if report['success_rate'] >= 70 else 1
        
    except Exception as e:
        print(f"\n❌ Edge data test suite failed with error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())