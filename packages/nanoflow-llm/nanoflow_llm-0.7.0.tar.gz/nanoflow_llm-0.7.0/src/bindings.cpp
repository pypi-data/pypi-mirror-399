
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Required for automatic conversion of std::vector
#include "nanoflow_core.h"

namespace py = pybind11;

// --- NANOFLOW v0.7 PYTHON BINDINGS ---
// Exposes the C++ SparseEngine to Python

PYBIND11_MODULE(nanoflow_ext, m) {
    m.doc() = "NanoFlow v0.7 Sparse Streaming Engine";

    // 1. Bind the BackendType Enum
    py::enum_<nanoflow::BackendType>(m, "BackendType")
        .value("CPU", nanoflow::BackendType::CPU)
        .value("CUDA", nanoflow::BackendType::CUDA)
        .value("METAL", nanoflow::BackendType::METAL)
        .export_values();

    // 2. Bind the SparseEngine Class
    py::class_<nanoflow::SparseEngine>(m, "SparseEngine")
        .def(py::init<const std::string&, nanoflow::BackendType>(),
             py::arg("model_path"),
             py::arg("backend") = nanoflow::BackendType::CPU,
             "Initialize the engine with a .safetensors model path and backend.")
             
        .def("generate_next_token", &nanoflow::SparseEngine::generate_next_token,
             py::arg("input_ids"),
             "Prefetch tiles and compute the next token for a sequence of input IDs.");
}
