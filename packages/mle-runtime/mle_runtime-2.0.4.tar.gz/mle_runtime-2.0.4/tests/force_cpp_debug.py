#!/usr/bin/env python3
"""
Force C++ Engine Debug
"""

import numpy as np
import mle_runtime

def test_cpp_engine_directly():
    """Test C++ engine directly"""
    print("🔧 Testing C++ engine directly...")
    
    # Create simple model
    model_data = {
        'model_type': 'linear',
        'weights': [[2.0, 3.0]],
        'bias': [1.0]
    }
    
    # Export
    result = mle_runtime.export_model(model_data, 'force_cpp.mle', input_shape=(2,))
    print(f"Export result: {result}")
    
    # Force C++ engine by disabling Python fallback temporarily
    runtime = mle_runtime.MLERuntime(device='auto')
    
    # Disable fallback by setting failure count to 0
    runtime._core_manager.cpp_failure_count = 0
    runtime._core_manager.max_cpp_failures = 10  # Allow more attempts
    
    runtime.load_model('force_cpp.mle')
    
    # Test
    test_input = np.array([[1.0, 1.0]], dtype=np.float32)
    print(f"Input: {test_input}")
    
    # Run with C++ engine
    output = runtime.run([test_input])
    print(f"Output: {output}")
    
    return output

if __name__ == "__main__":
    test_cpp_engine_directly()