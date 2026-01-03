#include "device.hpp"
#include "loader.hpp"
#include <thread>
#include <cstring>
#include <numeric>
#include <map>
#include <unordered_map>
#include <sstream>

#ifdef ENABLE_COMPRESSION
#include <zlib.h>
#endif

namespace mle {

// Constants
const std::string VERSION = "2.0.4";
const std::string BUILD_DATE = __DATE__ " " __TIME__;

#ifdef ENABLE_CUDA
const bool CUDA_AVAILABLE = true;
#else
const bool CUDA_AVAILABLE = false;
#endif

#ifdef ENABLE_COMPRESSION
const bool COMPRESSION_AVAILABLE = true;
#else
const bool COMPRESSION_AVAILABLE = false;
#endif

#ifdef ENABLE_CRYPTO
const bool CRYPTO_AVAILABLE = true;
#else
const bool CRYPTO_AVAILABLE = false;
#endif

// Global state
static int g_num_threads = std::thread::hardware_concurrency();

std::string get_version() {
    return VERSION;
}

std::string get_build_info() {
    std::stringstream ss;
    ss << "MLE Runtime " << VERSION << "\n";
    ss << "Build Date: " << BUILD_DATE << "\n";
    
    ss << "Compiler: ";
#ifdef _MSC_VER
    ss << "MSVC " << _MSC_VER;
#elif defined(__GNUC__)
    ss << "GCC " << __GNUC__ << "." << __GNUC_MINOR__;
#elif defined(__clang__)
    ss << "Clang " << __clang_major__ << "." << __clang_minor__;
#else
    ss << "Unknown";
#endif
    ss << "\n";

    ss << "Platform: ";
#ifdef _WIN32
    ss << "Windows";
#elif defined(__linux__)
    ss << "Linux";
#elif defined(__APPLE__)
    ss << "macOS";
#else
    ss << "Unknown";
#endif
    ss << "\n";

    ss << "Architecture: ";
#ifdef _M_X64
    ss << "x64";
#elif defined(_M_IX86)
    ss << "x86";
#elif defined(__x86_64__)
    ss << "x86_64";
#elif defined(__i386__)
    ss << "i386";
#elif defined(__aarch64__)
    ss << "arm64";
#elif defined(__arm__)
    ss << "arm";
#else
    ss << "unknown";
#endif
    ss << "\n";

    ss << "CUDA Available: " << (CUDA_AVAILABLE ? "Yes" : "No") << "\n";
    ss << "Compression Available: " << (COMPRESSION_AVAILABLE ? "Yes" : "No") << "\n";
    ss << "Crypto Available: " << (CRYPTO_AVAILABLE ? "Yes" : "No");
    
    return ss.str();
}

std::vector<std::string> get_supported_devices() {
    std::vector<std::string> devices = {"CPU"};
    if (CUDA_AVAILABLE) {
        devices.push_back("CUDA");
    }
    devices.push_back("AUTO");
    return devices;
}

std::vector<std::string> get_supported_operators() {
    return {
        // Neural network operators
        "Linear", "ReLU", "GELU", "Softmax", "LayerNorm", "MatMul", "Add", "Mul",
        "Conv2D", "MaxPool2D", "BatchNorm", "Dropout", "Embedding", "Attention",
        
        // Machine learning algorithms
        "DecisionTree", "TreeEnsemble", "GradientBoosting", "SVM", "NaiveBayes",
        "KNN", "Clustering", "DBSCAN", "Decomposition",
        
        // Activation functions
        "Sigmoid", "Tanh", "LeakyReLU", "ELU", "Swish",
        
        // Normalization
        "GroupNorm", "InstanceNorm", "LocalResponseNorm",
        
        // Pooling
        "AvgPool2D", "GlobalAvgPool", "GlobalMaxPool", "AdaptiveAvgPool",
        
        // Convolution variants
        "Conv1D", "Conv3D", "DepthwiseConv2D", "TransposeConv2D",
        
        // Recurrent
        "LSTM", "GRU", "RNN",
        
        // Utility
        "Reshape", "Transpose", "Concat", "Split", "Slice", "Gather", "Scatter"
    };
}

void set_num_threads(int num_threads) {
    if (num_threads > 0 && num_threads <= static_cast<int>(std::thread::hardware_concurrency() * 2)) {
        g_num_threads = num_threads;
    }
}

int get_num_threads() {
    return g_num_threads;
}

void clear_cache() {
    // Clear any internal caches (model cache, operator cache, etc.)
    // In a real implementation, this would clear various caches
}

std::unordered_map<std::string, size_t> get_memory_usage() {
    std::unordered_map<std::string, size_t> usage;
    
    // In a real implementation, these would track actual memory usage
    usage["total_allocated"] = 0;
    usage["peak_usage"] = 0;
    usage["current_usage"] = 0;
    usage["model_cache"] = 0;
    usage["operator_cache"] = 0;
    usage["tensor_pool"] = 0;
    
    return usage;
}

} // namespace mle