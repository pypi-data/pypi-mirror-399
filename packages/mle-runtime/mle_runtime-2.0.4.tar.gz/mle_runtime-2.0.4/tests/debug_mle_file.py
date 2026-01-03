#!/usr/bin/env python3
"""
Debug MLE File Contents
"""

import struct
import json
import numpy as np
from sklearn.linear_model import LinearRegression
import mle_runtime

def debug_mle_file(filename):
    """Debug what's actually in an MLE file"""
    print(f"🔍 Debugging MLE file: {filename}")
    
    try:
        with open(filename, 'rb') as f:
            # Read header
            magic = struct.unpack('<I', f.read(4))[0]
            version = struct.unpack('<I', f.read(4))[0]
            metadata_size = struct.unpack('<Q', f.read(8))[0]
            model_size = struct.unpack('<Q', f.read(8))[0]
            
            print(f"Magic: 0x{magic:08X}")
            print(f"Version: {version}")
            print(f"Metadata size: {metadata_size}")
            print(f"Model size: {model_size}")
            
            # Read metadata
            metadata_bytes = f.read(metadata_size)
            metadata_str = metadata_bytes.decode('utf-8')
            
            print(f"\nMetadata JSON:")
            print(metadata_str)
            
            # Parse JSON
            try:
                metadata = json.loads(metadata_str)
                print(f"\nParsed metadata:")
                for key, value in metadata.items():
                    if isinstance(value, list) and len(value) > 5:
                        print(f"  {key}: [list with {len(value)} elements]")
                    else:
                        print(f"  {key}: {value}")
            except Exception as e:
                print(f"JSON parsing failed: {e}")
                
    except Exception as e:
        print(f"File reading failed: {e}")

def create_and_debug_simple_model():
    """Create a simple model and debug its MLE file"""
    print("🔧 Creating simple model...")
    
    # Create simple data
    X = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    y = np.array([5.0, 11.0], dtype=np.float32)  # y = 2*x1 + 1.5*x2
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    print(f"Sklearn coefficients: {model.coef_}")
    print(f"Sklearn intercept: {model.intercept_}")
    
    # Create model data
    model_data = {
        'model_type': 'linear',
        'weights': model.coef_.reshape(1, -1).tolist(),
        'bias': [float(model.intercept_)]
    }
    
    print(f"Model data: {model_data}")
    
    # Export
    result = mle_runtime.export_model(model_data, 'debug_model.mle', input_shape=(2,))
    print(f"Export result: {result}")
    
    # Debug the file
    debug_mle_file('debug_model.mle')

if __name__ == "__main__":
    create_and_debug_simple_model()