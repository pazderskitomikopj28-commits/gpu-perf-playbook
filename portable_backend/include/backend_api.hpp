#pragma once

#include <cstddef>

namespace portable_backend {

enum class Status {
  kOk = 0,
  kNotAvailable,
  kInvalidArgument,
};

struct TensorView {
  void* data = nullptr;
  std::size_t elements = 0;
};

// This deliberately small interface keeps algorithm code independent from a
// particular GPU runtime. A real SUPA implementation should be added only
// after the official SDK, compiler and device semantics are available.
Status scale(TensorView input, TensorView output, float factor);
const char* status_string(Status status);

}  // namespace portable_backend
