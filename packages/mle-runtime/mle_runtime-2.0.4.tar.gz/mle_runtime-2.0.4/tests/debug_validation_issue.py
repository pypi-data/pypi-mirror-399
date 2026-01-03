#!/usr/bin/env python3
"""
Debug Validation Test Issues
"""

import numpy as np
import mle_runtime
import tempfile
import os

def test_correctness_issue():
    """Test the specific correctness issue"""
    print("🔍 Testing Correctness Issue")
    
    try:
        # Recreate the exact test from validation
        W = np.array([[1.0, 0.0, 0.0],
                     [0.0, 1.0, 0.0],
                     [0.0, 0.0, 1.0]], dtype=np.float32)  # Identity matrix
        b = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        
        model_data = {
            'weights': W,
            'bias': b,
            'type': 'linear'
        }
        
        export_path = "correctness_debug.mle"
        result = mle_runtime.export_model(model_data, export_path, input_shape=(3,))
        print(f"Export result: {result['status']}")
        
        # Test input
        test_input = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
        expected_output = np.dot(test_input, W.T) + b  # [1.1, 2.2, 3.3]
        
        print(f"Test input: {test_input}")
        print(f"Expected output: {expected_output}")
        
        # Test with auto backend (should use C++)
        runtime = mle_runtime.MLERuntime(device='auto')
        runtime.load_model(export_path)
        
        outputs = runtime.run([test_input])
        print(f"Actual output: {outputs[0] if outputs else None}")
        
        if outputs and len(outputs) > 0:
            actual_output = outputs[0]
            abs_error = np.abs(actual_output - expected_output)
            max_abs_error = np.max(abs_error)
            print(f"Max absolute error: {max_abs_error}")
            print(f"Is correct (< 1e-5): {max_abs_error < 1e-5}")
        
        # Clean up
        if os.path.exists(export_path):
            os.remove(export_path)
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_array_indexing():
    """Test array indexing issues"""
    print("\n🔍 Testing Array Indexing")
    
    try:
        runtime = mle_runtime.MLERuntime(device='auto')
        
        # Create simple model
        model_data = {
            'weights': np.random.randn(5, 3).astype(np.float32),
            'bias': np.zeros(3, dtype=np.float32),
            'type': 'linear'
        }
        
        export_path = "indexing_debug.mle"
        result = mle_runtime.export_model(model_data, export_path, input_shape=(5,))
        runtime.load_model(export_path)
        
        # Test input
        test_input = [np.array([[1.0, 2.0, 3.0, 4.0, 5.0]], dtype=np.float32)]
        
        # Run multiple times to test determinism
        outputs_list = []
        for i in range(3):
            outputs = runtime.run(test_input)
            if outputs:
                print(f"Run {i+1}: output shape {outputs[0].shape}, type {type(outputs[0])}")
                outputs_list.append(outputs[0].copy())
            else:
                print(f"Run {i+1}: No output")
        
        # Test variance
        if len(outputs_list) > 1:
            output_array = np.array(outputs_list)
            print(f"Output array shape: {output_array.shape}")
            variance = np.var(output_array, axis=0)
            max_variance = np.max(variance)
            print(f"Max variance: {max_variance}")
        
        # Clean up
        if os.path.exists(export_path):
            os.remove(export_path)
    
    except Exception as e:
        print(f"❌ Array indexing test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_correctness_issue()
    test_array_indexing()