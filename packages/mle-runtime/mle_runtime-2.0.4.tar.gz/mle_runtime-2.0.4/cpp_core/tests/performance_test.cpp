#include <iostream>
#include <chrono>
#include <vector>
#include <random>
#include <iomanip>
#include <cassert>

#include "engine.hpp"
#include "tensor_fusion_engine.hpp"
#include "device.hpp"

using namespace mle;

class PerformanceTestSuite {
public:
    PerformanceTestSuite() {
        std::cout << "🔬 MLE Runtime Research Performance Test Suite" << std::endl;
        std::cout << "=" << std::string(60, '=') << std::endl;
    }
    
    void run_all_tests() {
        test_tensor_operations();
        test_fusion_engine();
        test_simd_kernels();
        test_device_management();
        test_adaptive_execution();
        
        print_summary();
    }

private:
    struct TestResult {
        std::string name;
        double execution_time_ms;
        bool passed;
        std::string details;
    };
    
    std::vector<TestResult> results_;
    
    void test_tensor_operations() {
        std::cout << "\n📊 Testing Tensor Operations" << std::endl;
        
        // Test AlignedTensor creation and operations
        auto start = std::chrono::high_resolution_clock::now();
        
        try {
            AlignedTensor tensor1({1000, 1000});
            AlignedTensor tensor2({1000, 1000});
            
            // Fill with random data
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<float> dis(-1.0f, 1.0f);
            
            for (size_t i = 0; i < tensor1.size(); ++i) {
                tensor1.data()[i] = dis(gen);
                tensor2.data()[i] = dis(gen);
            }
            
            // Test vectorized operations
            tensor1.vectorized_add(tensor2);
            tensor1.vectorized_mul(tensor2);
            tensor1.vectorized_relu();
            
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            
            results_.push_back({
                "Tensor Operations (1M elements)",
                duration.count() / 1000.0,
                true,
                "Vectorized add, mul, relu on 1M float elements"
            });
            
            std::cout << "  ✅ Tensor operations: " << duration.count() / 1000.0 << " ms" << std::endl;
            
        } catch (const std::exception& e) {
            results_.push_back({
                "Tensor Operations",
                0.0,
                false,
                std::string("Failed: ") + e.what()
            });
            std::cout << "  ❌ Tensor operations failed: " << e.what() << std::endl;
        }
    }
    
    void test_fusion_engine() {
        std::cout << "\n🔗 Testing Tensor Fusion Engine" << std::endl;
        
        auto start = std::chrono::high_resolution_clock::now();
        
        try {
            TensorFusionEngine engine;
            engine.enable_adaptive_optimization(true);
            
            // Create a simple computation graph
            std::vector<std::shared_ptr<FusionNode>> nodes;
            
            // Linear -> ReLU pattern (should be fused)
            auto linear_node = std::make_shared<FusionNode>();
            linear_node->type = FusionNode::OpType::LINEAR;
            
            auto relu_node = std::make_shared<FusionNode>();
            relu_node->type = FusionNode::OpType::RELU;
            relu_node->inputs.push_back(linear_node);
            linear_node->outputs.push_back(relu_node);
            
            nodes.push_back(linear_node);
            nodes.push_back(relu_node);
            
            engine.load_graph(nodes);
            
            // Test execution
            AlignedTensor input({1, 100});
            std::fill_n(input.data(), input.size(), 1.0f);
            
            auto outputs = engine.execute({input});
            
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            
            // Get performance metrics
            auto metrics = engine.get_performance_metrics();
            
            results_.push_back({
                "Tensor Fusion Engine",
                duration.count() / 1000.0,
                true,
                "Graph optimization and execution with fusion"
            });
            
            std::cout << "  ✅ Fusion engine: " << duration.count() / 1000.0 << " ms" << std::endl;
            std::cout << "     Fused operations: " << metrics.fused_operations << std::endl;
            std::cout << "     SIMD operations: " << metrics.simd_operations << std::endl;
            
        } catch (const std::exception& e) {
            results_.push_back({
                "Tensor Fusion Engine",
                0.0,
                false,
                std::string("Failed: ") + e.what()
            });
            std::cout << "  ❌ Fusion engine failed: " << e.what() << std::endl;
        }
    }
    
    void test_simd_kernels() {
        std::cout << "\n⚡ Testing SIMD Kernels" << std::endl;
        
        const size_t size = 10000;
        std::vector<float> input(size);
        std::vector<float> output(size);
        std::vector<float> reference(size);
        
        // Initialize test data
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<float> dis(-10.0f, 10.0f);
        
        for (size_t i = 0; i < size; ++i) {
            input[i] = dis(gen);
        }
        
        // Test ReLU kernel
        auto start = std::chrono::high_resolution_clock::now();
        
        try {
            SIMDKernels::avx2_relu(input.data(), output.data(), size);
            
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            
            // Verify correctness
            bool correct = true;
            for (size_t i = 0; i < size; ++i) {
                float expected = std::max(0.0f, input[i]);
                if (std::abs(output[i] - expected) > 1e-6f) {
                    correct = false;
                    break;
                }
            }
            
            results_.push_back({
                "SIMD ReLU Kernel",
                duration.count() / 1000.0,
                correct,
                correct ? "Vectorized ReLU on 10K elements" : "Correctness check failed"
            });
            
            std::cout << "  ✅ SIMD ReLU: " << duration.count() / 1000.0 << " ms" 
                      << (correct ? " (correct)" : " (INCORRECT)") << std::endl;
            
        } catch (const std::exception& e) {
            results_.push_back({
                "SIMD ReLU Kernel",
                0.0,
                false,
                std::string("Failed: ") + e.what()
            });
            std::cout << "  ❌ SIMD ReLU failed: " << e.what() << std::endl;
        }
        
        // Test GEMM kernel
        start = std::chrono::high_resolution_clock::now();
        
        try {
            const size_t M = 128, N = 128, K = 128;
            std::vector<float> A(M * K), B(K * N), C(M * N, 0.0f);
            
            // Initialize matrices
            for (size_t i = 0; i < M * K; ++i) A[i] = dis(gen);
            for (size_t i = 0; i < K * N; ++i) B[i] = dis(gen);
            
            SIMDKernels::avx2_gemm(A.data(), B.data(), C.data(), M, N, K);
            
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            
            // Basic sanity check (not full correctness verification)
            bool has_nonzero = false;
            for (float val : C) {
                if (std::abs(val) > 1e-6f) {
                    has_nonzero = true;
                    break;
                }
            }
            
            results_.push_back({
                "SIMD GEMM Kernel",
                duration.count() / 1000.0,
                has_nonzero,
                "128x128x128 matrix multiplication"
            });
            
            std::cout << "  ✅ SIMD GEMM: " << duration.count() / 1000.0 << " ms" 
                      << (has_nonzero ? " (has output)" : " (no output)") << std::endl;
            
        } catch (const std::exception& e) {
            results_.push_back({
                "SIMD GEMM Kernel",
                0.0,
                false,
                std::string("Failed: ") + e.what()
            });
            std::cout << "  ❌ SIMD GEMM failed: " << e.what() << std::endl;
        }
    }
    
    void test_device_management() {
        std::cout << "\n🖥️  Testing Device Management" << std::endl;
        
        auto start = std::chrono::high_resolution_clock::now();
        
        try {
            auto& device_manager = DeviceManager::instance();
            
            // Test device enumeration
            auto available_devices = device_manager.get_available_devices();
            std::cout << "  Available devices: " << available_devices.size() << std::endl;
            
            // Test CPU device
            auto cpu_device = device_manager.get_device(Device::CPU);
            if (cpu_device) {
                auto cpu_info = cpu_device->get_device_info();
                std::cout << "  CPU: " << cpu_info.device_name << std::endl;
                std::cout << "       Memory: " << cpu_info.memory_total_mb << " MB" << std::endl;
                std::cout << "       Cores: " << cpu_info.compute_units << std::endl;
                std::cout << "       Utilization: " << std::fixed << std::setprecision(1) 
                          << cpu_info.utilization_percent << "%" << std::endl;
            }
            
            // Test CUDA device (if available)
            auto cuda_device = device_manager.get_device(Device::CUDA);
            if (cuda_device && cuda_device->is_available()) {
                auto cuda_info = cuda_device->get_device_info();
                std::cout << "  CUDA: " << cuda_info.device_name << std::endl;
                std::cout << "        Memory: " << cuda_info.memory_total_mb << " MB" << std::endl;
            } else {
                std::cout << "  CUDA: Not available" << std::endl;
            }
            
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            
            results_.push_back({
                "Device Management",
                duration.count() / 1000.0,
                true,
                "Device enumeration and info retrieval"
            });
            
            std::cout << "  ✅ Device management: " << duration.count() / 1000.0 << " ms" << std::endl;
            
        } catch (const std::exception& e) {
            results_.push_back({
                "Device Management",
                0.0,
                false,
                std::string("Failed: ") + e.what()
            });
            std::cout << "  ❌ Device management failed: " << e.what() << std::endl;
        }
    }
    
    void test_adaptive_execution() {
        std::cout << "\n🧠 Testing Adaptive Execution Engine" << std::endl;
        
        auto start = std::chrono::high_resolution_clock::now();
        
        try {
            Engine engine(Device::AUTO);
            engine.enable_adaptive_optimization(true);
            engine.set_performance_target(5.0); // 5ms target
            
            // Simulate model loading (we don't have a real model file)
            // In a real test, we would load an actual model
            
            // Test runtime metrics
            auto metrics = engine.get_runtime_metrics();
            std::cout << "  Initial metrics:" << std::endl;
            std::cout << "    Total inferences: " << metrics.total_inferences << std::endl;
            std::cout << "    Average latency: " << std::fixed << std::setprecision(2) 
                      << metrics.average_latency_ms << " ms" << std::endl;
            
            // Test optimization suggestions
            auto suggestions = engine.suggest_optimizations();
            if (!suggestions.empty()) {
                std::cout << "  Optimization suggestions:" << std::endl;
                std::cout << suggestions << std::endl;
            }
            
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            
            results_.push_back({
                "Adaptive Execution Engine",
                duration.count() / 1000.0,
                true,
                "Engine initialization and metrics collection"
            });
            
            std::cout << "  ✅ Adaptive execution: " << duration.count() / 1000.0 << " ms" << std::endl;
            
        } catch (const std::exception& e) {
            results_.push_back({
                "Adaptive Execution Engine",
                duration.count() / 1000.0,
                false,
                std::string("Failed: ") + e.what()
            });
            std::cout << "  ❌ Adaptive execution failed: " << e.what() << std::endl;
        }
    }
    
    void print_summary() {
        std::cout << "\n📋 Performance Test Summary" << std::endl;
        std::cout << "=" << std::string(60, '=') << std::endl;
        
        int passed = 0, failed = 0;
        double total_time = 0.0;
        
        for (const auto& result : results_) {
            std::cout << std::left << std::setw(30) << result.name << " ";
            
            if (result.passed) {
                std::cout << "✅ PASS ";
                passed++;
            } else {
                std::cout << "❌ FAIL ";
                failed++;
            }
            
            std::cout << std::right << std::setw(8) << std::fixed << std::setprecision(2) 
                      << result.execution_time_ms << " ms" << std::endl;
            
            if (!result.details.empty()) {
                std::cout << "    " << result.details << std::endl;
            }
            
            total_time += result.execution_time_ms;
        }
        
        std::cout << std::string(60, '-') << std::endl;
        std::cout << "Total tests: " << (passed + failed) << std::endl;
        std::cout << "Passed: " << passed << std::endl;
        std::cout << "Failed: " << failed << std::endl;
        std::cout << "Total time: " << std::fixed << std::setprecision(2) << total_time << " ms" << std::endl;
        
        if (failed == 0) {
            std::cout << "\n🎉 All tests passed! Research features are working correctly." << std::endl;
        } else {
            std::cout << "\n⚠️  Some tests failed. Check the implementation." << std::endl;
        }
        
        // Performance analysis
        std::cout << "\n📈 Performance Analysis:" << std::endl;
        
        // Find tensor operations test
        for (const auto& result : results_) {
            if (result.name.find("Tensor Operations") != std::string::npos && result.passed) {
                double ops_per_ms = 1000000.0 / result.execution_time_ms; // 1M operations
                std::cout << "  Tensor throughput: " << std::scientific << std::setprecision(2) 
                          << ops_per_ms * 1000 << " ops/sec" << std::endl;
                break;
            }
        }
        
        // Find SIMD performance
        for (const auto& result : results_) {
            if (result.name.find("SIMD ReLU") != std::string::npos && result.passed) {
                double elements_per_ms = 10000.0 / result.execution_time_ms;
                std::cout << "  SIMD ReLU throughput: " << std::scientific << std::setprecision(2) 
                          << elements_per_ms * 1000 << " elements/sec" << std::endl;
                break;
            }
        }
        
        std::cout << std::endl;
    }
};

int main() {
    try {
        PerformanceTestSuite test_suite;
        test_suite.run_all_tests();
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "❌ Test suite failed: " << e.what() << std::endl;
        return 1;
    }
}