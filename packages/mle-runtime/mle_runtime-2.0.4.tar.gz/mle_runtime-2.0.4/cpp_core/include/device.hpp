#pragma once

/**
 * Device Management for MLE Runtime
 * Research Innovation: Intelligent Device Selection and Load Balancing
 */

#include <string>
#include <vector>
#include <memory>

namespace mle {

// Forward declarations
enum class Device;

// Research Innovation: Device Information
struct DeviceInfo {
    std::string name;
    std::string type;  // "CPU", "CUDA", "OpenCL", etc.
    size_t memory_mb;
    int compute_units;
    bool supports_fp16;
    bool supports_int8;
    double peak_flops;
    double memory_bandwidth_gbps;
    std::string driver_version;
};

// Research Innovation: Device Manager
class DeviceManager {
public:
    static DeviceManager& instance();
    
    // Device discovery and management
    std::vector<DeviceInfo> get_available_devices();
    DeviceInfo get_device_info(Device device);
    Device get_optimal_device(size_t workload_size, const std::string& workload_type = "general");
    
    // Load balancing
    Device get_least_loaded_device();
    void update_device_load(Device device, double load_factor);
    
    // Performance monitoring
    double get_device_utilization(Device device);
    size_t get_device_memory_usage(Device device);
    
    // Research Innovation: Adaptive device selection
    void enable_adaptive_selection(bool enable = true);
    void set_performance_target(double target_latency_ms);
    
private:
    DeviceManager() = default;
    
    struct DeviceState {
        double current_load = 0.0;
        double utilization = 0.0;
        size_t memory_used = 0;
        uint64_t last_update_time = 0;
    };
    
    std::vector<DeviceState> device_states_;
    bool adaptive_selection_enabled_ = false;
    double performance_target_ms_ = 10.0;
    
    void initialize_devices();
    void update_device_states();
    Device select_device_by_heuristics(size_t workload_size, const std::string& workload_type);
};

// Research Innovation: Device-specific optimizations
namespace device_utils {
    bool is_cpu_device(Device device);
    bool is_gpu_device(Device device);
    bool supports_simd(Device device);
    bool supports_tensor_cores(Device device);
    
    // CPU-specific utilities
    int get_cpu_core_count();
    bool has_avx2_support();
    bool has_avx512_support();
    size_t get_l3_cache_size();
    
    // GPU-specific utilities
    bool is_cuda_available();
    int get_cuda_device_count();
    std::string get_cuda_version();
    size_t get_gpu_memory_total(int device_id = 0);
    size_t get_gpu_memory_free(int device_id = 0);
}

} // namespace mle