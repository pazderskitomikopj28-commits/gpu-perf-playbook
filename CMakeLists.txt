cmake_minimum_required(VERSION 3.24)
project(gpu_perf_playbook LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(portable_backend STATIC
  portable_backend/src/supa_backend_stub.cpp
)
target_include_directories(portable_backend PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/portable_backend/include
)

option(BUILD_CUDA_BACKEND "Build the optional CUDA backend" OFF)
if(BUILD_CUDA_BACKEND)
  enable_language(CUDA)
  add_library(cuda_backend STATIC portable_backend/src/cuda_backend.cu)
  target_include_directories(cuda_backend PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/portable_backend/include
  )
  set_target_properties(cuda_backend PROPERTIES CUDA_STANDARD 17)
endif()
