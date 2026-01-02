
#pragma once

// --- STANDARD LIBRARY INCLUDES (PORTABLE) ---
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <queue>
#include <functional>
#include <memory>
#include <cstdint>
#include <unordered_map>

// --- NANOFLOW v0.7 CORE HEADER ---
// Cross-Platform Architecture: Windows (MSVC), Linux (GCC), macOS (Clang)

namespace nanoflow {

// --- HARDWARE BACKEND ENUM ---
// Allows the engine to switch compute strategies at runtime.
enum class BackendType {
    CPU,    // Universal (GGML Base)
    CUDA,   // NVIDIA GPUs (Windows/Linux)
    METAL   // Apple Silicon (macOS)
};

// --- 1. ABSTRACT FILE MAPPER (The "Virtual Disk") ---
// Hides OS-specific I/O details. 
// Windows uses CreateFile/MapViewOfFile. Linux/Mac uses open/mmap.
// The implementation (.cpp) will handle the #ifdefs.
class FileMapper {
public:
    FileMapper(const std::string& filepath);
    ~FileMapper();

    // Thread-safe read of a specific chunk from the virtual file address space.
    // Returns the number of bytes read.
    size_t read_chunk(uint64_t file_offset, size_t size, void* dest_buffer);

    // Returns the total size of the model file.
    uint64_t get_file_size() const;

private:
    std::string filepath_;
    uint64_t file_size_;

    // PIMPL idiom or void* to hide OS-specific handles (HANDLE vs int fd)
    // This ensures headers don't leak <windows.h> or <unistd.h>
    void* platform_handle_ = nullptr;
};

// --- 2. RING BUFFER (The "Hot Cache") ---
// Manages the strict 1GB RAM limit using RAII.
struct TileMetadata {
    uint32_t tile_id;
    size_t size_bytes;
    uint64_t lru_timestamp;
    bool is_ready;
};

class RingBuffer {
public:
    // Initialize the fixed-size buffer (Default: 1GB)
    RingBuffer(size_t capacity_mb = 1024);
    ~RingBuffer();

    // Reserves a slot in the buffer. 
    // If full, evicts the Least Recently Used (LRU) tile.
    // Returns a pointer to the memory slot.
    void* allocate_slot(uint32_t tile_id, size_t size);

    // Accessor for compute threads.
    void* get_data_ptr(uint32_t tile_id);

private:
    // The monolithic memory block
    std::vector<uint8_t> buffer_;
    size_t capacity_bytes_;
    size_t current_offset_ = 0;

    std::mutex mutex_;
    std::unordered_map<uint32_t, TileMetadata> metadata_map_;
};

// --- 3. DISK STREAMER (The "Async Worker") ---
// Handles the background prefetching logic.
class DiskStreamer {
public:
    DiskStreamer(std::shared_ptr<FileMapper> mapper, std::shared_ptr<RingBuffer> buffer);
    ~DiskStreamer();

    // Enqueues a tile to be fetched immediately.
    void request_tile(uint32_t tile_id, uint64_t file_offset, size_t size);

private:
    // The background worker loop
    void worker_loop();

    std::shared_ptr<FileMapper> mapper_;
    std::shared_ptr<RingBuffer> buffer_;

    // Threading primitives
    std::thread worker_thread_;
    std::atomic<bool> stop_flag_;
    std::mutex queue_mutex_;
    std::condition_variable cv_;
    
    struct Request {
        uint32_t tile_id;
        uint64_t file_offset;
        size_t size;
    };
    std::queue<Request> request_queue_;
};

// --- 4. SPARSE ENGINE (The "Coordinator") ---
// Orchestrates the pipeline: Predict -> Stream -> Compute
class SparseEngine {
public:
    SparseEngine(const std::string& model_path, BackendType backend = BackendType::CPU);
    ~SparseEngine();

    // Main entry point for Python
    // 1. Determines active tiles for the token.
    // 2. Streams them (if not cached).
    // 3. Performs compute.
    void generate_next_token(const std::vector<int>& input_ids);

private:
    std::shared_ptr<FileMapper> mapper_;
    std::shared_ptr<RingBuffer> ring_buffer_;
    std::unique_ptr<DiskStreamer> streamer_;
    BackendType backend_;
};

} // namespace nanoflow
