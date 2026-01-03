#pragma once
#include "pybind11/pybind11.h"
#include "pybind11/operators.h"
#include "pybind11/stl.h"
#include "util.h"
#include "Vector.h"

namespace py = pybind11;

template<typename T, uint32_t Size>
void bind_Vector(py::module_ const& module, char const* className) {
    using vector = math3d::Vector<T, Size>;
    auto vec_class =
        py::class_<vector>(module, className)
        // Construction
        .def(py::init())
        .def(py::init([](py::list const& list) {
            auto const input = list.cast<std::vector<T>>();
            return vector{input};
        }))
        // Member access
        .def_property("x",
            [](vector const& self) {
                double const value = self.x;
                return value;
            },
            [](vector& self, double const value) {
                self.x = value;
            }
        )
        .def_property("y",
        [](vector const& self) {
                T const value = self.y;
                return value;
            },
            [](vector& self, double const value) {
                self.y = value;
            }
        )
        .def_property("z",
        [](vector const& self) {
                T const value = self.z;
                return value;
            },
            [](vector& self, double const value) {
                self.z = value;
            }
        )
        // Formatted output
        .def("__str__", [](vector const& v) {
            return util::convertSpaceToNewLine(v.asString());
        })
        .def("__repr__", [](vector const& v) {
            return util::convertSpaceToNewLine(v.asString());
        })
        // Operations
        .def(py::self + py::self)
        .def(py::self - py::self)
        .def(py::self * T{})
        .def(py::self / T{})
        .def("dot", &vector::dot)
        .def("normalize", [](vector& v) { v.normalize(); return v; })
        .def("length", [](vector const& v) { return v.length(); })
        .def("length_sqr", [](vector const& v) { return v.lengthSquared(); })
        .def("projection", &vector::getVectorProjection);
    if constexpr (Size == 3) {
        vec_class
        .def(py::self * py::self);
    }
}