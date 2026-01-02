
#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <cstdint>
#include <future>
#include <mutex>
#include <queue>
#include <memory>

// --- NANOFLOW v0.7 CORE DEFINITIONS ---

// A 'Tile' is the atomic unit of streaming (e.g., a 1024x1024 weight block).
struct TileMetadata {
    uint32_t layer_id;
    uint32_t tile_id;
    uint64_t file_offset;   // Byte offset in the .safetensors file
    uint64_t size_bytes;    // Compressed/Quantized size on disk
    bool is_quantized;      // True if stored in 4-bit
};

// --- COMPONENT 1: The Virtual File Mapper ---
// Handles raw disk I/O without OS-level caching interfering with our Ring Buffer.
class VirtualMapper {
public:
    VirtualMapper(const std::string& filepath);
    ~VirtualMapper();

    // Reads a specific byte range directly into our allocated Hot Buffer
    // Returns bytes read.
    size_t read_chunk(uint64_t offset, size_t size, void* dest_buffer);

private:
    std::string filepath_;
    // File descriptor or handle (OS specific implementation hidden)
    int fd_;
};

// --- COMPONENT 2: Ring Buffer / LRU Cache ---
// Manages the hard 1GB RAM limit. Handles allocation and eviction.
class RingBufferManager {
public:
    RingBufferManager(size_t capacity_mb = 1024);
    ~RingBufferManager();

    // Requests a memory block for an incoming tile.
    // If full, triggers eviction of LRU tiles.
    void* allocate_slot(size_t size);

    // Marks a slot as 'recently used' to protect it from immediate eviction
    void touch(void* ptr);

private:
    size_t capacity_bytes_;
    size_t current_usage_;
    void* base_pointer_; // The monolithic 1GB block
    
    std::mutex mutex_;
};

// --- COMPONENT 3: Async Streamer (The "Spotify" Logic) ---
// Runs in a background thread, fetching tiles ahead of the compute engine.
class AsyncStreamer {
public:
    AsyncStreamer(VirtualMapper& mapper, RingBufferManager& cache);
    
    // The "Predictor" calls this to queue up data for Token N+1
    void prefetch_tile(const TileMetadata& tile);

    // The Compute Engine calls this to get the data (blocks if not ready)
    void* get_tile_data(uint32_t tile_id);

private:
    VirtualMapper& mapper_;
    RingBufferManager& cache_;
    
    // Queue for tiles to be fetched
    std::queue<TileMetadata> fetch_queue_;
    
    // Maps TileID -> Memory Address (if loaded)
    std::unordered_map<uint32_t, void*> resident_tiles_;
    
    // Background worker control
    std::future<void> io_thread_;
    bool stop_signal_ = false;
    
    void worker_loop();
};

// --- MASTER CLASS: Sparse NanoFlow Engine ---
class SparseNanoFlow {
public:
    SparseNanoFlow(const std::string& model_path, int ram_limit_mb = 1024);
    ~SparseNanoFlow();

    // 1. Predict: Which experts/tiles do we need for the next token?
    std::vector<uint32_t> predict_active_tiles(const std::vector<int>& input_ids);

    // 2. Stream: Ensure those tiles are in RAM (or arriving)
    void prepare_tiles(const std::vector<uint32_t>& tile_ids);

    // 3. Compute: Execute only on the active tiles
    void forward(const std::vector<int>& input_ids);

private:
    std::unique_ptr<VirtualMapper> mapper_;
    std::unique_ptr<RingBufferManager> buffer_;
    std::unique_ptr<AsyncStreamer> streamer_;
};
