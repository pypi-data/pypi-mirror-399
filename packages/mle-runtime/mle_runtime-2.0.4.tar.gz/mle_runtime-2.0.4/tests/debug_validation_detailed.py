#!/usr/bin/env python3
"""
Debug validation test with detailed error tracking
"""

import numpy as np
import sys
import time
import os
import psutil
import threading
import tempfile
import traceback
from typing import List, Dict, Any, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json

def test_deterministic_behavior_debug():
    """Debug the deterministic behavior test specifically"""
    print("🔍 Testing Deterministic Behavior (Debug)")
    
    try:
        import mle_runtime
        
        # Create test model
        model_data = {
            'weights': np.random.randn(5, 3).astype(np.float32),
            'bias': np.zeros(3, dtype=np.float32),
            'type': 'linear'
        }
        
        temp_dir = tempfile.mkdtemp()
        export_path = os.path.join(temp_dir, "deterministic_test.mle")
        result = mle_runtime.export_model(model_data, export_path, input_shape=(5,))
        
        if result['status'] != 'success':
            print("❌ Model export failed")
            return
        
        # Load model
        runtime = mle_runtime.MLERuntime(device='auto')
        runtime.load_model(export_path)
        
        # Fixed test input
        test_input = [np.array([[1.0, 2.0, 3.0, 4.0, 5.0]], dtype=np.float32)]
        
        # Test 1: Multiple sequential runs
        sequential_outputs = []
        for i in range(10):
            try:
                outputs = runtime.run(test_input)
                if outputs:
                    print(f"Run {i+1}: output type {type(outputs[0])}, shape {outputs[0].shape}")
                    sequential_outputs.append(outputs[0].copy())
                else:
                    print(f"Run {i+1}: No outputs")
            except Exception as e:
                print(f"Run {i+1} failed: {e}")
                traceback.print_exc()
        
        # Check sequential determinism
        print(f"\nSequential outputs collected: {len(sequential_outputs)}")
        if len(sequential_outputs) > 1:
            try:
                print("Converting to numpy array...")
                output_array = np.array(sequential_outputs)
                print(f"Output array shape: {output_array.shape}")
                print(f"Output array dtype: {output_array.dtype}")
                
                print("Calculating variance...")
                sequential_variance = np.var(output_array, axis=0)
                print(f"Sequential variance shape: {sequential_variance.shape}")
                print(f"Sequential variance: {sequential_variance}")
                
                max_sequential_variance = np.max(sequential_variance)
                print(f"Max sequential variance: {max_sequential_variance}")
                
                sequential_deterministic = max_sequential_variance < 1e-10
                print(f"Sequential deterministic: {sequential_deterministic}")
                
            except Exception as e:
                print(f"❌ Sequential variance calculation failed: {e}")
                traceback.print_exc()
        
        # Test 2: Thread-safe determinism (simplified)
        def thread_inference():
            try:
                # Create new runtime instance for thread safety
                thread_runtime = mle_runtime.MLERuntime(device='auto')
                thread_runtime.load_model(export_path)
                outputs = thread_runtime.run(test_input)
                return outputs[0].copy() if outputs else None
            except Exception as e:
                print(f"Thread inference failed: {e}")
                return None
        
        thread_outputs = []
        print(f"\nTesting thread determinism...")
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(thread_inference) for _ in range(5)]
            for i, future in enumerate(futures):
                try:
                    result = future.result(timeout=10)
                    if result is not None:
                        print(f"Thread {i+1}: output shape {result.shape}")
                        thread_outputs.append(result)
                    else:
                        print(f"Thread {i+1}: No result")
                except Exception as e:
                    print(f"Thread {i+1} execution failed: {e}")
        
        # Check thread determinism
        print(f"\nThread outputs collected: {len(thread_outputs)}")
        if len(thread_outputs) > 1:
            try:
                thread_array = np.array(thread_outputs)
                print(f"Thread array shape: {thread_array.shape}")
                
                thread_variance = np.var(thread_array, axis=0)
                max_thread_variance = np.max(thread_variance)
                thread_deterministic = max_thread_variance < 1e-6
                
                print(f"Max thread variance: {max_thread_variance}")
                print(f"Thread deterministic: {thread_deterministic}")
                
            except Exception as e:
                print(f"❌ Thread variance calculation failed: {e}")
                traceback.print_exc()
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_deterministic_behavior_debug()