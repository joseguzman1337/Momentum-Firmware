cmake_minimum_required(VERSION 3.22)
project(RTL8814AU_Shim LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(rtl8814au-shim
    src/main.cpp
    src/rtl8814au_shim.cpp
)

target_include_directories(rtl8814au-shim PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(rtl8814au-shim
    "-framework IOKit"
    "-framework CoreFoundation"
)
