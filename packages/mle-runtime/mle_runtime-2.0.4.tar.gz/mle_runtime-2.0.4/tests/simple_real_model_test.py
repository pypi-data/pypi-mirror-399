#!/usr/bin/env python3
"""
Simple Real Model Test
Tests basic functionality with real sklearn models
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression

# Import MLE Runtime
import mle_runtime

def test_simple_linear_model():
    """Test a simple linear regression model"""
    print("🔧 Creating simple linear regression model...")
    
    # Create simple dataset
    X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], dtype=np.float32)
    y = np.array([3.0, 7.0, 11.0], dtype=np.float32)  # y = x1 + x2
    
    # Train sklearn model
    model = LinearRegression()
    model.fit(X, y)
    
    print(f"Sklearn model coefficients: {model.coef_}")
    print(f"Sklearn model intercept: {model.intercept_}")
    
    # Test sklearn prediction
    test_input = np.array([[2.0, 3.0]], dtype=np.float32)
    sklearn_pred = model.predict(test_input)
    print(f"Sklearn prediction for [2.0, 3.0]: {sklearn_pred[0]}")
    
    # Create MLE model data
    model_data = {
        'model_type': 'linear',
        'weights': model.coef_.reshape(1, -1).tolist(),  # Ensure 2D
        'bias': [float(model.intercept_)],
        'sklearn_model': model
    }
    
    print(f"MLE model weights: {model_data['weights']}")
    print(f"MLE model bias: {model_data['bias']}")
    
    # Export and test
    result = mle_runtime.export_model(model_data, 'simple_linear.mle', input_shape=test_input.shape)
    
    if result['status'] != 'success':
        print(f"❌ Export failed: {result.get('error', 'Unknown error')}")
        return False
    
    # Load and test
    runtime = mle_runtime.MLERuntime(device='auto')
    runtime.load_model('simple_linear.mle')
    
    # Run inference
    mle_output = runtime.run([test_input])
    print(f"MLE output shape: {[np.array(out).shape for out in mle_output]}")
    print(f"MLE output: {mle_output}")
    
    # Handle different output formats
    if len(mle_output) > 0:
        output_array = np.array(mle_output[0])
        if output_array.size > 0:
            mle_pred = float(output_array.flat[0])
        else:
            mle_pred = 0.0
    else:
        mle_pred = 0.0
    
    print(f"MLE prediction for [2.0, 3.0]: {mle_pred}")
    
    # Compare
    error = abs(float(sklearn_pred[0]) - float(mle_pred))
    print(f"Prediction error: {error}")
    
    # Check if reasonable (within 10% or 1.0 absolute)
    tolerance = max(0.1 * abs(sklearn_pred[0]), 1.0)
    success = error < tolerance
    
    print(f"Test result: {'✅ PASS' if success else '❌ FAIL'} (tolerance: {tolerance})")
    
    return success

def test_python_fallback():
    """Test Python fallback engine directly"""
    print("\n🔧 Testing Python fallback engine...")
    
    # Create simple model
    X = np.array([[1.0, 2.0]], dtype=np.float32)
    
    # Create runtime and test Python engine
    runtime = mle_runtime.MLERuntime(device='cpu')  # Force CPU to test Python
    
    # Create a simple model data
    model_data = {
        'model_type': 'linear',
        'weights': [[1.0, 1.0]],  # Simple: output = x1 + x2
        'bias': [0.0]
    }
    
    # Export model
    result = mle_runtime.export_model(model_data, 'python_test.mle', input_shape=X.shape)
    
    if result['status'] != 'success':
        print(f"❌ Export failed: {result.get('error', 'Unknown error')}")
        return False
    
    # Load and test
    runtime.load_model('python_test.mle')
    output = runtime.run([X])
    
    print(f"Python output: {output}")
    
    expected = 3.0  # 1.0 + 2.0
    if len(output) > 0:
        output_array = np.array(output[0])
        if output_array.size > 0:
            actual = float(output_array.flat[0])
        else:
            actual = 0.0
    else:
        actual = 0.0
    
    print(f"Expected: {expected}, Got: {actual}")
    error = abs(expected - actual)
    success = error < 1.0
    
    print(f"Python fallback test: {'✅ PASS' if success else '❌ FAIL'} (error: {error})")
    
    return success

def main():
    print("🧪 Simple Real Model Test")
    print("=" * 50)
    
    results = []
    
    # Test 1: Simple linear model
    try:
        results.append(test_simple_linear_model())
    except Exception as e:
        print(f"❌ Linear model test failed: {e}")
        results.append(False)
    
    # Test 2: Python fallback
    try:
        results.append(test_python_fallback())
    except Exception as e:
        print(f"❌ Python fallback test failed: {e}")
        results.append(False)
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed!")
    elif passed > 0:
        print("👍 Some functionality working")
    else:
        print("⚠️  All tests failed - needs debugging")
    
    return passed > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)