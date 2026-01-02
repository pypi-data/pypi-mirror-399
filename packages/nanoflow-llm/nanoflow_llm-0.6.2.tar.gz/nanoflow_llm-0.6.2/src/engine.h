
#pragma once
#include "ggml.h"
#include <string>
#include <unordered_map>
#include <vector>
#include <cstdint>

class NanoFlowEngine {
public:
    NanoFlowEngine();
    ~NanoFlowEngine();

    // Format-Agnostic Weight Setter (Zero-Copy)
    // Python passes the raw memory address of the tensor data here.
    void set_weights(const std::string& name, uintptr_t raw_pointer, 
                     int rows, int cols, int ggml_type_id);

    // Trigger computation (Demonstration)
    void compute(const std::string& tensor_name);

private:
    struct ggml_context* ctx;
    std::unordered_map<std::string, struct ggml_tensor*> tensors;
};
