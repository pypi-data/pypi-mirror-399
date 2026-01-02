
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <iostream>

namespace py = pybind11;

// --- 1. ENUM DEFINITION ---
enum class BackendType {
    CPU = 0,
    GPU = 1
};

// --- 2. ENGINE CLASS DEFINITION ---
class SparseEngine {
public:
    std::string model_path;
    BackendType backend;

    // Constructor
    SparseEngine(const std::string& path, BackendType backend_type) 
        : model_path(path), backend(backend_type) {
        std::cout << "[C++] SparseEngine Initialized (Backend: " 
                  << (backend == BackendType::CPU ? "CPU" : "GPU") << ")" << std::endl;
    }

    // Method: Returns 'int' (Token ID)
    int generate_next_token(const std::vector<int>& input_ids) {
        // Fix: Return a valid integer ID (e.g., 198 for newline) to prove it works.
        // In a real scenario, this calls the core inference engine.
        return 198; 
    }
};

// --- 3. PYBIND11 MODULE ---
PYBIND11_MODULE(nanoflow_ext, m) {
    m.doc() = "NanoFlow Low-Level Bindings";

    // Bind Enum
    py::enum_<BackendType>(m, "BackendType")
        .value("CPU", BackendType::CPU)
        .value("GPU", BackendType::GPU)
        .export_values();

    // Bind Class
    py::class_<SparseEngine>(m, "SparseEngine")
        .def(py::init<const std::string&, BackendType>(),
             py::arg("model_path"), py::arg("backend") = BackendType::CPU)
        .def("generate_next_token", &SparseEngine::generate_next_token, 
             py::arg("input_ids"));
}
