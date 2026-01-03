"""
MLE Runtime Core Validation
Ensures C++ core is available and functional at import time
"""

import sys
import platform
from typing import Dict, Any

def validate_cpp_core() -> Dict[str, Any]:
    """
    Validate C++ core availability and functionality
    This function is called at import time to ensure the C++ core is working
    """
    validation_results = {
        'core_available': False,
        'version': None,
        'build_info': {},
        'supported_devices': [],
        'supported_operators': [],
        'cuda_available': False,
        'compression_available': False,
        'crypto_available': False,
        'platform_compatible': True,
        'errors': []
    }
    
    try:
        # Import the C++ core module
        from . import _mle_core as core
        validation_results['core_available'] = True
        
        # Get version information
        try:
            validation_results['version'] = core.get_version()
        except AttributeError:
            validation_results['errors'].append("Version information not available")
        
        # Get build information
        try:
            validation_results['build_info'] = core.get_build_info()
        except AttributeError:
            validation_results['errors'].append("Build information not available")
        
        # Get supported devices
        try:
            validation_results['supported_devices'] = core.get_supported_devices()
        except AttributeError:
            validation_results['errors'].append("Device information not available")
        
        # Get supported operators
        try:
            validation_results['supported_operators'] = core.get_supported_operators()
        except AttributeError:
            validation_results['errors'].append("Operator information not available")
        
        # Check feature availability
        try:
            validation_results['cuda_available'] = getattr(core, 'CUDA_AVAILABLE', False)
            validation_results['compression_available'] = getattr(core, 'COMPRESSION_AVAILABLE', False)
            validation_results['crypto_available'] = getattr(core, 'CRYPTO_AVAILABLE', False)
        except AttributeError:
            validation_results['errors'].append("Feature flags not available")
        
        # Test basic functionality
        try:
            engine = core.Engine(core.Device.CPU)
            validation_results['basic_functionality'] = True
        except Exception as e:
            validation_results['errors'].append(f"Basic functionality test failed: {e}")
            validation_results['basic_functionality'] = False
        
    except ImportError as e:
        validation_results['core_available'] = False
        validation_results['errors'].append(f"C++ core import failed: {e}")
        
        # Provide detailed error information
        system_info = get_system_info()
        validation_results['system_info'] = system_info
        
        # Generate helpful error message
        error_msg = generate_error_message(e, system_info)
        validation_results['detailed_error'] = error_msg
    
    return validation_results

def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging"""
    return {
        'platform': platform.platform(),
        'system': platform.system(),
        'machine': platform.machine(),
        'architecture': platform.architecture(),
        'python_version': sys.version,
        'python_executable': sys.executable,
    }

def generate_error_message(import_error: ImportError, system_info: Dict[str, Any]) -> str:
    """Generate a helpful error message based on the import error and system info"""
    
    base_msg = (
        "MLE Runtime C++ Core Not Available\n"
        "====================================\n\n"
        f"Import Error: {import_error}\n\n"
        f"System Information:\n"
        f"- Platform: {system_info['platform']}\n"
        f"- System: {system_info['system']}\n"
        f"- Architecture: {system_info['machine']}\n"
        f"- Python: {system_info['python_version']}\n\n"
    )
    
    # Platform-specific guidance
    system = system_info['system'].lower()
    
    if system == 'windows':
        platform_msg = (
            "Windows Installation Issues:\n"
            "- Ensure Visual Studio Build Tools are installed\n"
            "- Install Microsoft Visual C++ Redistributable\n"
            "- Try: pip install --force-reinstall mle-runtime\n"
            "- Build from source: python setup_cpp_mandatory.py build_ext --inplace\n"
        )
    elif system == 'darwin':  # macOS
        platform_msg = (
            "macOS Installation Issues:\n"
            "- Install Xcode Command Line Tools: xcode-select --install\n"
            "- Install CMake: brew install cmake\n"
            "- Try: pip install --force-reinstall mle-runtime\n"
            "- Build from source: python setup_cpp_mandatory.py build_ext --inplace\n"
        )
    elif system == 'linux':
        platform_msg = (
            "Linux Installation Issues:\n"
            "- Install build essentials: sudo apt-get install build-essential cmake\n"
            "- Install Python dev headers: sudo apt-get install python3-dev\n"
            "- Try: pip install --force-reinstall mle-runtime\n"
            "- Build from source: python setup_cpp_mandatory.py build_ext --inplace\n"
        )
    else:
        platform_msg = (
            "Platform-Specific Issues:\n"
            "- Ensure C++ compiler is available\n"
            "- Install CMake (version 3.22 or higher)\n"
            "- Install Python development headers\n"
            "- Try building from source\n"
        )
    
    solutions_msg = (
        "\nCommon Solutions:\n"
        "1. Reinstall package: pip uninstall mle-runtime && pip install mle-runtime\n"
        "2. Update pip/setuptools: pip install --upgrade pip setuptools wheel\n"
        "3. Install with verbose output: pip install -v mle-runtime\n"
        "4. Check for pre-built wheels: pip install --only-binary=mle-runtime mle-runtime\n"
        "5. Build from source with debug: python setup_cpp_mandatory.py build_ext --debug\n\n"
        "For support, visit: https://github.com/mle-runtime/mle-runtime/issues\n"
    )
    
    return base_msg + platform_msg + solutions_msg

def ensure_cpp_core():
    """
    Ensure C++ core is available, raise detailed error if not
    This is called at module import time
    """
    validation = validate_cpp_core()
    
    if not validation['core_available']:
        error_msg = validation.get('detailed_error', 'C++ core not available')
        raise RuntimeError(error_msg)
    
    if validation['errors']:
        import warnings
        warnings.warn(f"C++ core loaded with warnings: {'; '.join(validation['errors'])}")
    
    return validation

# Perform validation at import time
_CORE_VALIDATION = ensure_cpp_core()

def get_core_info() -> Dict[str, Any]:
    """Get information about the loaded C++ core"""
    return _CORE_VALIDATION.copy()

def is_cuda_available() -> bool:
    """Check if CUDA support is available"""
    return _CORE_VALIDATION.get('cuda_available', False)

def is_compression_available() -> bool:
    """Check if compression support is available"""
    return _CORE_VALIDATION.get('compression_available', False)

def is_crypto_available() -> bool:
    """Check if cryptographic features are available"""
    return _CORE_VALIDATION.get('crypto_available', False)

def get_supported_devices() -> list:
    """Get list of supported devices"""
    return _CORE_VALIDATION.get('supported_devices', ['CPU'])

def get_supported_operators() -> list:
    """Get list of supported operators"""
    return _CORE_VALIDATION.get('supported_operators', [])