#pragma once

/**
 * Advanced Tensor Fusion Engine for MLE Runtime
 * Research Contribution: Dynamic Operator Fusion with Memory-Aware Scheduling
 * 
 * Novel Features:
 * 1. Dynamic operator fusion based on memory access patterns
 * 2. SIMD-optimized kernels with auto-vectorization
 * 3. Cache-aware memory layout optimization
 * 4. Predictive prefetching for sequential operations
 */

#include <vector>
#include <memory>
#include <unordered_map>
#include <immintrin.h>  // AVX/SSE intrinsics
#include <thread>
#include <future>

namespace mle {

// Research Innovation: Memory-Aligned Tensor with Cache-Friendly Layout
class AlignedTensor {
public:
    static constexpr size_t CACHE_LINE_SIZE = 64;
    static constexpr size_t SIMD_ALIGNMENT = 32;  // AVX2 alignment
    
    // Default constructor
    AlignedTensor();
    AlignedTensor(const std::vector<size_t>& shape);
    ~AlignedTensor();
    
    // Copy constructor and assignment operator
    AlignedTensor(const AlignedTensor& other);
    AlignedTensor& operator=(const AlignedTensor& other);
    
    // Move constructor and assignment operator
    AlignedTensor(AlignedTensor&& other) noexcept;
    AlignedTensor& operator=(AlignedTensor&& other) noexcept;
    
    // Memory-aligned data access
    float* data() { return aligned_data_; }
    const float* data() const { return aligned_data_; }
    
    // Cache-friendly strided access
    float& operator()(const std::vector<size_t>& indices);
    const float& operator()(const std::vector<size_t>& indices) const;
    
    // SIMD-friendly batch operations
    void vectorized_add(const AlignedTensor& other);
    void vectorized_mul(const AlignedTensor& other);
    void vectorized_relu();
    
    size_t size() const { return total_size_; }
    const std::vector<size_t>& shape() const { return shape_; }
    
private:
    std::vector<size_t> shape_;
    std::vector<size_t> strides_;
    float* aligned_data_;
    size_t total_size_;
    
    void compute_strides();
    void allocate_aligned_memory();
};

// Research Innovation: Operator Fusion Graph
class FusionNode {
public:
    enum class OpType {
        LINEAR, RELU, GELU, SOFTMAX, LAYERNORM, MATMUL,
        CONV2D, BATCHNORM, DROPOUT, ATTENTION,
        // ML-specific operators
        DECISION_TREE, RANDOM_FOREST, SVM, NAIVE_BAYES
    };
    
    OpType type;
    std::vector<std::shared_ptr<FusionNode>> inputs;
    std::vector<std::shared_ptr<FusionNode>> outputs;
    std::unordered_map<std::string, AlignedTensor> weights;
    std::unordered_map<std::string, float> params;
    
    // Fusion compatibility analysis
    bool can_fuse_with(const FusionNode& other) const;
    float fusion_benefit_score(const FusionNode& other) const;
};

// Research Innovation: Dynamic Fusion Optimizer
class FusionOptimizer {
public:
    struct FusionPattern {
        std::vector<FusionNode::OpType> pattern;
        std::string kernel_name;
        float performance_gain;
    };
    
    FusionOptimizer();
    
    // Analyze computation graph and identify fusion opportunities
    std::vector<FusionPattern> analyze_fusion_opportunities(
        const std::vector<std::shared_ptr<FusionNode>>& graph);
    
    // Apply fusion transformations
    std::vector<std::shared_ptr<FusionNode>> apply_fusions(
        const std::vector<std::shared_ptr<FusionNode>>& graph,
        const std::vector<FusionPattern>& patterns);
    
private:
    std::vector<FusionPattern> known_patterns_;
    
    void initialize_fusion_patterns();
    bool matches_pattern(const std::vector<std::shared_ptr<FusionNode>>& subgraph,
                        const FusionPattern& pattern) const;
};

// Research Innovation: SIMD-Optimized Kernel Library
class SIMDKernels {
public:
    // AVX2-optimized matrix multiplication
    static void avx2_gemm(const float* A, const float* B, float* C,
                         size_t M, size_t N, size_t K);
    
    // Vectorized activation functions
    static void avx2_relu(const float* input, float* output, size_t size);
    static void avx2_gelu(const float* input, float* output, size_t size);
    static void avx2_softmax(const float* input, float* output, size_t size);
    
    // Fused operations
    static void avx2_linear_relu(const float* input, const float* weight,
                                const float* bias, float* output,
                                size_t batch_size, size_t input_size, size_t output_size);
    
    // ML-specific kernels
    static void avx2_decision_tree_predict(const float* features,
                                          const float* tree_data,
                                          float* predictions,
                                          size_t n_samples, size_t n_features);
    
    // CPU capability detection (now public)
    static bool cpu_supports_avx2();
    static bool cpu_supports_fma();
};

// Research Innovation: Memory-Aware Scheduler
class MemoryAwareScheduler {
public:
    struct MemoryProfile {
        size_t l1_cache_size = 32 * 1024;      // 32KB
        size_t l2_cache_size = 256 * 1024;     // 256KB
        size_t l3_cache_size = 8 * 1024 * 1024; // 8MB
        size_t memory_bandwidth = 50ULL * 1024 * 1024 * 1024; // 50GB/s
    };
    
    MemoryAwareScheduler(const MemoryProfile& profile = MemoryProfile{});
    
    // Schedule operations to minimize cache misses
    std::vector<std::shared_ptr<FusionNode>> schedule_operations(
        const std::vector<std::shared_ptr<FusionNode>>& graph);
    
    // Predict memory access patterns
    size_t estimate_cache_misses(const std::vector<std::shared_ptr<FusionNode>>& schedule);
    
private:
    MemoryProfile memory_profile_;
    
    float calculate_reuse_distance(const FusionNode& op1, const FusionNode& op2);
    bool fits_in_cache(size_t data_size, size_t cache_level) const;
};

// Research Innovation: Predictive Prefetcher
class PredictivePrefetcher {
public:
    PredictivePrefetcher();
    
    // Learn access patterns during execution
    void record_access(void* address, size_t size);
    
    // Predict next memory accesses
    std::vector<void*> predict_next_accesses();
    
    // Prefetch data into cache
    void prefetch_data(void* address, size_t size);
    
private:
    struct AccessPattern {
        void* base_address;
        size_t stride;
        size_t count;
        double confidence;
    };
    
    std::vector<AccessPattern> learned_patterns_;
    std::vector<void*> recent_accesses_;
    
    void update_patterns();
    void prefetch_cache_line(void* address);
};

// Main Tensor Fusion Engine
class TensorFusionEngine {
public:
    TensorFusionEngine();
    ~TensorFusionEngine();
    
    // Load and optimize computation graph
    void load_graph(const std::vector<std::shared_ptr<FusionNode>>& nodes);
    
    // Execute optimized graph
    std::vector<AlignedTensor> execute(const std::vector<AlignedTensor>& inputs);
    
    // Performance monitoring
    struct PerformanceMetrics {
        double execution_time_ms;
        size_t cache_misses;
        size_t simd_operations;
        double memory_bandwidth_utilization;
        size_t fused_operations;
    };
    
    PerformanceMetrics get_performance_metrics() const;
    
    // Research feature: Adaptive optimization
    void enable_adaptive_optimization(bool enable = true);
    
private:
    std::vector<std::shared_ptr<FusionNode>> optimized_graph_;
    std::unique_ptr<FusionOptimizer> fusion_optimizer_;
    std::unique_ptr<MemoryAwareScheduler> scheduler_;
    std::unique_ptr<PredictivePrefetcher> prefetcher_;
    
    PerformanceMetrics metrics_;
    bool adaptive_optimization_enabled_;
    
    void optimize_graph();
    void execute_node(const std::shared_ptr<FusionNode>& node,
                     std::unordered_map<FusionNode*, AlignedTensor>& tensor_cache);
};

} // namespace mle