cmake_minimum_required(VERSION 3.14)
project(reverseaffinite VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt5 REQUIRED COMPONENTS Widgets Gui Core)

add_executable(reverseaffinite
    src/main.cpp
    src/layers.cpp
    src/history.cpp
    src/filters.cpp
    src/tools.cpp
    src/canvas.cpp
    src/panels.cpp
    src/app_ui.cpp
)

target_include_directories(reverseaffinite PRIVATE include)
target_link_libraries(reverseaffinite PRIVATE Qt5::Widgets Qt5::Gui Qt5::Core)

# Install instructions:
# sudo apt install qtbase5-dev qt5-qmake cmake g++
# mkdir build && cd build && cmake .. && make -j$(nproc)
