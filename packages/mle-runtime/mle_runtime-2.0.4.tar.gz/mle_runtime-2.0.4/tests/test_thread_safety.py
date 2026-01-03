#!/usr/bin/env python3
"""
Test thread safety issue specifically
"""

import numpy as np
import mle_runtime
import threading
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor

def test_thread_safety():
    """Test thread safety with detailed error tracking"""
    print("🔍 Testing Thread Safety")
    
    try:
        # Create test model
        model_data = {
            'weights': np.random.randn(5, 3).astype(np.float32),
            'bias': np.zeros(3, dtype=np.float32),
            'type': 'linear'
        }
        
        temp_dir = tempfile.mkdtemp()
        export_path = os.path.join(temp_dir, "thread_test.mle")
        result = mle_runtime.export_model(model_data, export_path, input_shape=(5,))
        
        test_input = [np.array([[1.0, 2.0, 3.0, 4.0, 5.0]], dtype=np.float32)]
        
        def safe_thread_inference(thread_id):
            """Thread-safe inference with detailed error handling"""
            try:
                print(f"Thread {thread_id}: Starting")
                
                # Create new runtime instance for thread safety
                thread_runtime = mle_runtime.MLERuntime(device='auto')
                print(f"Thread {thread_id}: Runtime created")
                
                thread_runtime.load_model(export_path)
                print(f"Thread {thread_id}: Model loaded")
                
                outputs = thread_runtime.run(test_input)
                print(f"Thread {thread_id}: Inference completed")
                
                if outputs:
                    print(f"Thread {thread_id}: outputs type = {type(outputs)}")
                    print(f"Thread {thread_id}: outputs length = {len(outputs)}")
                    print(f"Thread {thread_id}: outputs[0] type = {type(outputs[0])}")
                    print(f"Thread {thread_id}: outputs[0] shape = {outputs[0].shape}")
                    
                    # The problematic line - let's debug it
                    try:
                        result = outputs[0].copy()
                        print(f"Thread {thread_id}: ✅ copy() successful")
                        return result
                    except Exception as copy_error:
                        print(f"Thread {thread_id}: ❌ copy() failed: {copy_error}")
                        print(f"Thread {thread_id}: outputs[0] = {outputs[0]}")
                        print(f"Thread {thread_id}: type(outputs[0]) = {type(outputs[0])}")
                        
                        # Try alternative approaches
                        try:
                            result = np.array(outputs[0])
                            print(f"Thread {thread_id}: ✅ np.array() worked as fallback")
                            return result
                        except Exception as array_error:
                            print(f"Thread {thread_id}: ❌ np.array() also failed: {array_error}")
                            return None
                else:
                    print(f"Thread {thread_id}: No outputs")
                    return None
                    
            except Exception as e:
                print(f"Thread {thread_id}: ❌ Thread inference failed: {e}")
                import traceback
                traceback.print_exc()
                return None
        
        # Test with multiple threads
        print("\nTesting with ThreadPoolExecutor:")
        thread_results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(safe_thread_inference, i+1) for i in range(5)]
            for i, future in enumerate(futures):
                try:
                    result = future.result(timeout=15)
                    if result is not None:
                        thread_results.append(result)
                        print(f"Main: Thread {i+1} succeeded")
                    else:
                        print(f"Main: Thread {i+1} returned None")
                except Exception as e:
                    print(f"Main: Thread {i+1} exception: {e}")
        
        print(f"\nSuccessful thread results: {len(thread_results)}")
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_thread_safety()