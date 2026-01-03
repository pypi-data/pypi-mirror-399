#--------------------------------------------------------------------------------#
REGISTER_GLOBAL_HEADERS(INCLUDES)
#--------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------#
# Get Fortran sources
#--------------------------------------------------------------------------------#

REGISTER_GLOBAL_FORTRAN_SOURCES(FORTRAN_SOURCES)
get_property(FORTRAN_SOURCES GLOBAL PROPERTY FORTRAN_SOURCES)

#--------------------------------------------------------------------------------#
# Build shared library
#--------------------------------------------------------------------------------#

add_library(nulapack_shared SHARED ${FORTRAN_SOURCES})
target_include_directories(nulapack_shared PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include>
)
set_target_properties(nulapack_shared PROPERTIES
    OUTPUT_NAME nulapack
    SOVERSION 1
    VERSION ${PROJECT_VERSION}
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib
)

#--------------------------------------------------------------------------------#
# Build static library
#--------------------------------------------------------------------------------#
add_library(nulapack_static STATIC ${FORTRAN_SOURCES})
target_include_directories(nulapack_static PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include>
)
set_target_properties(nulapack_static PROPERTIES
    OUTPUT_NAME nulapack
    VERSION ${PROJECT_VERSION}
    ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib
)

#--------------------------------------------------------------------------------#
# Install targets
#--------------------------------------------------------------------------------#

install(TARGETS nulapack_shared nulapack_static
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)
