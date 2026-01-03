#!/usr/bin/env python3
"""
Debug C++ Engine Input Format Issue
"""

import numpy as np
import mle_runtime


from sklearn.linear_model import LinearRegression
def test_cpp_engine_directly():
    """Test C++ engine directly to debug input format issue"""
    print("🔍 Testing C++ Engine Input Format")
    
    try:
        # Create runtime
        runtime = mle_runtime.MLERuntime(device='cpu')
        
        # Create simple test model
        model_data = LinearRegression()
        model_data.fit(np.linspace(1,20,1).reshape(-1, 1) ,np.linspace(1,20,1))
        
        
        # Export model
        export_result = mle_runtime.export_model(model_data, "debug_test.mle", input_shape=(2,))
        print(f"Export result: {export_result}")
        
        # Load model
        runtime.load_model("debug_test.mle")
        # print(f"Load result - C++: {load_result.get('cpp_loaded', False)}, Python: {load_result.get('python_loaded', False)}")
        
        # Test different input formats
        test_inputs = [
            # Format 1: List of numpy arrays
            [np.array([[1.0, 2.0]], dtype=np.float32)],
            
            # Format 2: Single numpy array
            np.array([[1.0, 2.0]], dtype=np.float32),
        ]
        
        for i, test_input in enumerate(test_inputs):
            print(f"\n--- Test Input Format {i+1} ---")
            print(f"Input type: {type(test_input)}")
            if isinstance(test_input, list):
                print(f"Input shape: {[inp.shape for inp in test_input]}")
                print(f"Input dtype: {[inp.dtype for inp in test_input]}")
            else:
                print(f"Input shape: {test_input.shape}")
                print(f"Input dtype: {test_input.dtype}")
            
            try:
                # Test C++ engine directly if available
                if runtime:
                    print("Testing C++ engine directly...")
                    
                    # Convert to the format expected by C++ engine
                    if isinstance(test_input, list):
                        # For list of numpy arrays, convert each array to list and flatten
                        cpp_inputs = []
                        for inp in test_input:
                            if inp.ndim == 1:
                                inp_2d = inp.reshape(1, -1)
                            else:
                                inp_2d = inp
                            cpp_inputs.extend(inp_2d.tolist())  # Flatten the structure
                    else:
                        # For single numpy array
                        if test_input.ndim == 1:
                            test_input = test_input.reshape(1, -1)
                        cpp_inputs = test_input.tolist()  # This should give [[1.0, 2.0]]
                    
                    print(f"C++ input format: {type(cpp_inputs)}")
                    print(f"C++ input structure: {[type(inp) for inp in cpp_inputs]}")
                    print(f"C++ input shapes: {[len(inp) if isinstance(inp, list) else 'not list' for inp in cpp_inputs]}")
                    
                    cpp_outputs = runtime.run(cpp_inputs)
                    print(f"✅ C++ engine success: {cpp_outputs}")
                    
                else:
                    print("❌ C++ engine not available")
                
                # Test full runtime
                print("Testing full runtime...")
                outputs = runtime.run(test_input if isinstance(test_input, list) else [test_input])
                print(f"✅ Runtime success: {[out.shape for out in outputs]}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cpp_engine_directly()