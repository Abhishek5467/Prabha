cmake_minimum_required(VERSION 3.20)
project(prabha_core LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# vendored single-header nlohmann/json (no network needed at configure time)
add_library(nlohmann_json INTERFACE)
target_include_directories(nlohmann_json INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/third_party)

add_library(prabha_core INTERFACE)
target_include_directories(prabha_core INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(prabha_core INTERFACE nlohmann_json)

# conformance runner — the C++ engine's finish line is this binary printing 14/14
add_executable(prabha_conformance src/main_conformance.cpp)
target_link_libraries(prabha_conformance PRIVATE prabha_core)

if(MSVC)
  target_compile_options(prabha_conformance PRIVATE /W4 /permissive-)
else()
  target_compile_options(prabha_conformance PRIVATE -Wall -Wextra)
endif()
