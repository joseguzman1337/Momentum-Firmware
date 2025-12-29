cmake_minimum_required(VERSION 3.22)
project(RTL8814AU_DriverKit LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(RTL8814AU_DriverKit MODULE
    Sources/Driver.cpp
    Sources/USBDevice.cpp
)

target_include_directories(RTL8814AU_DriverKit PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/Sources
)
