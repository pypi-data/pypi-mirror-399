#include <pybind11/pybind11.h>
#include <iostream>
#include <vector>
#include <chrono>
#include <random>
#include <iomanip>

#include "ggml.h"
#include "ggml-alloc.h"
#include "ggml-backend.h"

namespace py = pybind11;

// Explicit declaration for cpu backend init if header is missing in include path
extern "C" ggml_backend_t ggml_backend_cpu_init(void);

class NanoFlowEngine {
private:
    struct ggml_context * ctx = nullptr;
    ggml_backend_t backend = nullptr;
    ggml_gallocr_t alloc = nullptr;
    size_t ram_limit_bytes;
    std::string model_path;

public:
    // Constructor: Initialize Context & Backend
    NanoFlowEngine(std::string path, int ram_limit_mb) : model_path(path) {
        ram_limit_bytes = (size_t)ram_limit_mb * 1024 * 1024;
        
        std::cout << "[NanoFlow] Initializing Engine with " << ram_limit_mb << "MB Fixed Buffer..." << std::endl;

        // 1. Initialize Params (No Alloc - we use gallocr later)
        struct ggml_init_params params = {
            /*.mem_size   =*/ ram_limit_bytes,
            /*.mem_buffer =*/ NULL,
            /*.no_alloc   =*/ true,
        };

        // 2. Create Context
        ctx = ggml_init(params);
        if (!ctx) {
            throw std::runtime_error("Failed to create ggml context");
        }

        // 3. Initialize Backend (CPU)
        backend = ggml_backend_cpu_init();
        if (!backend) {
            ggml_free(ctx);
            throw std::runtime_error("Failed to initialize CPU backend");
        }

        // 4. Initialize Allocator (Manages the tensor memory)
        alloc = ggml_gallocr_new(ggml_backend_get_default_buffer_type(backend));
    }

    // Destructor: Cleanup
    ~NanoFlowEngine() {
        if (alloc) ggml_gallocr_free(alloc);
        if (backend) ggml_backend_free(backend);
        if (ctx) ggml_free(ctx);
        std::cout << "[NanoFlow] Engine Destroyed." << std::endl;
    }

    // Benchmark Method: F16 x F32 Matrix Multiplication
    float benchmark_layer(int rows, int cols) {
        // Note: In a real persistent engine, we would reset the context or use a separate graph context.
        // For this PoC, we append to the existing context. 
        // WARNING: Repeated calls without reset will eventually fill the context memory.
        
        // 1. Create Tensors
        // W: [rows, cols] (F16 Weights)
        // X: [rows, 1]    (F32 Input)
        struct ggml_tensor * W = ggml_new_tensor_2d(ctx, GGML_TYPE_F16, rows, cols);
        struct ggml_tensor * X = ggml_new_tensor_2d(ctx, GGML_TYPE_F32, rows, 1);

        // 2. Define Operation: Q = W * X
        struct ggml_tensor * Q = ggml_mul_mat(ctx, W, X);

        // 3. Build Graph
        struct ggml_cgraph * gf = ggml_new_graph(ctx);
        ggml_build_forward_expand(gf, Q);

        // 4. Allocate Memory (Reserve & Alloc)
        // Use the fixed buffer strategy via gallocr
        if (!ggml_gallocr_reserve_n(alloc, gf, NULL, NULL)) {
            std::cerr << "[Error] Failed to reserve memory for graph!" << std::endl;
            return -1.0f;
        }
        if (!ggml_gallocr_alloc_graph(alloc, gf)) {
            std::cerr << "[Error] Failed to allocate graph tensors!" << std::endl;
            return -1.0f;
        }

        // 5. Fill with Random Data (Simulating Load)
        float * x_data = (float *) X->data;
        for (int i = 0; i < ggml_nelements(X); i++) {
            x_data[i] = ((float)rand() / RAND_MAX);
        }
        
        // Convert dummy float weights to F16
        ggml_fp16_t * w_data = (ggml_fp16_t *) W->data;
        std::vector<float> w_temp(ggml_nelements(W));
        for (size_t i = 0; i < w_temp.size(); i++) {
            w_temp[i] = ((float)rand() / RAND_MAX) * 0.01f;
        }
        ggml_fp32_to_fp16_row(w_temp.data(), w_data, ggml_nelements(W));

        // 6. Compute & Measure
        auto start = std::chrono::high_resolution_clock::now();
        
        ggml_backend_graph_compute(backend, gf);
        
        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> duration = end - start;

        return (float)duration.count();
    }
};

// Pybind11 Binding Code
PYBIND11_MODULE(nanoflow, m) {
    m.doc() = "NanoFlow C++ Inference Engine";

    py::class_<NanoFlowEngine>(m, "NanoFlowEngine")
        .def(py::init<std::string, int>())
        .def("benchmark_layer", &NanoFlowEngine::benchmark_layer, "Run a layer benchmark",
             py::arg("rows"), py::arg("cols"));
}
