#!/usr/bin/env python3
"""
Final accuracy test with the original trained model scenario.
"""

import numpy as np
import mle_runtime

def test_original_scenario():
    """Test the original scenario that was failing."""
    print("🎯 Final Accuracy Test - Original Scenario")
    print("=" * 50)
    
    # Create the original test model with known weights and bias
    model_data = {
        'weights': np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32),
        'bias': np.array([0.1, 0.2, 0.3], dtype=np.float32),
        'type': 'linear'
    }
    
    print(f"Model weights:\n{model_data['weights']}")
    print(f"Model bias: {model_data['bias']}")
    
    # Export model
    result = mle_runtime.export_model(model_data, 'test_final_accuracy.mle', input_shape=(3,))
    print(f"Export result: {result['status']}")
    
    # Test input
    test_input = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
    expected = np.array([[1.1, 2.2, 3.3]], dtype=np.float32)  # Identity + bias
    
    print(f"\nTest input: {test_input[0]}")
    print(f"Expected output: {expected[0]}")
    
    # Test both engines
    print("\n🐍 Python Engine:")
    runtime_py = mle_runtime.MLERuntime(device='python')
    runtime_py.load_model('test_final_accuracy.mle')
    py_output = runtime_py.run([test_input])
    py_error = np.max(np.abs(py_output[0] - expected[0]))
    print(f"  Output: {py_output[0]}")
    print(f"  Error: {py_error:.6f}")
    print(f"  {'✅ PASS' if py_error < 1e-5 else '❌ FAIL'}")
    
    print("\n⚡ C++ Engine:")
    runtime_cpp = mle_runtime.MLERuntime(device='auto')
    runtime_cpp.load_model('test_final_accuracy.mle')
    cpp_output = runtime_cpp.run([test_input])
    cpp_error = np.max(np.abs(cpp_output[0] - expected[0]))
    print(f"  Output: {cpp_output[0]}")
    print(f"  Error: {cpp_error:.6f}")
    print(f"  {'✅ PASS' if cpp_error < 1e-5 else '❌ FAIL'}")
    
    # Overall result
    overall_success = py_error < 1e-5 and cpp_error < 1e-5
    print(f"\n🎯 Overall Result: {'✅ SUCCESS - ISSUE RESOLVED!' if overall_success else '❌ STILL FAILING'}")
    
    return overall_success

if __name__ == "__main__":
    success = test_original_scenario()
    
    # Clean up
    import os
    if os.path.exists('test_final_accuracy.mle'):
        os.remove('test_final_accuracy.mle')
    
    if success:
        print("\n🎉 The C++ engine accuracy issue has been completely resolved!")
        print("Both engines now correctly compute linear transformations with trained models.")
    else:
        print("\n⚠️  There may still be issues with more complex scenarios.")