#include "backend_api.hpp"

namespace portable_backend {
namespace supa {

Status scale(ConstTensorView input, TensorView output, float factor) {
  (void)factor;
  if (input.data == nullptr || output.data == nullptr || input.elements == 0 ||
      input.elements != output.elements) {
    return Status::kInvalidArgument;
  }
  // A stub is safer than pretending that a CUDA kernel is a SUPA kernel. This
  // is the explicit seam to replace inside a real BIRENSUPA environment.
  return Status::kNotAvailable;
}

}  // namespace supa
}  // namespace portable_backend
