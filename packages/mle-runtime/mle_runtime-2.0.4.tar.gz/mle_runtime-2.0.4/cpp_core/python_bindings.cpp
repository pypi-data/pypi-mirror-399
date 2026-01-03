/**
 * Advanced Python Bindings for MLE Runtime C++ Core
 * Research Innovation: Intelligent Fallback System with Performance Monitoring
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "include/engine.hpp"
#include "include/loader.hpp"
#include "include/device.hpp"
#include "include/tensor_fusion_engine.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_mle_core, m) {
    m.doc() = "MLE Runtime C++ Core - Research-Grade High-Performance ML Inference Engine v2.0.4";
    
    // Research Innovation: Device enumeration with hybrid support
    py::enum_<mle::Device>(m, "Device")
        .value("CPU", mle::Device::CPU)
        .value("CUDA", mle::Device::CUDA)
        .value("AUTO", mle::Device::AUTO)
        .value("HYBRID", mle::Device::HYBRID)
        .export_values();
    
    // Research Innovation: Advanced benchmark results
    py::class_<mle::Engine::BenchmarkResult>(m, "BenchmarkResult")
        .def_readonly("mean_time_ms", &mle::Engine::BenchmarkResult::mean_time_ms)
        .def_readonly("std_time_ms", &mle::Engine::BenchmarkResult::std_time_ms)
        .def_readonly("min_time_ms", &mle::Engine::BenchmarkResult::min_time_ms)
        .def_readonly("max_time_ms", &mle::Engine::BenchmarkResult::max_time_ms)
        .def_readonly("throughput_ops_per_sec", &mle::Engine::BenchmarkResult::throughput_ops_per_sec)
        .def_readonly("memory_peak_mb", &mle::Engine::BenchmarkResult::memory_peak_mb)
        .def_readonly("cpu_utilization", &mle::Engine::BenchmarkResult::cpu_utilization)
        .def_readonly("gpu_utilization", &mle::Engine::BenchmarkResult::gpu_utilization);
    
    // Research Innovation: Runtime metrics for monitoring
    py::class_<mle::Engine::RuntimeMetrics>(m, "RuntimeMetrics")
        .def_readonly("current_latency_ms", &mle::Engine::RuntimeMetrics::current_latency_ms)
        .def_readonly("average_latency_ms", &mle::Engine::RuntimeMetrics::average_latency_ms)
        .def_readonly("current_memory_mb", &mle::Engine::RuntimeMetrics::current_memory_mb)
        .def_readonly("cpu_usage_percent", &mle::Engine::RuntimeMetrics::cpu_usage_percent)
        .def_readonly("gpu_usage_percent", &mle::Engine::RuntimeMetrics::gpu_usage_percent)
        .def_readonly("total_inferences", &mle::Engine::RuntimeMetrics::total_inferences)
        .def_readonly("cache_hit_rate", &mle::Engine::RuntimeMetrics::cache_hit_rate)
        .def_readonly("bottleneck_operator", &mle::Engine::RuntimeMetrics::bottleneck_operator);
    
    // Research Innovation: Advanced Engine class with adaptive features
    py::class_<mle::Engine>(m, "Engine")
        .def(py::init<mle::Device>(), "Initialize engine with device")
        .def("load_model", &mle::Engine::load_model, 
             "Load MLE model from file path",
             py::arg("path"))
        .def("run", &mle::Engine::run,
             "Run inference on input arrays",
             py::arg("inputs"))
        .def("get_device", &mle::Engine::get_device,
             "Get current device")
        .def("is_model_loaded", &mle::Engine::is_model_loaded,
             "Check if model is loaded")
        .def("get_model_info", &mle::Engine::get_model_info,
             "Get model information")
        .def("benchmark", &mle::Engine::benchmark,
             "Benchmark model performance with advanced metrics",
             py::arg("inputs"), py::arg("num_runs") = 100)
        
        // Research Innovation: Adaptive optimization methods
        .def("enable_adaptive_optimization", &mle::Engine::enable_adaptive_optimization,
             "Enable adaptive optimization that learns and improves performance",
             py::arg("enable") = true)
        .def("set_performance_target", &mle::Engine::set_performance_target,
             "Set target latency for adaptive optimization",
             py::arg("target_latency_ms"))
        .def("enable_dynamic_quantization", &mle::Engine::enable_dynamic_quantization,
             "Enable dynamic quantization for memory optimization",
             py::arg("enable") = true)
        .def("set_memory_budget", &mle::Engine::set_memory_budget,
             "Set memory budget for optimization decisions",
             py::arg("budget_mb"))
        
        // Research Innovation: Real-time monitoring
        .def("get_runtime_metrics", &mle::Engine::get_runtime_metrics,
             "Get real-time performance metrics")
        .def("get_operator_names", &mle::Engine::get_operator_names,
             "Get list of operator names in the model")
        .def("get_operator_timings", &mle::Engine::get_operator_timings,
             "Get timing information for each operator")
        .def("suggest_optimizations", &mle::Engine::suggest_optimizations,
             "Get AI-powered optimization suggestions");
    
    // Research Innovation: Tensor Fusion Engine
    py::class_<mle::TensorFusionEngine>(m, "TensorFusionEngine")
        .def(py::init<>())
        .def("enable_adaptive_optimization", &mle::TensorFusionEngine::enable_adaptive_optimization,
             "Enable adaptive optimization for fusion engine",
             py::arg("enable") = true)
        .def("get_performance_metrics", &mle::TensorFusionEngine::get_performance_metrics,
             "Get fusion engine performance metrics");
    
    // Research Innovation: Performance metrics for fusion engine
    py::class_<mle::TensorFusionEngine::PerformanceMetrics>(m, "FusionPerformanceMetrics")
        .def_readonly("execution_time_ms", &mle::TensorFusionEngine::PerformanceMetrics::execution_time_ms)
        .def_readonly("cache_misses", &mle::TensorFusionEngine::PerformanceMetrics::cache_misses)
        .def_readonly("simd_operations", &mle::TensorFusionEngine::PerformanceMetrics::simd_operations)
        .def_readonly("memory_bandwidth_utilization", &mle::TensorFusionEngine::PerformanceMetrics::memory_bandwidth_utilization)
        .def_readonly("fused_operations", &mle::TensorFusionEngine::PerformanceMetrics::fused_operations);
    
    // Loader utilities
    py::class_<mle::ModelLoader>(m, "ModelLoader")
        .def_static("validate_file", &mle::ModelLoader::validate_file,
                   "Validate MLE file format",
                   py::arg("path"))
        .def_static("get_file_info", &mle::ModelLoader::get_file_info,
                   "Get file information",
                   py::arg("path"))
        .def_static("inspect_model", &mle::ModelLoader::inspect_model,
                   "Inspect model details",
                   py::arg("path"));
    
    // Research Innovation: Advanced compression utilities
    m.def("compress_data", [](py::bytes data, uint32_t compression_type) {
        std::string input = data;
        auto result = mle::compress_data(
            reinterpret_cast<const uint8_t*>(input.data()), 
            input.size(), 
            compression_type
        );
        return py::bytes(reinterpret_cast<const char*>(result.data()), result.size());
    }, "Compress data using advanced algorithms",
       py::arg("data"), py::arg("compression_type"));
    
    m.def("decompress_data", [](py::bytes data, uint32_t compression_type, size_t uncompressed_size) {
        std::string input = data;
        auto result = mle::decompress_data(
            reinterpret_cast<const uint8_t*>(input.data()), 
            input.size(), 
            compression_type,
            uncompressed_size
        );
        return py::bytes(reinterpret_cast<const char*>(result.data()), result.size());
    }, "Decompress data using advanced algorithms",
       py::arg("data"), py::arg("compression_type"), py::arg("uncompressed_size"));
    
    // Research Innovation: System information and optimization
    py::class_<mle::performance::SystemInfo>(m, "SystemInfo")
        .def_readonly("cpu_name", &mle::performance::SystemInfo::cpu_name)
        .def_readonly("cpu_cores", &mle::performance::SystemInfo::cpu_cores)
        .def_readonly("cpu_threads", &mle::performance::SystemInfo::cpu_threads)
        .def_readonly("total_memory_gb", &mle::performance::SystemInfo::total_memory_gb)
        .def_readonly("avx2_support", &mle::performance::SystemInfo::avx2_support)
        .def_readonly("avx512_support", &mle::performance::SystemInfo::avx512_support)
        .def_readonly("cuda_available", &mle::performance::SystemInfo::cuda_available)
        .def_readonly("cuda_version", &mle::performance::SystemInfo::cuda_version)
        .def_readonly("cuda_devices", &mle::performance::SystemInfo::cuda_devices);
    
    // Performance utilities
    m.def("set_num_threads", &mle::set_num_threads, 
          "Set number of threads for CPU operations",
          py::arg("num_threads"));
    m.def("get_num_threads", &mle::get_num_threads, 
          "Get current number of threads");
    m.def("get_optimal_thread_count", &mle::performance::get_optimal_thread_count,
          "Get optimal thread count for current system");
    m.def("get_system_info", &mle::performance::get_system_info,
          "Get comprehensive system information");
    
    // Memory management
    m.def("clear_cache", &mle::clear_cache, "Clear internal caches");
    m.def("get_memory_usage", &mle::get_memory_usage, "Get memory usage statistics");
    
    // Version information
    m.def("get_version", &mle::get_version, "Get C++ core version");
    m.def("get_build_info", &mle::get_build_info, "Get build information");
    m.def("get_supported_devices", &mle::get_supported_devices, "Get supported devices");
    m.def("get_supported_operators", &mle::get_supported_operators, "Get supported operators");
    
    // Research Innovation: Advanced error handling
    py::register_exception<mle::MLEException>(m, "MLEException");
    py::register_exception<mle::LoaderException>(m, "LoaderException");
    py::register_exception<mle::EngineException>(m, "EngineException");
    py::register_exception<mle::OptimizationException>(m, "OptimizationException");
    
    // Research Innovation: Performance profiling
    m.def("enable_performance_profiling", &mle::performance::enable_performance_profiling,
          "Enable detailed performance profiling",
          py::arg("enable") = true);
    m.def("set_cache_size_hint", &mle::performance::set_cache_size_hint,
          "Set cache size hints for optimization",
          py::arg("l1_kb"), py::arg("l2_kb"), py::arg("l3_kb"));
    
    // Constants
    m.attr("VERSION") = mle::VERSION;
    m.attr("BUILD_DATE") = mle::BUILD_DATE;
    m.attr("CUDA_AVAILABLE") = mle::CUDA_AVAILABLE;
    m.attr("COMPRESSION_AVAILABLE") = mle::COMPRESSION_AVAILABLE;
    m.attr("CRYPTO_AVAILABLE") = mle::CRYPTO_AVAILABLE;
    m.attr("RESEARCH_FEATURES_ENABLED") = true;
    m.attr("TENSOR_FUSION_AVAILABLE") = true;
    m.attr("ADAPTIVE_OPTIMIZATION_AVAILABLE") = true;
}