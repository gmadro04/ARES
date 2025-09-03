cmake_minimum_required(VERSION 2.6)
project(loop_function)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS "-Wall -Wextra")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}")

# Check for Lua and add include path
find_package(Lua53 REQUIRED)
include_directories(${LUA_INCLUDE_DIR})

# Creating news code to compile and find_package
# -- old lines to find and compile package argos3
# Check for ARGoS3
#find_package(PkgConfig)
#pkg_check_modules(ARGOS REQUIRED argos3)

# Add ARGoS paths
#include_directories(${ARGOS_INCLUDE_DIRS})
#link_directories(${ARGOS_LIBRARY_DIRS})
# -- this is the new change to compile and find_package
find_package(PkgConfig REQUIRED)
pkg_check_modules(ARGOS QUIET argos3)
if (NOT ARGOS_FOUND)
  pkg_check_modules(ARGOS REQUIRED argos3_simulator)
endif()

include_directories(${ARGOS_INCLUDE_DIRS})
link_directories(${ARGOS_LIBRARY_DIRS})

# Create the loop function library
add_library(loop_function SHARED loop_function.h loop_function.cpp)
target_link_libraries(loop_function
  ${ARGOS_LIBRARIES}
  ${LUA_LIBRARIES}
  argos3plugin_simulator_entities
  argos3plugin_simulator_footbot
  argos3plugin_simulator_media)
