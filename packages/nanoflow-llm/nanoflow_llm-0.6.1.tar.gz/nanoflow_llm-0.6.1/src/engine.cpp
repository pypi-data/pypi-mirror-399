
#include "engine.h"
#include <iostream>

NanoFlowEngine::NanoFlowEngine() {
    // Initialize GGML context to hold tensor metadata (structs), not data.
    // ENABLE ZERO-COPY: Set no_alloc = true so GGML doesn't allocate data buffers.
    struct ggml_init_params params = {
        .mem_size   = 16 * 1024 * 1024, // 16 MB metadata buffer
        .mem_buffer = NULL,
        .no_alloc   = true, // <--- CHANGED: We manage data memory externally (Python)
    };
    ctx = ggml_init(params);
}

NanoFlowEngine::~NanoFlowEngine() {
    if (ctx) ggml_free(ctx);
}

void NanoFlowEngine::set_weights(const std::string& name, uintptr_t raw_pointer, 
                                 int rows, int cols, int ggml_type_id) {
    if (raw_pointer == 0) {
        std::cerr << "[Error] Null pointer provided for tensor: " << name << std::endl;
        return;
    }

    // Create a tensor description in GGML (metadata only)
    // Note: GGML usually expects (cols, rows) for 2D creation
    struct ggml_tensor* t = ggml_new_tensor_2d(ctx, (ggml_type)ggml_type_id, cols, rows);

    // ZERO-COPY MAGIC: Point the tensor's data to the external memory (Python's RAM)
    t->data = (void*)raw_pointer;
    
    ggml_set_name(t, name.c_str());
    tensors[name] = t;

    std::cout << "[C++ Backend] Registered '" << name << "' "
              << "Shape:(" << rows << "x" << cols << ") "
              << "Ptr:" << (void*)raw_pointer << std::endl;
}

void NanoFlowEngine::compute(const std::string& tensor_name) {
    if (tensors.find(tensor_name) == tensors.end()) {
        std::cerr << "[Error] Tensor not found: " << tensor_name << std::endl;
        return;
    }
    
    struct ggml_tensor* t = tensors[tensor_name];
    
    // Demonstration: Read the first value to prove we have access to the memory
    // Assuming float (GGML_TYPE_F32 = 0) for this simple check
    float* data = (float*)t->data;
    std::cout << "[C++ Compute] Accessing '" << tensor_name << "'. "
              << "First value: " << data[0] << std::endl;
}
