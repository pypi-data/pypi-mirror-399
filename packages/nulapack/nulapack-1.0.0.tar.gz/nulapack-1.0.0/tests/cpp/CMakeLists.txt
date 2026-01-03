get_property(FORTRAN_SOURCES GLOBAL PROPERTY FORTRAN_SOURCES)
add_library(fortran_objs OBJECT ${FORTRAN_SOURCES})

file(GLOB TEST_SOURCES CONFIGURE_DEPENDS *.cpp)

foreach(src ${TEST_SOURCES})
    get_filename_component(name ${src} NAME_WE)

    add_executable(${name} ${src} $<TARGET_OBJECTS:fortran_objs>)
    target_include_directories(${name} PRIVATE ${CMAKE_SOURCE_DIR}/interface/cpp)
    target_link_libraries(${name} PRIVATE m Catch2::Catch2WithMain)
endforeach()

enable_testing()
