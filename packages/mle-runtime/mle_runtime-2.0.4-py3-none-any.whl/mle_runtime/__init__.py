"""
MLE Runtime - Research-Grade Machine Learning Inference Engine

Advanced ML inference runtime with research-grade optimizations:
- Adaptive Execution Engine with Dynamic Optimization
- Intelligent C++/Python Fallback System
- Tensor Fusion Engine with SIMD Optimizations
- Real-time Performance Monitoring and Learning
- Memory-Aware Scheduling and Caching

Version: 2.0.4 - Research Edition with Advanced Features
"""

import time
import numpy as np

__version__ = "2.0.4"
__author__ = "Vinay Kamble"
__email__ = "vinaykamble289@gmail.com"
__license__ = "MIT"

# Core imports with intelligent fallback
from .mle_runtime import (
    MLERuntime, 
    MLEFormat, 
    CompressionUtils, 
    SecurityUtils,
    load_model,
    get_version_info,
    get_supported_operators,
    get_system_performance_info,
    enable_research_mode
)

# Convenience functions
def export_model(model, output_path, input_shape=None, **kwargs):
    """
    Universal model exporter - automatically detects model type and exports
    
    Args:
        model: Trained model from any supported framework
        output_path: Path to save .mle file
        input_shape: Input shape tuple (required for some models)
        **kwargs: Additional export options
    
    Returns:
        dict: Export information and statistics
    """
    try:
        import struct
        import json
        import pickle
        import time
        from pathlib import Path
        
        output_path = Path(output_path)
        
        # Prepare model data
        if isinstance(model, dict):
            # Dictionary-based model
            model_data = model.copy()
        elif hasattr(model, 'state_dict'):
            # PyTorch-like model
            model_data = {'state_dict': model.state_dict()}
        elif hasattr(model, 'get_weights'):
            # Keras-like model
            model_data = {'weights': model.get_weights()}
        else:
            # Generic model - try to serialize
            model_data = {'model': model}
        
        # Add metadata with actual model parameters
        metadata = {
            'version': 2,
            'created_at': time.time(),
            'input_shape': input_shape,
            'model_type': kwargs.get('model_type', 'generic'),
            'framework': kwargs.get('framework', 'mle_runtime'),
            'compression': kwargs.get('compression', 'none'),
            'quantization': kwargs.get('quantization', 'none')
        }
        
        # Include model weights in metadata for C++ engine access
        if isinstance(model_data, dict):
            # Copy all model parameters to metadata for C++ engine
            for key in ['weights', 'bias', 'model_type', 'n_estimators', 'learning_rate', 'feature_importances', 'tree_structure']:
                if key in model_data:
                    if isinstance(model_data[key], np.ndarray):
                        metadata[key] = model_data[key].tolist()
                    else:
                        metadata[key] = model_data[key]
        
        # Serialize model data
        model_bytes = _serialize_model_data(model_data)
        metadata_bytes = json.dumps(metadata).encode('utf-8')
        
        # Write MLE file
        with open(output_path, 'wb') as f:
            # Write header
            f.write(struct.pack('<I', 0x00454C4D))  # MLE magic
            f.write(struct.pack('<I', 2))  # Version
            f.write(struct.pack('<Q', len(metadata_bytes)))  # Metadata size
            f.write(struct.pack('<Q', len(model_bytes)))  # Model size
            
            # Write metadata and model data
            f.write(metadata_bytes)
            f.write(model_bytes)
        
        return {
            'status': 'success',
            'file_path': str(output_path),
            'file_size': len(metadata_bytes) + len(model_bytes) + 24,  # Header size
            'metadata': metadata
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def _serialize_model_data(model_data):
    """Serialize model data to bytes"""
    import pickle
    try:
        return pickle.dumps(model_data)
    except Exception as e:
        # Fallback to JSON for simple data
        try:
            # Convert numpy arrays to lists for JSON serialization
            json_data = _convert_numpy_to_json(model_data)
            return json.dumps(json_data).encode('utf-8')
        except:
            # Final fallback
            return str(model_data).encode('utf-8')

def _convert_numpy_to_json(obj):
    """Convert numpy arrays to JSON-serializable format"""
    if isinstance(obj, np.ndarray):
        return {
            '__numpy_array__': True,
            'data': obj.tolist(),
            'dtype': str(obj.dtype),
            'shape': obj.shape
        }
    elif isinstance(obj, dict):
        return {k: _convert_numpy_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_convert_numpy_to_json(item) for item in obj]
    else:
        return obj

def benchmark_model(model_path, inputs, num_runs=100):
    """
    Benchmark model performance
    
    Args:
        model_path: Path to .mle model file
        inputs: Input data for benchmarking
        num_runs: Number of benchmark iterations
    
    Returns:
        dict: Performance statistics
    """
    runtime = load_model(model_path)
    return runtime.benchmark(inputs, num_runs)

def inspect_model(model_path):
    """
    Inspect model file and return information
    
    Args:
        model_path: Path to .mle model file
    
    Returns:
        dict: Model information
    """
    runtime = MLERuntime()
    runtime.load_model(model_path)
    return runtime.get_model_info()

# Export public API
__all__ = [
    # Core classes
    'MLERuntime', 'MLEFormat',
    'CompressionUtils', 'SecurityUtils',
    
    # Main functions
    'load_model', 'inspect_model', 'export_model', 'benchmark_model',
    
    # Utilities
    'get_version_info', 'get_supported_operators', 'get_system_performance_info',
    'enable_research_mode'
]

# Make inspect_model available at module level
globals()['inspect_model'] = inspect_model