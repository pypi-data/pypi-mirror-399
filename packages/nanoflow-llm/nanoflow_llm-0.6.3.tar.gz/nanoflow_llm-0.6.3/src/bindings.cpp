
#include <pybind11/pybind11.h>
#include "engine.h"

namespace py = pybind11;

PYBIND11_MODULE(nanoflow_ext, m) {
    m.doc() = "NanoFlow Universal Bindings";

    py::class_<NanoFlowEngine>(m, "NanoFlowEngine")
        .def(py::init<int>(), py::arg("ram_limit_mb") = 16)
        .def("set_weights", &NanoFlowEngine::set_weights, 
             "Register weights from raw pointer",
             py::arg("name"), py::arg("raw_pointer"), 
             py::arg("rows"), py::arg("cols"), 
             py::arg("ggml_type_id") = 0) // Default to F32 (0)
        .def("compute", [](NanoFlowEngine& self, std::string name) {
            self.compute(name);
        }, py::arg("tensor_name") = ""); // Default empty string to support engine.compute()
}
