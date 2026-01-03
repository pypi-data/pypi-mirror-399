#pragma once

/**
 * Advanced MLE Runtime Engine with Research Innovations
 * 
 * Research Contributions:
 * 1. Adaptive Execution Engine with Dynamic Optimization
 * 2. Hybrid CPU-GPU Scheduling with Load Balancing
 * 3. Memory-Efficient Model Representation
 * 4. Real-time Performance Monitoring and Adaptation
 */

#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include <cstdint>
#include <atomic>
#include <mutex>
#include "tensor_fusion_engine.hpp"

namespace mle {

enum class Device {
    CPU = 0,
    CUDA = 1,
    AUTO = 2,
    HYBRID = 3  // Research Innovation: Hybrid CPU-GPU execution
};

enum class OperatorType : uint32_t {
    // Neural Network Operators
    LINEAR = 1,
    RELU = 2,
    GELU = 3,
    SOFTMAX = 4,
    LAYERNORM = 5,
    MATMUL = 6,
    ADD = 7,
    MUL = 8,
    CONV2D = 9,
    MAXPOOL2D = 10,
    BATCHNORM = 11,
    DROPOUT = 12,
    EMBEDDING = 13,
    ATTENTION = 14,
    
    // Classical ML Operators
    DECISION_TREE = 26,
    TREE_ENSEMBLE = 27,
    GRADIENT_BOOSTING = 28,
    SVM = 29,
    NAIVE_BAYES = 30,
    KNN = 31,
    CLUSTERING = 32,
    DBSCAN = 33,
    DECOMPOSITION = 34,
    
    // Research Innovation: Advanced Operators
    ADAPTIVE_POOLING = 35,
    DYNAMIC_CONV = 36,
    LEARNED_ACTIVATION = 37,
    SPARSE_ATTENTION = 38,
    QUANTIZED_LINEAR = 39
};

// Research Innovation: Advanced Tensor with Memory Optimization
struct Tensor {
    std::vector<float> data;
    std::vector<size_t> shape;
    bool is_quantized = false;
    float quantization_scale = 1.0f;
    int8_t quantization_zero_point = 0;
    
    Tensor() = default;
    Tensor(const std::vector<float>& data, const std::vector<size_t>& shape);
    
    size_t size() const;
    size_t ndim() const;
    size_t memory_footprint() const;
    
    float* data_ptr() { return data.data(); }
    const float* data_ptr() const { return data.data(); }
    
    // Research Innovation: Dynamic quantization
    void quantize_int8();
    void dequantize();
    
    // Memory optimization
    void optimize_memory_layout();
    bool is_memory_aligned() const;
};

// Research Innovation: Adaptive Operator with Performance Learning
struct Operator {
    OperatorType type;
    std::unordered_map<std::string, Tensor> weights;
    std::unordered_map<std::string, float> params;
    std::unordered_map<std::string, std::string> attributes;
    
    // Performance tracking
    mutable std::atomic<uint64_t> execution_count{0};
    mutable std::atomic<uint64_t> total_execution_time_us{0};
    mutable std::mutex performance_mutex;
    
    virtual ~Operator() = default;
    virtual Tensor forward(const Tensor& input) = 0;
    
    // Research Innovation: Adaptive execution
    virtual bool should_use_gpu(const Tensor& input) const;
    virtual void update_performance_stats(uint64_t execution_time_us) const;
    double get_average_execution_time() const;
};

// Research Innovation: Intelligent Model Graph with Auto-Optimization
class ModelGraph {
public:
    void add_operator(std::unique_ptr<Operator> op);
    std::vector<Tensor> execute(const std::vector<Tensor>& inputs);
    
    size_t get_operator_count() const { return operators_.size(); }
    
    // Research Innovation: Graph optimization
    void optimize_graph();
    void enable_dynamic_optimization(bool enable = true);
    
    // Performance analysis
    struct GraphMetrics {
        double total_execution_time_ms;
        size_t memory_usage_bytes;
        double cpu_utilization;
        double gpu_utilization;
        size_t cache_hit_rate;
    };
    
    GraphMetrics get_performance_metrics() const;
    
    // Public method for bottleneck analysis
    void analyze_bottlenecks();
    
private:
    std::vector<std::unique_ptr<Operator>> operators_;
    std::unique_ptr<TensorFusionEngine> fusion_engine_;
    bool dynamic_optimization_enabled_ = false;
    mutable GraphMetrics cached_metrics_;
    
    void apply_graph_transformations();
};

// Research Innovation: Advanced Engine with Adaptive Execution
class Engine {
public:
    explicit Engine(Device device);
    ~Engine();
    
    void load_model(const std::string& path);
    std::vector<std::vector<float>> run(const std::vector<std::vector<float>>& inputs);
    
    Device get_device() const;
    bool is_model_loaded() const;
    std::string get_model_info() const;
    
    struct BenchmarkResult {
        double mean_time_ms;
        double std_time_ms;
        double min_time_ms;
        double max_time_ms;
        double throughput_ops_per_sec;
        size_t memory_peak_mb;
        double cpu_utilization;
        double gpu_utilization;
    };
    
    BenchmarkResult benchmark(const std::vector<std::vector<float>>& inputs, int num_runs = 100);
    
    // Research Innovation: Adaptive execution features
    void enable_adaptive_optimization(bool enable = true);
    void set_performance_target(double target_latency_ms);
    void enable_dynamic_quantization(bool enable = true);
    void set_memory_budget(size_t budget_mb);
    
    // Research Innovation: Real-time monitoring
    struct RuntimeMetrics {
        double current_latency_ms;
        double average_latency_ms;
        size_t current_memory_mb;
        double cpu_usage_percent;
        double gpu_usage_percent;
        size_t total_inferences;
        double cache_hit_rate;
        std::string bottleneck_operator;
    };
    
    RuntimeMetrics get_runtime_metrics() const;
    
    // Research Innovation: Model introspection
    std::vector<std::string> get_operator_names() const;
    std::unordered_map<std::string, double> get_operator_timings() const;
    std::string suggest_optimizations() const;
    
    // Research Innovation: Dynamic model modification
    bool can_modify_model() const;
    void replace_operator(const std::string& name, std::unique_ptr<Operator> new_op);
    void add_profiling_hooks();

private:
    Device device_;
    bool model_loaded_;
    std::string model_path_;
    std::unique_ptr<ModelGraph> graph_;
    std::unordered_map<std::string, std::string> metadata_;
    
    // Research Innovation: Adaptive execution state
    bool adaptive_optimization_enabled_;
    double performance_target_ms_;
    bool dynamic_quantization_enabled_;
    size_t memory_budget_mb_;
    
    // Performance monitoring
    mutable RuntimeMetrics runtime_metrics_;
    mutable std::mutex metrics_mutex_;
    
    // Research Innovation: Execution strategies
    enum class ExecutionStrategy {
        CPU_ONLY,
        GPU_ONLY,
        HYBRID_PARALLEL,
        ADAPTIVE_SWITCHING
    };
    
    ExecutionStrategy current_strategy_;
    std::unique_ptr<TensorFusionEngine> fusion_engine_;
    
    void parse_mle_file(const std::string& path);
    void parse_graph_and_weights(const std::vector<uint8_t>& graph_data, 
                                const std::vector<uint8_t>& weights_data,
                                const std::unordered_map<std::string, std::string>& metadata);
    std::vector<Tensor> convert_inputs(const std::vector<std::vector<float>>& inputs);
    std::vector<std::vector<float>> convert_outputs(const std::vector<Tensor>& outputs);
    
    // Research Innovation: Adaptive execution methods
    void update_execution_strategy();
    void optimize_for_latency();
    void optimize_for_throughput();
    void optimize_for_memory();
    
    ExecutionStrategy select_optimal_strategy(const std::vector<Tensor>& inputs);
    void monitor_performance();
    void apply_runtime_optimizations();
};

// Research Innovation: Exception hierarchy for better error handling
class MLEException : public std::exception {
public:
    explicit MLEException(const std::string& message) : message_(message) {}
    const char* what() const noexcept override { return message_.c_str(); }
private:
    std::string message_;
};

class LoaderException : public MLEException {
public:
    explicit LoaderException(const std::string& message) : MLEException("Loader Error: " + message) {}
};

class EngineException : public MLEException {
public:
    explicit EngineException(const std::string& message) : MLEException("Engine Error: " + message) {}
};

class OptimizationException : public MLEException {
public:
    explicit OptimizationException(const std::string& message) : MLEException("Optimization Error: " + message) {}
};

// Research Innovation: Global performance utilities
namespace performance {
    void set_global_thread_count(int threads);
    int get_optimal_thread_count();
    void enable_performance_profiling(bool enable = true);
    void set_cache_size_hint(size_t l1_kb, size_t l2_kb, size_t l3_kb);
    
    struct SystemInfo {
        std::string cpu_name;
        int cpu_cores;
        int cpu_threads;
        size_t total_memory_gb;
        bool avx2_support;
        bool avx512_support;
        bool cuda_available;
        std::string cuda_version;
        int cuda_devices;
    };
    
    SystemInfo get_system_info();
}

} // namespace mle