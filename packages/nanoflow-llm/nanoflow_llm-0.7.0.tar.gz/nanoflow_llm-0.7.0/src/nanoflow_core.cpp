
#include "nanoflow_core.h"
#include <iostream>
#include <stdexcept>
#include <cstring>
#include <algorithm>

// --- PLATFORM SPECIFIC INCLUDES ---
#ifdef _WIN32
    #include <windows.h>
#else
    #include <fcntl.h>
    #include <unistd.h>
    #include <sys/stat.h>
#endif

namespace nanoflow {

// ==========================================
// 1. FileMapper Implementation
// ==========================================

FileMapper::FileMapper(const std::string& filepath) : filepath_(filepath) {
#ifdef _WIN32
    // Windows Implementation
    HANDLE hFile = CreateFileA(
        filepath.c_str(),
        GENERIC_READ,
        FILE_SHARE_READ,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );
    
    if (hFile == INVALID_HANDLE_VALUE) {
        throw std::runtime_error("Failed to open file on Windows: " + filepath);
    }
    
    LARGE_INTEGER size;
    if (!GetFileSizeEx(hFile, &size)) {
        CloseHandle(hFile);
        throw std::runtime_error("Failed to get file size");
    }
    
    file_size_ = static_cast<uint64_t>(size.QuadPart);
    platform_handle_ = (void*)hFile;
    
#else
    // Linux/macOS Implementation
    int fd = open(filepath.c_str(), O_RDONLY);
    if (fd == -1) {
        throw std::runtime_error("Failed to open file: " + filepath);
    }
    
    struct stat sb;
    if (fstat(fd, &sb) == -1) {
        close(fd);
        throw std::runtime_error("Failed to get file size");
    }
    
    file_size_ = static_cast<uint64_t>(sb.st_size);
    // Store int fd in void* (safe on 64-bit where pointer >= 32-bit int)
    platform_handle_ = (void*)(intptr_t)fd; 
#endif
    std::cout << "[FileMapper] Opened: " << filepath << " (" << file_size_ / (1024*1024) << " MB)" << std::endl;
}

FileMapper::~FileMapper() {
#ifdef _WIN32
    if (platform_handle_) {
        CloseHandle((HANDLE)platform_handle_);
    }
#else
    if (platform_handle_) {
        close((int)(intptr_t)platform_handle_);
    }
#endif
}

size_t FileMapper::read_chunk(uint64_t file_offset, size_t size, void* dest_buffer) {
    if (file_offset + size > file_size_) {
        // Clamp read to end of file
        if (file_offset >= file_size_) return 0;
        size = file_size_ - file_offset;
    }

#ifdef _WIN32
    HANDLE hFile = (HANDLE)platform_handle_;
    OVERLAPPED ov = {0};
    ov.Offset = (DWORD)(file_offset & 0xFFFFFFFF);
    ov.OffsetHigh = (DWORD)(file_offset >> 32);
    
    DWORD bytesRead = 0;
    if (!ReadFile(hFile, dest_buffer, (DWORD)size, &bytesRead, &ov)) {
        return 0; // Error
    }
    return (size_t)bytesRead;
#else
    int fd = (int)(intptr_t)platform_handle_;
    // pread is thread-safe and doesn't change file offset
    ssize_t bytesRead = pread(fd, dest_buffer, size, file_offset);
    if (bytesRead < 0) return 0;
    return (size_t)bytesRead;
#endif
}

uint64_t FileMapper::get_file_size() const {
    return file_size_;
}

// ==========================================
// 2. RingBuffer Implementation
// ==========================================

RingBuffer::RingBuffer(size_t capacity_mb) {
    capacity_bytes_ = capacity_mb * 1024 * 1024;
    buffer_.resize(capacity_bytes_);
    std::cout << "[RingBuffer] Allocated " << capacity_mb << " MB RAM." << std::endl;
}

RingBuffer::~RingBuffer() {}

void* RingBuffer::allocate_slot(uint32_t tile_id, size_t size) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    // Naive Ring Strategy for v0.7 Prototype:
    // Just append. If full, wrap around. 
    // Real implementation needs intelligent LRU.
    
    if (current_offset_ + size > capacity_bytes_) {
        current_offset_ = 0; // Wrap around (Evict oldest implicitly by overwriting)
    }
    
    void* ptr = buffer_.data() + current_offset_;
    
    // Register metadata
    metadata_map_[tile_id] = {tile_id, size, 0, false};
    
    current_offset_ += size;
    return ptr;
}

void* RingBuffer::get_data_ptr(uint32_t tile_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    // Note: To fully implement this, we need to store the offset in TileMetadata.
    // For this prototype, we rely on the Streamer having the pointer from allocate_slot.
    return nullptr; 
}

// ==========================================
// 3. DiskStreamer Implementation
// ==========================================

DiskStreamer::DiskStreamer(std::shared_ptr<FileMapper> mapper, std::shared_ptr<RingBuffer> buffer)
    : mapper_(mapper), buffer_(buffer), stop_flag_(false) {
    
    // Start background thread
    worker_thread_ = std::thread(&DiskStreamer::worker_loop, this);
}

DiskStreamer::~DiskStreamer() {
    stop_flag_ = true;
    cv_.notify_all();
    if (worker_thread_.joinable()) {
        worker_thread_.join();
    }
}

void DiskStreamer::request_tile(uint32_t tile_id, uint64_t file_offset, size_t size) {
    {
        std::lock_guard<std::mutex> lock(queue_mutex_);
        request_queue_.push({tile_id, file_offset, size});
    }
    cv_.notify_one();
}

void DiskStreamer::worker_loop() {
    while (!stop_flag_) {
        Request req;
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            cv_.wait(lock, [this] { return stop_flag_ || !request_queue_.empty(); });
            
            if (stop_flag_ && request_queue_.empty()) return;
            
            req = request_queue_.front();
            request_queue_.pop();
        }
        
        // 1. Allocate RAM
        void* dest = buffer_->allocate_slot(req.tile_id, req.size);
        
        // 2. Read from Disk (Block here, but main thread keeps running)
        size_t bytes = mapper_->read_chunk(req.file_offset, req.size, dest);
        
        // 3. Mark as Ready (Logic to be added in metadata update)
    }
}

// ==========================================
// 4. SparseEngine Implementation
// ==========================================

SparseEngine::SparseEngine(const std::string& model_path, BackendType backend) 
    : backend_(backend) {
    
    mapper_ = std::make_shared<FileMapper>(model_path);
    ring_buffer_ = std::make_shared<RingBuffer>(1024); // 1GB limit
    streamer_ = std::make_unique<DiskStreamer>(mapper_, ring_buffer_);
    
    std::cout << "[SparseEngine] Initialized with backend: " << (int)backend << std::endl;
}

SparseEngine::~SparseEngine() {}

void SparseEngine::generate_next_token(const std::vector<int>& input_ids) {
    // 1. Predict (Mock: assume we need tile 0)
    uint32_t next_tile = 0; 
    
    // 2. Prefetch (Mock: Offset 0, size 1MB)
    streamer_->request_tile(next_tile, 0, 1024 * 1024);
    
    // 3. Compute (Placeholder)
    // std::cout << "[Engine] Computing token..." << std::endl;
}

} // namespace nanoflow
