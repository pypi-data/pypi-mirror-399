#!/usr/bin/env python3
"""
Test Engine Selection
"""

import numpy as np
import mle_runtime

def test_engine_selection():
    """Test which engine is actually being used"""
    print("🔧 Testing engine selection...")
    
    # Create simple model
    model_data = {
        'model_type': 'linear',
        'weights': [[2.0, 3.0]],
        'bias': [1.0]
    }
    
    # Export
    result = mle_runtime.export_model(model_data, 'engine_test.mle', input_shape=(2,))
    
    # Test with different devices
    devices = ['auto', 'cpu']
    
    for device in devices:
        print(f"\n--- Testing with device: {device} ---")
        
        runtime = mle_runtime.MLERuntime(device=device)
        runtime.load_model('engine_test.mle')
        
        # Check engine status
        try:
            perf_summary = runtime.get_performance_summary()
            print(f"C++ Available: {perf_summary['core_manager_stats']['cpp_available']}")
            print(f"Fallback Active: {perf_summary['core_manager_stats']['fallback_active']}")
        except Exception as e:
            print(f"Performance summary failed: {e}")
        
        # Test inference
        test_input = np.array([[1.0, 1.0]], dtype=np.float32)
        output = runtime.run([test_input])
        
        print(f"Input: {test_input[0]}")
        print(f"Output: {output[0] if output else 'None'}")
        
        # Check last metrics
        try:
            if hasattr(runtime, 'last_metrics'):
                print(f"Used C++ Core: {runtime.last_metrics.used_cpp_core}")
        except:
            pass

if __name__ == "__main__":
    test_engine_selection()