#!/usr/bin/env python3
"""
Debug the slice error in validation tests
"""

import numpy as np
import mle_runtime
import tempfile
import os

def test_slice_error():
    """Reproduce the slice error"""
    print("🔍 Testing Slice Error")
    
    try:
        # Create runtime
        runtime = mle_runtime.MLERuntime(device='auto')
        
        # Create simple test model
        model_data = {
            'weights': np.random.randn(5, 3).astype(np.float32),
            'bias': np.zeros(3, dtype=np.float32),
            'type': 'linear'
        }
        
        export_path = "slice_debug.mle"
        result = mle_runtime.export_model(model_data, export_path, input_shape=(5,))
        runtime.load_model(export_path)
        
        # Test input
        test_input = [np.array([[1.0, 2.0, 3.0, 4.0, 5.0]], dtype=np.float32)]
        
        # Run inference multiple times
        sequential_outputs = []
        for i in range(3):
            outputs = runtime.run(test_input)
            print(f"Run {i+1}:")
            print(f"  outputs type: {type(outputs)}")
            print(f"  outputs length: {len(outputs) if outputs else 'None'}")
            if outputs:
                print(f"  outputs[0] type: {type(outputs[0])}")
                print(f"  outputs[0] shape: {outputs[0].shape}")
                print(f"  outputs[0]: {outputs[0]}")
                
                # Try the operations that might cause slice error
                try:
                    # This is what the validation test does
                    copied_output = outputs[0].copy()
                    sequential_outputs.append(copied_output)
                    print(f"  ✅ copy() worked")
                except Exception as e:
                    print(f"  ❌ copy() failed: {e}")
                
                try:
                    # Test array access
                    first_element = outputs[0][0]
                    print(f"  ✅ outputs[0][0] = {first_element}")
                except Exception as e:
                    print(f"  ❌ outputs[0][0] failed: {e}")
        
        # Test variance calculation (this might be where the error occurs)
        if len(sequential_outputs) > 1:
            print(f"\nTesting variance calculation:")
            try:
                output_array = np.array(sequential_outputs)
                print(f"  output_array shape: {output_array.shape}")
                print(f"  output_array type: {type(output_array)}")
                
                variance = np.var(output_array, axis=0)
                print(f"  ✅ variance calculation worked: {variance}")
                
                max_variance = np.max(variance)
                print(f"  ✅ max variance: {max_variance}")
                
            except Exception as e:
                print(f"  ❌ variance calculation failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Clean up
        if os.path.exists(export_path):
            os.remove(export_path)
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_slice_error()