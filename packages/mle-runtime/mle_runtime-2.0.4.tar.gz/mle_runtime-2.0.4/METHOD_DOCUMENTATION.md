# MLE Runtime - Method Documentation

## Core Classes and Methods

### MLERuntime Class

The main runtime class for loading and executing MLE models.

#### `__init__(device: str = "auto")`
Initialize the MLE Runtime with specified device.

**Parameters:**
- `device` (str): Target device ("cpu", "cuda", "auto", "hybrid")

**Example:**
```python
runtime = mle_runtime.MLERuntime(device="auto")
```

#### `load_model(path: Union[str, Path], **kwargs) -> Dict[str, Any]`
Load an MLE model file with intelligent engine selection.

**Parameters:**
- `path` (str/Path): Path to the .mle model file
- `**kwargs`: Additional loading options

**Returns:**
- `dict`: Loading results and engine information

**Example:**
```python
result = runtime.load_model('model.mle')
print(f"C++ loaded: {result['cpp_loaded']}")
print(f"Python loaded: {result['python_loaded']}")
```

#### `run(inputs: List[np.ndarray]) -> List[np.ndarray]`
Run inference with adaptive engine selection.

**Parameters:**
- `inputs` (List[np.ndarray]): List of input arrays

**Returns:**
- `List[np.ndarray]`: Model predictions

**Features:**
- Automatic input validation and sanitization
- Intelligent C++/Python engine selection
- Performance monitoring and optimization
- Graceful fallback handling

**Example:**
```python
import numpy as np
inputs = [np.random.randn(1, 20).astype(np.float32)]
predictions = runtime.run(inputs)
print(f"Predictions: {predictions[0]}")
```

#### `benchmark(inputs: List[np.ndarray], num_runs: int = 100) -> Dict[str, Any]`
Comprehensive benchmarking with both engines.

**Parameters:**
- `inputs` (List[np.ndarray]): Input data for benchmarking
- `num_runs` (int): Number of benchmark iterations

**Returns:**
- `dict`: Detailed performance statistics

**Example:**
```python
results = runtime.benchmark([test_data], num_runs=50)
print(f"Mean time: {results['python_results']['mean_time_ms']:.2f}ms")
print(f"Throughput: {results['python_results']['throughput_ops_per_sec']:.1f} ops/sec")
```

#### `get_model_info() -> Dict[str, Any]`
Get comprehensive model information.

**Returns:**
- `dict`: Model metadata, engine status, and performance stats

**Example:**
```python
info = runtime.get_model_info()
print(f"Model path: {info['model_path']}")
print(f"Engines available: {info['engines_available']}")
print(f"Total executions: {info['execution_stats']['total_executions']}")
```

#### `get_performance_summary() -> Dict[str, Any]`
Get comprehensive performance summary.

**Returns:**
- `dict`: Performance metrics and optimization suggestions

**Example:**
```python
summary = runtime.get_performance_summary()
print(f"Average execution time: {summary['runtime_stats']['average_execution_time_ms']:.2f}ms")
print(f"C++ core usage: {summary['core_manager_stats']['cpp_available']}")
```

#### `enable_adaptive_optimization(enable: bool = True)`
Enable adaptive optimization features.

**Parameters:**
- `enable` (bool): Whether to enable adaptive optimization

**Example:**
```python
runtime.enable_adaptive_optimization(True)
```

#### `set_performance_target(target_ms: float)`
Set performance target for optimization.

**Parameters:**
- `target_ms` (float): Target execution time in milliseconds

**Example:**
```python
runtime.set_performance_target(10.0)  # Target 10ms execution
```

### Utility Classes

#### CompressionUtils
Utilities for model compression and quantization.

**Methods:**
- `quantize_weights_int8(weights)`: Quantize FP32 weights to INT8
- `dequantize_weights_int8(quantized, scale, zero_point)`: Dequantize INT8 back to FP32
- `quantize_weights_fp16(weights)`: Quantize FP32 weights to FP16
- `compress_data(data, compression_type)`: Compress data using specified algorithm
- `decompress_data(data, compression_type, size)`: Decompress data

**Example:**
```python
from mle_runtime import CompressionUtils

# Quantize weights to INT8
quantized, scale, zero_point = CompressionUtils.quantize_weights_int8(weights)
print(f"Quantized shape: {quantized.shape}, Scale: {scale}, Zero point: {zero_point}")

# Dequantize back to FP32
restored = CompressionUtils.dequantize_weights_int8(quantized, scale, zero_point)
```

#### SecurityUtils
Utilities for model security and integrity.

**Methods:**
- `compute_checksum(data)`: Compute CRC32 checksum
- `compute_hash(data)`: Compute SHA256 hash
- `generate_keypair()`: Generate ED25519 key pair
- `sign_data(data, private_key)`: Sign data with private key
- `verify_signature(data, signature, public_key)`: Verify signature

**Example:**
```python
from mle_runtime import SecurityUtils

# Generate key pair
public_key, private_key = SecurityUtils.generate_keypair()

# Sign model data
with open('model.mle', 'rb') as f:
    model_data = f.read()
signature = SecurityUtils.sign_data(model_data, private_key)

# Verify signature
is_valid = SecurityUtils.verify_signature(model_data, signature, public_key)
print(f"Signature valid: {is_valid}")
```

## Convenience Functions

### `load_model(path: Union[str, Path], device: str = "auto", **kwargs) -> MLERuntime`
Load MLE model with intelligent engine selection.

**Parameters:**
- `path` (str/Path): Path to model file
- `device` (str): Target device
- `**kwargs`: Additional options

**Returns:**
- `MLERuntime`: Loaded runtime instance

**Example:**
```python
import mle_runtime as mle

runtime = mle.load_model('model.mle', device='auto')
predictions = runtime.run([input_data])
```

### `export_model(model, output_path, input_shape=None, **kwargs)`
Universal model exporter - automatically detects model type and exports.

**Parameters:**
- `model`: Trained model from any supported framework
- `output_path` (str): Path to save .mle file
- `input_shape` (tuple): Input shape (required for some models)
- `**kwargs`: Additional export options

**Returns:**
- `dict`: Export information and statistics

**Example:**
```python
from sklearn.ensemble import RandomForestClassifier
import mle_runtime as mle

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Export to MLE format
result = mle.export_model(model, 'rf_model.mle', input_shape=(1, 20))
print(f"Export status: {result['status']}")
print(f"File size: {result['file_size']} bytes")
```

### `inspect_model(model_path)`
Inspect model file and return information.

**Parameters:**
- `model_path` (str): Path to .mle model file

**Returns:**
- `dict`: Model information

**Example:**
```python
info = mle_runtime.inspect_model('model.mle')
print(f"Model type: {info['model_metadata'].get('model_type', 'unknown')}")
print(f"File size: {info['file_size_bytes']} bytes")
```

### `benchmark_model(model_path, inputs, num_runs=100)`
Benchmark model performance.

**Parameters:**
- `model_path` (str): Path to .mle model file
- `inputs`: Input data for benchmarking
- `num_runs` (int): Number of benchmark iterations

**Returns:**
- `dict`: Performance statistics

**Example:**
```python
results = mle_runtime.benchmark_model('model.mle', [test_data], num_runs=50)
print(f"Mean time: {results['python_results']['mean_time_ms']:.2f}ms")
```

### `get_version_info() -> Dict[str, Any]`
Get version information with research features.

**Returns:**
- `dict`: Version and feature information

**Example:**
```python
info = mle_runtime.get_version_info()
print(f"Version: {info['version']}")
print(f"C++ core available: {info['cpp_core_available']}")
print(f"Research features: {info['research_features']}")
```

### `get_supported_operators() -> List[str]`
Get list of supported operators.

**Returns:**
- `List[str]`: List of supported operator names

**Example:**
```python
operators = mle_runtime.get_supported_operators()
print(f"Supported operators: {len(operators)}")
for op in operators[:10]:  # Show first 10
    print(f"  - {op}")
```

### `get_system_performance_info() -> Dict[str, Any]`
Get comprehensive system performance information.

**Returns:**
- `dict`: System and performance information

**Example:**
```python
info = mle_runtime.get_system_performance_info()
print(f"C++ core available: {info['cpp_core_available']}")
print(f"Fallback active: {info['fallback_active']}")
if 'system_info' in info:
    sys_info = info['system_info']
    print(f"CPU: {sys_info['cpu_name']}")
    print(f"Cores: {sys_info['cpu_cores']}")
    print(f"CUDA available: {sys_info['cuda_available']}")
```

### `enable_research_mode()`
Enable all research features and optimizations.

**Example:**
```python
mle_runtime.enable_research_mode()
# Enables:
# - Adaptive execution optimization
# - Performance monitoring and learning
# - Intelligent C++/Python switching
# - Advanced memory management
```

## Advanced Usage Patterns

### 1. Production Deployment
```python
import mle_runtime as mle
import numpy as np

# Load model once at startup
runtime = mle.load_model('production_model.mle')

# Enable optimizations
runtime.enable_adaptive_optimization(True)
runtime.set_performance_target(5.0)  # 5ms target

def predict(features):
    """Production prediction function"""
    input_data = np.array(features, dtype=np.float32).reshape(1, -1)
    predictions = runtime.run([input_data])
    return predictions[0].tolist()
```

### 2. Batch Processing
```python
import mle_runtime as mle
import numpy as np

runtime = mle.load_model('batch_model.mle')

def process_batch(batch_data, batch_size=32):
    """Process data in batches for optimal performance"""
    results = []
    for i in range(0, len(batch_data), batch_size):
        batch = batch_data[i:i+batch_size]
        batch_array = np.array(batch, dtype=np.float32)
        predictions = runtime.run([batch_array])
        results.extend(predictions[0].tolist())
    return results
```

### 3. Performance Monitoring
```python
import mle_runtime as mle

runtime = mle.load_model('monitored_model.mle')

# Run some predictions
for i in range(100):
    test_input = np.random.randn(1, 20).astype(np.float32)
    predictions = runtime.run([test_input])

# Get performance summary
summary = runtime.get_performance_summary()
print(f"Average execution time: {summary['runtime_stats']['average_execution_time_ms']:.2f}ms")
print(f"C++ core usage rate: {summary['cpp_core_usage_rate']:.1%}")
print("Optimization suggestions:")
for suggestion in summary['optimization_suggestions']:
    print(f"  - {suggestion}")
```

### 4. Model Comparison
```python
import mle_runtime as mle
import numpy as np

# Load multiple models
models = {
    'rf': mle.load_model('random_forest.mle'),
    'xgb': mle.load_model('xgboost.mle'),
    'nn': mle.load_model('neural_net.mle')
}

# Benchmark all models
test_data = [np.random.randn(100, 20).astype(np.float32)]
results = {}

for name, runtime in models.items():
    benchmark = runtime.benchmark(test_data, num_runs=50)
    results[name] = benchmark['python_results']['mean_time_ms']

# Show results
print("Model Performance Comparison:")
for name, time_ms in sorted(results.items(), key=lambda x: x[1]):
    print(f"  {name}: {time_ms:.2f}ms")
```

## Error Handling

### Common Error Patterns
```python
import mle_runtime as mle
import numpy as np

try:
    # Load model
    runtime = mle.load_model('model.mle')
    
    # Prepare input
    input_data = np.array([[1, 2, 3]], dtype=np.float32)
    
    # Run prediction
    predictions = runtime.run([input_data])
    print(f"Predictions: {predictions}")
    
except FileNotFoundError:
    print("Model file not found")
except ValueError as e:
    print(f"Input validation error: {e}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Input Validation
```python
def safe_predict(runtime, raw_input):
    """Safe prediction with input validation"""
    try:
        # Convert to numpy array
        if not isinstance(raw_input, np.ndarray):
            raw_input = np.array(raw_input)
        
        # Ensure correct dtype
        if raw_input.dtype != np.float32:
            raw_input = raw_input.astype(np.float32)
        
        # Ensure 2D shape
        if raw_input.ndim == 1:
            raw_input = raw_input.reshape(1, -1)
        
        # Check for invalid values
        if np.any(np.isnan(raw_input)) or np.any(np.isinf(raw_input)):
            raw_input = np.nan_to_num(raw_input)
        
        # Run prediction
        predictions = runtime.run([raw_input])
        return predictions[0]
        
    except Exception as e:
        print(f"Prediction failed: {e}")
        return None
```

This documentation covers all the main methods and usage patterns for MLE Runtime. The library provides a comprehensive set of tools for high-performance machine learning inference with intelligent fallback capabilities and extensive monitoring features.