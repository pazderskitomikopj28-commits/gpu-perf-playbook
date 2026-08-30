#include "backend_api.hpp"

#include <cuda_runtime.h>

#include <limits>

namespace {

__global__ void scale_kernel(const float* input, float* output, std::size_t n,
                             float factor) {
  const std::size_t index = static_cast<std::size_t>(blockIdx.x) * blockDim.x +
                            threadIdx.x;
  if (index < n) output[index] = input[index] * factor;
}

}  // namespace

namespace portable_backend {
namespace cuda {

Status scale(ConstTensorView input, TensorView output, float factor) {
  if (input.data == nullptr || output.data == nullptr ||
      input.elements == 0 || input.elements != output.elements ||
      input.elements >
          static_cast<std::size_t>(std::numeric_limits<int>::max()) * 256) {
    return Status::kInvalidArgument;
  }
  const int blocks = static_cast<int>((input.elements + 255) / 256);
  scale_kernel<<<blocks, 256>>>(static_cast<const float*>(input.data),
                                static_cast<float*>(output.data),
                                input.elements, factor);
  return cudaGetLastError() == cudaSuccess ? Status::kOk : Status::kNotAvailable;
}

}  // namespace cuda
}  // namespace portable_backend
