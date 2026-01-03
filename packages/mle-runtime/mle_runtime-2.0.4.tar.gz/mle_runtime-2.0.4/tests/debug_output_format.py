#!/usr/bin/env python3
"""
Debug Output Format Issue
"""

import numpy as np
import mle_runtime

from sklearn.linear_model import LinearRegression

def test_output_format():
    """Test what the C++ engine is actually returning"""
    print("🔍 Testing Output Format")
    
    try:
        # Create runtime
        runtime = mle_runtime.MLERuntime(device='auto')
        
        # Create simple test model
        model_data = LinearRegression()
        model_data.fit(np.linspace(1,20,1).reshape(-1, 1) ,np.linspace(1,20,1))
        
        # Export and load model
        export_result = mle_runtime.export_model(model_data, "debug_output.mle", input_shape=(2,))
        runtime.load_model("debug_output.mle")
        
        # Test input
        test_input = [np.array([[1.0, 2.0]], dtype=np.float32)]
        
        print(f"Input: {test_input}")
        print(f"Input type: {type(test_input)}")
        print(f"Input[0] type: {type(test_input[0])}")
        print(f"Input[0] shape: {test_input[0].shape}")
        
        # Run inference
        outputs = runtime.run(test_input)
        
        print(f"\nOutput: {outputs}")
        print(f"Output type: {type(outputs)}")
        if outputs:
            print(f"Output length: {len(outputs)}")
            print(f"Output[0] type: {type(outputs[0])}")
            print(f"Output[0]: {outputs[0]}")
            
            # Try to access the output
            try:
                print(f"Output[0] shape: {outputs[0].shape}")
                print(f"Output[0] dtype: {outputs[0].dtype}")
                print(f"Output[0][0]: {outputs[0][0]}")
            except Exception as e:
                print(f"Error accessing output[0]: {e}")
                
                # Try different access patterns
                try:
                    print(f"Output[0] as list: {list(outputs[0])}")
                except Exception as e2:
                    print(f"Error converting to list: {e2}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_output_format()