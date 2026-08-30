cmake_minimum_required(VERSION 3.22)
project(gpu_perf_playbook LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(portable_backend STATIC
  portable_backend/src/supa_backend_stub.cpp
  portable_backend/src/status.cpp
)
target_include_directories(portable_backend PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/portable_backend/include
)

option(BUILD_CUDA_BACKEND "Build the optional CUDA backend" OFF)
if(BUILD_CUDA_BACKEND)
  enable_language(CUDA)
  if(MSVC AND NOT CMAKE_CUDA_RUNTIME_LIBRARY)
    set(CMAKE_CUDA_RUNTIME_LIBRARY Shared)
  endif()
  add_library(cuda_backend STATIC portable_backend/src/cuda_backend.cu)
  target_include_directories(cuda_backend PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/portable_backend/include
  )
  set_target_properties(cuda_backend PROPERTIES CUDA_STANDARD 17)
endif()

add_executable(portable_backend_tests tests/test_portable_backend.cpp)
target_link_libraries(portable_backend_tests PRIVATE portable_backend)

enable_testing()
add_test(NAME portable_backend_tests COMMAND portable_backend_tests)
