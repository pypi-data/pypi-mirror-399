cmake_minimum_required(VERSION 3.22)

project(NULAPACK VERSION ${NULAPACK_VERSION} LANGUAGES C CXX Fortran)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)

enable_language(Fortran)
enable_language(C)

if(WIN32)
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static-libgcc -static-libstdc++")
endif()

file(GLOB CMAKE_FILES "${CMAKE_SOURCE_DIR}/cmake/*.cmake")

foreach(CMAKE_FILE ${CMAKE_FILES})
    include(${CMAKE_FILE})
endforeach()

SYSTEM_INFO()

add_subdirectory(src)
add_subdirectory(interface/cpp)

option(BUILD_TEST "Build tests" OFF)

if(BUILD_TEST)
    include(FetchContent)
    FetchContent_Declare(
        catch2
        GIT_REPOSITORY https://github.com/catchorg/Catch2.git
        GIT_TAG v3.5.4
    )
    FetchContent_MakeAvailable(catch2)

    add_subdirectory(tests/cpp)
endif()
