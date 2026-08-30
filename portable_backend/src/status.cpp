#include "backend_api.hpp"

namespace portable_backend {

const char* status_string(Status status) {
  switch (status) {
    case Status::kOk:
      return "ok";
    case Status::kNotAvailable:
      return "not_available";
    case Status::kInvalidArgument:
      return "invalid_argument";
  }
  return "unknown";
}

}  // namespace portable_backend
