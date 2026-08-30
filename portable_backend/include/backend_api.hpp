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

struct ConstTensorView {
  const void* data = nullptr;
  std::size_t elements = 0;
};

// Backend-specific namespaces prevent duplicate symbols when more than one
// adapter is linked into the same process. The SUPA entry point remains an
// explicit stub until it can be implemented and tested with the official SDK.
namespace supa {
Status scale(ConstTensorView input, TensorView output, float factor);
}  // namespace supa

namespace cuda {
Status scale(ConstTensorView input, TensorView output, float factor);
}  // namespace cuda

const char* status_string(Status status);

}  // namespace portable_backend
