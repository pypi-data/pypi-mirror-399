#!/usr/bin/env python3
"""
Isolated test to find the exact slice error
"""

import numpy as np
import mle_runtime
import tempfile
import os
import traceback

def test_deterministic_isolated():
    """Test deterministic behavior in isolation"""
    print("Testing Deterministic Behavior (Isolated)")
    
    try:
        # Create test model
        model_data = {
            'weights': np.random.randn(5, 3).astype(np.float32),
            'bias': np.zeros(3, dtype=np.float32),
            'type': 'linear'
        }
        
        temp_dir = tempfile.mkdtemp()
        export_path = os.path.join(temp_dir, "deterministic_test.mle")
        result = mle_runtime.export_model(model_data, export_path, input_shape=(5,))
        
        # Load model
        runtime = mle_runtime.MLERuntime(device='auto')
        runtime.load_model(export_path)
        
        # Fixed test input
        test_input = [np.array([[1.0, 2.0, 3.0, 4.0, 5.0]], dtype=np.float32)]
        
        # Test 1: Multiple sequential runs
        sequential_outputs = []
        for i in range(10):
            outputs = runtime.run(test_input)
            if outputs and len(outputs) > 0:
                output = outputs[0]
                print(f"Run {i+1}: output type = {type(output)}, shape = {getattr(output, 'shape', 'no shape')}")
                
                if isinstance(output, np.ndarray):
                    sequential_outputs.append(output.copy())
                else:
                    # Convert to numpy array if it's not already
                    sequential_outputs.append(np.array(output, dtype=np.float32))
        
        print(f"Sequential outputs collected: {len(sequential_outputs)}")
        
        # Check sequential determinism
        if len(sequential_outputs) > 1:
            print("Converting to numpy array...")
            output_array = np.array(sequential_outputs)
            print(f"Output array shape: {output_array.shape}")
            
            print("Calculating variance...")
            sequential_variance = np.var(output_array, axis=0)
            print(f"Sequential variance: {sequential_variance}")
            
            max_sequential_variance = np.max(sequential_variance)
            print(f"Max sequential variance: {max_sequential_variance}")
            
            sequential_deterministic = max_sequential_variance < 1e-10
            print(f"Sequential deterministic: {sequential_deterministic}")
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        
        print("SUCCESS: Deterministic test completed without slice error")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_deterministic_isolated()