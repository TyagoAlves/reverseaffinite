cmake_minimum_required(VERSION 3.14)
project(reverseaffinite VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt5 REQUIRED COMPONENTS Widgets Gui Core OpenGL)

# Check for OpenGL
find_package(OpenGL REQUIRED)

add_executable(reverseaffinite
    src/main.cpp
    src/layers.cpp
    src/history.cpp
    src/filters.cpp
    src/tools.cpp
    src/canvas.cpp
    src/panels.cpp
    src/app_ui.cpp
    src/simd_ops.cpp
    src/gl_canvas.cpp
)

target_include_directories(reverseaffinite PRIVATE include)

target_link_libraries(reverseaffinite PRIVATE
    Qt5::Widgets
    Qt5::Gui
    Qt5::Core
    Qt5::OpenGL
    OpenGL::GL
)

# Enable SIMD flags for simd_ops.cpp
set_source_files_properties(src/simd_ops.cpp PROPERTIES
    COMPILE_FLAGS "-msse2 -mavx2"
)

# Optionally enable SSE2 globally
if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
    target_compile_options(reverseaffinite PRIVATE -msse2)
endif()

# Install instructions:
# sudo apt install qtbase5-dev qt5-qmake cmake g++ libgl1-mesa-dev
# mkdir build && cd build && cmake .. && make -j$(nproc)
