#include "backend_api.hpp"

#include <cstring>
#include <iostream>

int main() {
  float input[] = {1.0f, 2.0f};
  float output[] = {0.0f, 0.0f};
  const portable_backend::ConstTensorView input_view{input, 2};
  const portable_backend::TensorView output_view{output, 2};
  const auto status =
      portable_backend::supa::scale(input_view, output_view, 2.0f);
  if (status != portable_backend::Status::kNotAvailable) {
    std::cerr << "SUPA stub must report not_available\n";
    return 1;
  }
  if (std::strcmp(portable_backend::status_string(status), "not_available") !=
      0) {
    std::cerr << "unexpected status string\n";
    return 1;
  }
  const portable_backend::ConstTensorView invalid_input{nullptr, 2};
  if (portable_backend::supa::scale(invalid_input, output_view, 2.0f) !=
      portable_backend::Status::kInvalidArgument) {
    std::cerr << "invalid tensor view was not rejected\n";
    return 1;
  }
  std::cout << "portable backend tests passed\n";
  return 0;
}
