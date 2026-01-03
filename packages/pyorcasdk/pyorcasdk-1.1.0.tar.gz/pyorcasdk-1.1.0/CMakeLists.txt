cmake_minimum_required(VERSION 3.28...4.0)

# Scikit-build-core sets these values for you, or you can just hard-code the
# name and version.
project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  DESCRIPTION "C++ bindings for Iris Dynamics orcaSDK"
  LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include(FetchContent)

FetchContent_Declare(
  orcaSDK
  SOURCE_DIR "${PROJECT_SOURCE_DIR}/extern/orcaSDK"
)

FetchContent_MakeAvailable(orcaSDK)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

FetchContent_Declare(
  pybind11
  SOURCE_DIR "${PROJECT_SOURCE_DIR}/extern/pybind11"
)

FetchContent_MakeAvailable(pybind11)

pybind11_add_module(_pyorcasdk
    bindings/pyorcasdk.cpp
) 

target_link_libraries(_pyorcasdk PRIVATE orcaSDK::core)

set_target_properties(_pyorcasdk PROPERTIES 
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/_pyorcasdk"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/_pyorcasdk"
)

install(FILES ${PROJECT_SOURCE_DIR}/extern/orca-api/python/orca_registers.py DESTINATION ${SKBUILD_PROJECT_NAME})

install(TARGETS _pyorcasdk DESTINATION ${SKBUILD_PROJECT_NAME})