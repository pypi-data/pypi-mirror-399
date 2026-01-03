#!/usr/bin/env python3
"""
Debug C++ Parsing Issues
"""

import numpy as np
import json
import struct
from sklearn.linear_model import LinearRegression
import mle_runtime

def create_debug_model():
    """Create a simple model and check parsing"""
    print("🔧 Creating debug model...")
    
    # Simple model with known weights
    model_data = {
        'model_type': 'linear',
        'weights': [[2.0, 3.0]],  # Simple: output = 2*x1 + 3*x2
        'bias': [1.0]
    }
    
    print(f"Original model data: {model_data}")
    
    # Export to MLE
    result = mle_runtime.export_model(model_data, 'debug_parsing.mle', input_shape=(2,))
    print(f"Export result: {result}")
    
    # Read the MLE file to see what's actually stored
    with open('debug_parsing.mle', 'rb') as f:
        # Read header
        magic = struct.unpack('<I', f.read(4))[0]
        version = struct.unpack('<I', f.read(4))[0]
        metadata_size = struct.unpack('<Q', f.read(8))[0]
        model_size = struct.unpack('<Q', f.read(8))[0]
        
        print(f"Header: magic=0x{magic:08X}, version={version}, metadata_size={metadata_size}")
        
        # Read metadata
        metadata_bytes = f.read(metadata_size)
        metadata_str = metadata_bytes.decode('utf-8')
        
        print(f"\nActual metadata in file:")
        print(repr(metadata_str))  # Use repr to see exact content
        
        # Parse JSON
        try:
            metadata = json.loads(metadata_str)
            print(f"\nParsed weights: {metadata.get('weights', 'NOT FOUND')}")
            print(f"Parsed bias: {metadata.get('bias', 'NOT FOUND')}")
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Problematic JSON: {metadata_str[:200]}...")
    
    # Test with MLE Runtime
    runtime = mle_runtime.MLERuntime(device='auto')
    runtime.load_model('debug_parsing.mle')
    
    # Test prediction
    test_input = np.array([[1.0, 1.0]], dtype=np.float32)
    expected = 2.0 * 1.0 + 3.0 * 1.0 + 1.0  # = 6.0
    
    output = runtime.run([test_input])
    actual = output[0][0] if output and len(output[0]) > 0 else 0.0
    
    print(f"\nTest input: {test_input[0]}")
    print(f"Expected output: {expected}")
    print(f"Actual output: {actual}")
    print(f"Error: {abs(expected - float(actual))}")
    
    return abs(expected - float(actual)) < 0.1

if __name__ == "__main__":
    success = create_debug_model()
    print(f"\nDebug result: {'✅ PASS' if success else '❌ FAIL'}")