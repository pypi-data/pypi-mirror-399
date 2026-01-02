
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "nanoflow_core.h"

namespace py = pybind11;

// PYBIND11_MODULE macro must match the filename for import to work
PYBIND11_MODULE(nanoflow_ext_v7, m) {
    m.doc() = "NanoFlow v0.7 Sparse Streaming Engine";

    py::enum_<nanoflow::BackendType>(m, "BackendType")
        .value("CPU", nanoflow::BackendType::CPU)
        .value("CUDA", nanoflow::BackendType::CUDA)
        .value("METAL", nanoflow::BackendType::METAL)
        .export_values();

    py::class_<nanoflow::SparseEngine>(m, "SparseEngine")
        .def(py::init<const std::string&, nanoflow::BackendType>(),
             py::arg("model_path"),
             py::arg("backend") = nanoflow::BackendType::CPU)
        .def("generate_next_token", &nanoflow::SparseEngine::generate_next_token,
             py::arg("input_ids"));
}
