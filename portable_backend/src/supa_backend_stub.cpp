#include "backend_api.hpp"

namespace portable_backend {

Status scale(TensorView input, TensorView output, float factor) {
  (void)input;
  (void)output;
  (void)factor;
  // A stub is safer than pretending that a CUDA kernel is a SUPA kernel. This
  // is the explicit seam to replace inside a real BIRENSUPA environment.
  return Status::kNotAvailable;
}

const char* status_string(Status status) {
  switch (status) {
    case Status::kOk: return "ok";
    case Status::kNotAvailable: return "not_available";
    case Status::kInvalidArgument: return "invalid_argument";
  }
  return "unknown";
}

}  // namespace portable_backend
