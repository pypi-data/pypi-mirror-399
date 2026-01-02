
#pragma once
#include <vector>
#include <string>
#include <unordered_map>
#include <queue>
#include <future>
#include <cstdint>
#include <mutex>
#include <memory>

// --- NANOFLOW v0.7: SPARSE STREAMING CORE ---
// Target: 256B Parameters on 1GB RAM via NVMe Streaming

// Basic unit of data: A compressed matrix block (e.g., 512x512 4-bit weights)
struct TileID {
    uint32_t layer_id;
    uint32_t expert_id; // For MoE (Mixture of Experts)
    uint32_t tile_idx;

    bool operator==(const TileID& other) const {
        return layer_id == other.layer_id && 
               expert_id == other.expert_id && 
               tile_idx == other.tile_idx;
    }
};

// Metadata for a tile residing in the Ring Buffer
struct HotTile {
    void* data_ptr;       // Direct pointer to data in the 1GB Ring Buffer
    size_t size_bytes;
    bool is_ready;        // Atomic flag: True when Async I/O completes write
    uint64_t lru_timestamp; // For eviction policies
};

// --- 1. TILE PREDICTOR (The "Brain") ---
// Responsible for looking ahead in the token generation stream.
// In a dense model, this is linear. In MoE, this predicts active experts.
class TilePredictor {
public:
    virtual ~TilePredictor() = default;

    // Predicts which tiles are needed for the next 'N' tokens.
    // Input: Current activation/token context.
    virtual std::vector<TileID> predict_next_batch(const std::vector<float>& current_activations) = 0;
};

// --- 2. DISK STREAMER (The "Infinite Disk" Manager) ---
// Manages the NVMe I/O and the strict 1GB RAM Ring Buffer.
class DiskStreamer {
public:
    // Initializes the 1GB Ring Buffer and opens the model file(s) for overlapping I/O.
    DiskStreamer(const std::string& model_path, size_t ram_limit_mb = 1024);
    ~DiskStreamer();

    // ASYNC PREFETCH: The Core "P2P" Logic.
    // Submits read requests to the NVMe SSD for tiles that *will* be needed.
    // These are written directly into the Ring Buffer.
    void prefetch_tiles(const std::vector<TileID>& tiles);

    // PAGE FAULT MECHANISM:
    // Returns a pointer to the tile data. 
    // If the data is prefetching, it waits (spin-lock). 
    // If not requested, it triggers an emergency blocking read.
    HotTile get_tile(const TileID& id);

    // Cleans up tiles that are past the context window to free Ring Buffer slots.
    void evict_stale_tiles(uint32_t current_layer_idx);

private:
    // The Monolithic 1GB Buffer
    void* ring_buffer_base_;
    size_t buffer_capacity_;
    size_t write_head_offset_; // Circular buffer pointer

    // Maps a logical TileID to its physical location in the Ring Buffer
    std::unordered_map<uint64_t, HotTile> buffer_map_;
    std::mutex map_mutex_;

    // I/O Worker internals
    std::queue<TileID> io_queue_;
    std::future<void> io_worker_;
    bool stop_worker_;
};

// --- 3. SPARSE ENGINE (The Coordinator) ---
// The main entry point that drives the Compute <-> Streamer loop.
class SparseEngine {
public:
    SparseEngine(const std::string& model_path);
    ~SparseEngine();

    // The main inference loop.
    // 1. Predicts next tiles.
    // 2. Prefetches them via Streamer.
    // 3. Computes current tiles (Tile-based Matrix Mul).
    void generate(const std::string& prompt);

private:
    std::unique_ptr<DiskStreamer> streamer_;
    std::unique_ptr<TilePredictor> predictor_;

    // Internal state
    int context_window_pos_ = 0;
    
    // ON-THE-FLY DEQUANTIZATION & COMPUTE
    // Decodes 4-bit tile -> Float32 in L1 Cache -> Computes MatMul
    void compute_tile(const HotTile& weight_tile, const std::vector<float>& input_vec, std::vector<float>& output_vec);
};
