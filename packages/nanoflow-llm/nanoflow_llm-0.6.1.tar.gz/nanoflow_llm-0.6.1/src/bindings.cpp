
#include <pybind11/pybind11.h>
#include "engine.h"

namespace py = pybind11;

PYBIND11_MODULE(nanoflow_ext, m) {
    m.doc() = "NanoFlow Universal Bindings";

    py::class_<NanoFlowEngine>(m, "NanoFlowEngine")
        .def(py::init<>())
        .def("set_weights", &NanoFlowEngine::set_weights, 
             "Register weights from raw pointer",
             py::arg("name"), py::arg("raw_pointer"), 
             py::arg("rows"), py::arg("cols"), py::arg("ggml_type_id"))
        .def("compute", &NanoFlowEngine::compute);
}
