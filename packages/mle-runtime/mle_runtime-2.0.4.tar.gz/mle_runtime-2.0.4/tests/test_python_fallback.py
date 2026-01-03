#!/usr/bin/env python3
"""
Test Python Fallback Engine
"""

import numpy as np
import mle_runtime

def test_python_fallback():
    """Test Python fallback engine directly"""
    print("🔧 Testing Python fallback engine...")
    
    # Create simple model with known weights
    model_data = {
        'model_type': 'linear',
        'weights': [[2.0, 3.0]],  # output = 2*x1 + 3*x2 + bias
        'bias': [1.0]
    }
    
    print(f"Model data: {model_data}")
    
    # Export
    result = mle_runtime.export_model(model_data, 'python_test.mle', input_shape=(2,))
    print(f"Export result: {result}")
    
    # Create runtime and force Python fallback by disabling C++
    runtime = mle_runtime.MLERuntime(device='cpu')
    
    # Manually disable C++ engine to force Python fallback
    runtime.cpp_engine = None
    
    runtime.load_model('python_test.mle')
    
    # Test with known input
    test_input = np.array([[1.0, 1.0]], dtype=np.float32)
    expected = 2.0 * 1.0 + 3.0 * 1.0 + 1.0  # = 6.0
    
    print(f"\nTest input: {test_input[0]}")
    print(f"Expected output: {expected}")
    
    # Run inference
    output = runtime.run([test_input])
    actual = output[0][0][0] if output and len(output[0]) > 0 and len(output[0][0]) > 0 else 0.0
    
    print(f"Actual output: {actual}")
    print(f"Error: {abs(expected - float(actual))}")
    
    success = abs(expected - float(actual)) < 0.1
    print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    return success

if __name__ == "__main__":
    test_python_fallback()