cmake_minimum_required(VERSION 3.22)
project(mle_core VERSION 2.0.4 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Research Innovation: Advanced build options
option(ENABLE_CUDA "Enable CUDA support" OFF)
option(BUILD_TESTS "Build tests" ON)
option(ENABLE_COMPRESSION "Enable compression support" ON)
option(ENABLE_CRYPTO "Enable cryptographic features" OFF)
option(BUILD_PYTHON_BINDINGS "Build Python bindings" ON)
option(ENABLE_RESEARCH_FEATURES "Enable research features" ON)
option(ENABLE_TENSOR_FUSION "Enable tensor fusion engine" ON)
option(ENABLE_SIMD_OPTIMIZATIONS "Enable SIMD optimizations" ON)

# Find Python and pybind11 for mandatory bindings
if(BUILD_PYTHON_BINDINGS)
    find_package(Python COMPONENTS Interpreter Development REQUIRED)
    
    # Use pybind11 from pip installation
    execute_process(
        COMMAND ${Python_EXECUTABLE} -c "import pybind11; print(pybind11.get_cmake_dir())"
        OUTPUT_VARIABLE pybind11_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE pybind11_RESULT
    )
    
    if(pybind11_RESULT EQUAL 0)
        find_package(pybind11 REQUIRED PATHS ${pybind11_DIR})
        message(STATUS "Found pybind11: ${pybind11_DIR}")
    else()
        message(FATAL_ERROR "pybind11 not found. Install with: pip install pybind11")
    endif()
endif()

# Research Innovation: Core library with advanced features
add_library(mle_core STATIC
    src/loader.cpp
    src/engine.cpp
    src/tensor_fusion_engine.cpp
    src/utils.cpp
    src/device.cpp
    src/ops_cpu.cpp
    src/security.cpp
    src/executor.cpp
)

target_include_directories(mle_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Research Innovation: Advanced compiler optimizations
target_compile_options(mle_core PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4 /O2 /arch:AVX2>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -O3 -march=native -mavx2 -mfma>
)

# Research Innovation: Conditional SIMD optimizations
if(ENABLE_SIMD_OPTIMIZATIONS)
    target_compile_definitions(mle_core PRIVATE ENABLE_SIMD_OPTIMIZATIONS)
    
    if(MSVC)
        target_compile_options(mle_core PRIVATE /arch:AVX2)
    else()
        target_compile_options(mle_core PRIVATE -mavx2 -mfma)
    endif()
    
    message(STATUS "SIMD optimizations enabled (AVX2/FMA)")
endif()

# Research Innovation: Tensor fusion engine
if(ENABLE_TENSOR_FUSION)
    target_compile_definitions(mle_core PRIVATE ENABLE_TENSOR_FUSION)
    message(STATUS "Tensor fusion engine enabled")
endif()

# Research Innovation: Research features
if(ENABLE_RESEARCH_FEATURES)
    target_compile_definitions(mle_core PRIVATE ENABLE_RESEARCH_FEATURES)
    message(STATUS "Research features enabled")
endif()

# Compression support
if(ENABLE_COMPRESSION)
    find_package(ZLIB QUIET)
    if(ZLIB_FOUND)
        target_link_libraries(mle_core PRIVATE ZLIB::ZLIB)
        target_compile_definitions(mle_core PRIVATE ENABLE_COMPRESSION)
        message(STATUS "Compression support enabled")
    else()
        message(WARNING "ZLIB not found - compression disabled")
    endif()
endif()

# Cryptographic support
if(ENABLE_CRYPTO)
    find_package(OpenSSL QUIET)
    if(OpenSSL_FOUND)
        target_link_libraries(mle_core PRIVATE OpenSSL::SSL OpenSSL::Crypto)
        target_compile_definitions(mle_core PRIVATE ENABLE_CRYPTO)
        message(STATUS "Cryptographic support enabled")
    else()
        message(WARNING "OpenSSL not found - crypto disabled")
    endif()
endif()

# CUDA support
if(ENABLE_CUDA)
    enable_language(CUDA)
    find_package(CUDAToolkit QUIET)
    
    if(CUDAToolkit_FOUND)
        target_sources(mle_core PRIVATE
            src/ops_cuda.cu
            src/cuda_context.cpp
        )
        
        target_link_libraries(mle_core PUBLIC
            CUDA::cudart
            CUDA::cublas
        )
        
        target_compile_definitions(mle_core PUBLIC ENABLE_CUDA)
        
        set_target_properties(mle_core PROPERTIES
            CUDA_SEPARABLE_COMPILATION ON
            CUDA_ARCHITECTURES "75;80;86;89"
        )
        
        message(STATUS "CUDA support enabled")
    else()
        message(WARNING "CUDA not found - GPU acceleration disabled")
    endif()
endif()

# Research Innovation: Performance tests
if(BUILD_TESTS)
    enable_testing()
    
    # Performance benchmark test
    add_executable(performance_test
        tests/performance_test.cpp
    )
    
    target_link_libraries(performance_test PRIVATE mle_core)
    add_test(NAME performance_test COMMAND performance_test)
    
    message(STATUS "Tests enabled")
endif()

# Research Innovation: Python bindings with advanced features
if(BUILD_PYTHON_BINDINGS)
    pybind11_add_module(_mle_core python_bindings.cpp)
    
    target_link_libraries(_mle_core PRIVATE mle_core)
    
    # Set properties for Python module
    target_compile_definitions(_mle_core PRIVATE 
        VERSION_INFO=${PROJECT_VERSION}
        RESEARCH_BUILD=1
    )
    
    # Research Innovation: Enable all features in Python bindings
    if(ENABLE_RESEARCH_FEATURES)
        target_compile_definitions(_mle_core PRIVATE ENABLE_RESEARCH_FEATURES)
    endif()
    
    if(ENABLE_TENSOR_FUSION)
        target_compile_definitions(_mle_core PRIVATE ENABLE_TENSOR_FUSION)
    endif()
    
    # Ensure the module can find the core library
    if(WIN32)
        set_target_properties(_mle_core PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/Release
        )
    else()
        set_target_properties(_mle_core PROPERTIES
            LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        )
    endif()
    
    # Install Python module
    install(TARGETS _mle_core DESTINATION .)
    
    message(STATUS "Python bindings enabled with research features")
endif()

# Install
install(TARGETS mle_core
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)

install(DIRECTORY include/
    DESTINATION include/mle
)

# Research Innovation: Build summary
message(STATUS "")
message(STATUS "=== MLE Runtime Research Build Configuration ===")
message(STATUS "Version: ${PROJECT_VERSION}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "")
message(STATUS "Features:")
message(STATUS "  Research Features: ${ENABLE_RESEARCH_FEATURES}")
message(STATUS "  Tensor Fusion: ${ENABLE_TENSOR_FUSION}")
message(STATUS "  SIMD Optimizations: ${ENABLE_SIMD_OPTIMIZATIONS}")
message(STATUS "  CUDA Support: ${ENABLE_CUDA}")
message(STATUS "  Compression: ${ENABLE_COMPRESSION}")
message(STATUS "  Cryptography: ${ENABLE_CRYPTO}")
message(STATUS "  Python Bindings: ${BUILD_PYTHON_BINDINGS}")
message(STATUS "  Tests: ${BUILD_TESTS}")
message(STATUS "")
message(STATUS "Compiler: ${CMAKE_CXX_COMPILER_ID}")
message(STATUS "Compiler Version: ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "================================================")
message(STATUS "")