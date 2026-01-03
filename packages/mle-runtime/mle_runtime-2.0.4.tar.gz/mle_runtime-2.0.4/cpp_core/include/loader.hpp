#pragma once

/**
 * Advanced Model Loader for MLE Runtime
 * Research Innovation: Intelligent Model Loading with Format Detection
 */

#include <string>
#include <vector>
#include <unordered_map>
#include <fstream>
#include <cstdint>

namespace mle {

// Research Innovation: Enhanced MLE File Format
struct MLEHeader {
    uint32_t magic;                    // Magic number: 0x00454C4D ("MLE\0")
    uint32_t version;                  // Format version
    uint32_t feature_flags;            // Feature flags
    uint32_t header_size;              // Header size in bytes
    uint64_t metadata_offset;          // Metadata section offset
    uint64_t metadata_size;            // Metadata section size
    uint64_t graph_offset;             // Graph definition offset
    uint64_t graph_size;               // Graph definition size
    uint64_t weights_offset;           // Weights data offset
    uint64_t weights_size;             // Weights data size
    uint64_t signature_offset;         // Digital signature offset
    uint64_t signature_size;           // Digital signature size
    uint32_t metadata_checksum;        // Metadata CRC32
    uint32_t graph_checksum;           // Graph CRC32
    uint32_t weights_checksum;         // Weights CRC32
    uint32_t header_checksum;          // Header CRC32
    uint32_t min_reader_version;       // Minimum reader version
    uint32_t writer_version;           // Writer version
};

// Research Innovation: Advanced Model Loader
class ModelLoader {
public:
    // File validation and inspection
    static bool validate_file(const std::string& path);
    static std::unordered_map<std::string, std::string> get_file_info(const std::string& path);
    static std::unordered_map<std::string, std::string> inspect_model(const std::string& path);
    
    // Header operations
    static MLEHeader read_header(std::ifstream& file);
    static bool validate_header(const MLEHeader& header);
    
    // Section readers
    static std::string read_metadata(std::ifstream& file, const MLEHeader& header);
    static std::vector<uint8_t> read_graph(std::ifstream& file, const MLEHeader& header);
    static std::vector<uint8_t> read_weights(std::ifstream& file, const MLEHeader& header);
    static std::vector<uint8_t> read_signature(std::ifstream& file, const MLEHeader& header);
    
    // Research Innovation: Intelligent format detection
    static std::string detect_model_format(const std::string& path);
    static bool is_mle_format(const std::string& path);
    static bool is_legacy_format(const std::string& path);
    
    // Compression and security
    static std::vector<uint8_t> decompress_section(const std::vector<uint8_t>& data, 
                                                   uint32_t compression_type);
    static bool verify_checksum(const std::vector<uint8_t>& data, uint32_t expected_checksum);
    
private:
    static constexpr uint32_t MLE_MAGIC = 0x00454C4D;
    static constexpr uint32_t MIN_SUPPORTED_VERSION = 1;
    static constexpr uint32_t MAX_SUPPORTED_VERSION = 2;
    
    static uint32_t calculate_crc32(const std::vector<uint8_t>& data);
    static bool validate_magic_number(uint32_t magic);
    static bool validate_version(uint32_t version);
};

// Research Innovation: Compression utilities
std::vector<uint8_t> compress_data(const uint8_t* data, size_t size, uint32_t compression_type);
std::vector<uint8_t> decompress_data(const uint8_t* data, size_t size, 
                                    uint32_t compression_type, size_t uncompressed_size);

// Research Innovation: Global utility functions
std::string get_version();
std::string get_build_info();
std::vector<std::string> get_supported_devices();
std::vector<std::string> get_supported_operators();

void set_num_threads(int num_threads);
int get_num_threads();
void clear_cache();
std::unordered_map<std::string, size_t> get_memory_usage();

// Research Innovation: Constants
extern const std::string VERSION;
extern const std::string BUILD_DATE;
extern const bool CUDA_AVAILABLE;
extern const bool COMPRESSION_AVAILABLE;
extern const bool CRYPTO_AVAILABLE;

} // namespace mle