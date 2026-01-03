#include "device.hpp"
#include "engine.hpp"
#include <iostream>
#include <thread>
#include <chrono>
#include <algorithm>

#ifdef _WIN32
#include <windows.h>
#include <pdh.h>
#include <intrin.h>
#pragma comment(lib, "pdh.lib")
#else
#include <unistd.h>
#include <sys/sysinfo.h>
#include <cpuid.h>
#endif

namespace mle {

// DeviceManager Implementation
DeviceManager& DeviceManager::instance() {
    static DeviceManager instance;
    return instance;
}

void DeviceManager::initialize_devices() {
    // Initialize device states for available devices
    device_states_.resize(4); // CPU, CUDA, AUTO, HYBRID
    
    std::cout << "✅ Device manager initialized" << std::endl;
}

std::vector<DeviceInfo> DeviceManager::get_available_devices() {
    std::vector<DeviceInfo> devices;
    
    // CPU device (always available)
    DeviceInfo cpu_info;
    cpu_info.name = "CPU";
    cpu_info.type = "CPU";
    cpu_info.memory_mb = 8192; // Placeholder
    cpu_info.compute_units = std::thread::hardware_concurrency();
    cpu_info.supports_fp16 = false;
    cpu_info.supports_int8 = true;
    cpu_info.peak_flops = 100.0; // Placeholder
    cpu_info.memory_bandwidth_gbps = 50.0; // Placeholder
    cpu_info.driver_version = "N/A";
    devices.push_back(cpu_info);
    
    // CUDA device (if available)
    if (device_utils::is_cuda_available()) {
        DeviceInfo cuda_info;
        cuda_info.name = "CUDA";
        cuda_info.type = "CUDA";
        cuda_info.memory_mb = 4096; // Placeholder
        cuda_info.compute_units = 2048; // Placeholder
        cuda_info.supports_fp16 = true;
        cuda_info.supports_int8 = true;
        cuda_info.peak_flops = 1000.0; // Placeholder
        cuda_info.memory_bandwidth_gbps = 500.0; // Placeholder
        cuda_info.driver_version = device_utils::get_cuda_version();
        devices.push_back(cuda_info);
    }
    
    return devices;
}

DeviceInfo DeviceManager::get_device_info(Device device) {
    auto devices = get_available_devices();
    
    switch (device) {
        case Device::CPU:
            return devices.empty() ? DeviceInfo{} : devices[0];
        case Device::CUDA:
            return devices.size() > 1 ? devices[1] : DeviceInfo{};
        default:
            return DeviceInfo{};
    }
}

Device DeviceManager::get_optimal_device(size_t workload_size, const std::string& workload_type) {
    if (adaptive_selection_enabled_) {
        return select_device_by_heuristics(workload_size, workload_type);
    }
    
    // Simple heuristic: use GPU for large workloads if available
    if (workload_size > 10000 && device_utils::is_cuda_available()) {
        return Device::CUDA;
    }
    
    return Device::CPU;
}

Device DeviceManager::get_least_loaded_device() {
    Device best_device = Device::CPU;
    double min_load = 1.0;
    
    for (size_t i = 0; i < device_states_.size(); ++i) {
        if (device_states_[i].current_load < min_load) {
            min_load = device_states_[i].current_load;
            best_device = static_cast<Device>(i);
        }
    }
    
    return best_device;
}

void DeviceManager::update_device_load(Device device, double load_factor) {
    size_t idx = static_cast<size_t>(device);
    if (idx < device_states_.size()) {
        device_states_[idx].current_load = load_factor;
        device_states_[idx].last_update_time = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now().time_since_epoch()).count();
    }
}

double DeviceManager::get_device_utilization(Device device) {
    size_t idx = static_cast<size_t>(device);
    if (idx < device_states_.size()) {
        return device_states_[idx].utilization;
    }
    return 0.0;
}

size_t DeviceManager::get_device_memory_usage(Device device) {
    size_t idx = static_cast<size_t>(device);
    if (idx < device_states_.size()) {
        return device_states_[idx].memory_used;
    }
    return 0;
}

void DeviceManager::enable_adaptive_selection(bool enable) {
    adaptive_selection_enabled_ = enable;
}

void DeviceManager::set_performance_target(double target_latency_ms) {
    performance_target_ms_ = target_latency_ms;
}

void DeviceManager::update_device_states() {
    // Update device utilization and memory usage
    // This would query actual system metrics in a real implementation
}

Device DeviceManager::select_device_by_heuristics(size_t workload_size, const std::string& workload_type) {
    // Intelligent device selection based on workload characteristics
    if (workload_type == "inference" && workload_size > 50000) {
        return Device::CUDA;
    } else if (workload_type == "training") {
        return Device::CUDA;
    } else {
        return Device::CPU;
    }
}

// Device utilities implementation
namespace device_utils {

bool is_cpu_device(Device device) {
    return device == Device::CPU;
}

bool is_gpu_device(Device device) {
    return device == Device::CUDA;
}

bool supports_simd(Device device) {
    return device == Device::CPU && has_avx2_support();
}

bool supports_tensor_cores(Device device) {
    return device == Device::CUDA; // Simplified
}

int get_cpu_core_count() {
    return std::thread::hardware_concurrency();
}

bool has_avx2_support() {
#ifdef _WIN32
    int cpuInfo[4];
    __cpuid(cpuInfo, 7);
    return (cpuInfo[1] & (1 << 5)) != 0; // AVX2 bit
#else
    return false; // Simplified for non-Windows
#endif
}

bool has_avx512_support() {
#ifdef _WIN32
    int cpuInfo[4];
    __cpuid(cpuInfo, 7);
    return (cpuInfo[1] & (1 << 16)) != 0; // AVX512F bit
#else
    return false; // Simplified for non-Windows
#endif
}

size_t get_l3_cache_size() {
    return 8 * 1024 * 1024; // 8MB placeholder
}

bool is_cuda_available() {
#ifdef ENABLE_CUDA
    return true;
#else
    return false;
#endif
}

int get_cuda_device_count() {
#ifdef ENABLE_CUDA
    // Would query CUDA runtime
    return 1;
#else
    return 0;
#endif
}

std::string get_cuda_version() {
#ifdef ENABLE_CUDA
    return "11.8"; // Placeholder
#else
    return "N/A";
#endif
}

size_t get_gpu_memory_total(int device_id) {
#ifdef ENABLE_CUDA
    // Would query CUDA memory info
    return 8192; // 8GB placeholder
#else
    return 0;
#endif
}

size_t get_gpu_memory_free(int device_id) {
#ifdef ENABLE_CUDA
    // Would query CUDA memory info
    return 6144; // 6GB placeholder
#else
    return 0;
#endif
}

} // namespace device_utils

} // namespace mle