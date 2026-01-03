/**
 * Python bindings for Kanerva SDM using pybind11.
 * 
 * (c) 2025 Simon Wong
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "kanerva_sdm/kanerva_sdm.h"

namespace py = pybind11;

PYBIND11_MODULE(_kanerva_sdm, m) {
    m.doc() = "Sparse Distributed Memory implementation based on Kanerva (1992)";

    py::class_<KanervaSDM>(m, "KanervaSDM")
        .def(py::init<int, int, int, int, unsigned int>(),
             py::arg("address_dimension"),
             py::arg("memory_dimension"),
             py::arg("num_locations"),
             py::arg("hamming_threshold"),
             py::arg("random_seed") = 42,
             "Initialize the Kanerva Sparse Distributed Memory.\n\n"
             "Parameters\n"
             "----------\n"
             "address_dimension : int\n"
             "    Length of address vectors (N).\n"
             "memory_dimension : int\n"
             "    Length of memory vectors (U).\n"
             "num_locations : int\n"
             "    Number of hard locations (M).\n"
             "hamming_threshold : int\n"
             "    Hamming distance threshold for activation (H).\n"
             "random_seed : int, optional\n"
             "    Seed for reproducible random generation of hard locations (default: 42).\n\n"
             "Raises\n"
             "------\n"
             "ValueError\n"
             "    If any dimension or threshold is non-positive.")
        
        .def("write", &KanervaSDM::write,
             py::arg("address"),
             py::arg("memory"),
             "Write a memory to an address.\n\n"
             "Parameters\n"
             "----------\n"
             "address : list of int\n"
             "    Target address vector (x) of size address_dimension.\n"
             "    Must contain only 0s and 1s.\n"
             "memory : list of int\n"
             "    Memory vector (w) of size memory_dimension.\n"
             "    Must contain only 0s and 1s.\n\n"
             "Raises\n"
             "------\n"
             "ValueError\n"
             "    If address or memory vectors have incorrect size or contain non-binary values.")
        
        .def("read", &KanervaSDM::read,
             py::arg("address"),
             "Read a memory from an address.\n\n"
             "Parameters\n"
             "----------\n"
             "address : list of int\n"
             "    Target address vector (x) of size address_dimension.\n"
             "    Must contain only 0s and 1s.\n\n"
             "Returns\n"
             "-------\n"
             "list of int\n"
             "    Recalled memory vector (z) of size memory_dimension.\n"
             "    Returns all zeros if no locations are activated.\n\n"
             "Raises\n"
             "------\n"
             "ValueError\n"
             "    If address vector has incorrect size or contains non-binary values.")
        
        .def("erase_memory", &KanervaSDM::erase_memory,
             "Erase memory matrix (C), but preserve address matrix (A).\n\n"
             "This resets all memory counters to zero while keeping the hard locations intact.")
        
        .def_property_readonly("address_dimension", &KanervaSDM::get_address_dimension,
                              "Length of address vectors (N).")
        .def_property_readonly("memory_dimension", &KanervaSDM::get_memory_dimension,
                              "Length of memory vectors (U).")
        .def_property_readonly("num_locations", &KanervaSDM::get_num_locations,
                              "Number of hard locations (M).")
        .def_property_readonly("hamming_threshold", &KanervaSDM::get_hamming_threshold,
                              "Hamming distance threshold for activation (H).")
        .def_property_readonly("memory_count", &KanervaSDM::get_memory_count,
                              "Number of stored memories (T).")
        
        .def("__repr__", [](const KanervaSDM &sdm) {
            return "<KanervaSDM(address_dim=" + std::to_string(sdm.get_address_dimension()) +
                   ", memory_dim=" + std::to_string(sdm.get_memory_dimension()) +
                   ", locations=" + std::to_string(sdm.get_num_locations()) +
                   ", threshold=" + std::to_string(sdm.get_hamming_threshold()) +
                   ", memories=" + std::to_string(sdm.get_memory_count()) + ")>";
        });

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}