include(FortranCInterface)

FortranCInterface_VERIFY()

REGISTER_GLOBAL_FORTRAN_SOURCES(FORTRAN_SOURCES)

get_property(FORTRAN_SOURCES GLOBAL PROPERTY FORTRAN_SOURCES)

set(SYMBOLS)

foreach(SRC ${FORTRAN_SOURCES})
    get_filename_component(SRC_NAME ${SRC} NAME_WE)
    list(APPEND SYMBOLS ${SRC_NAME})
endforeach()

FortranCInterface_HEADER(
    ${CMAKE_SOURCE_DIR}/interface/cpp/mangling.h
    MACRO_NAMESPACE    "API_"
    SYMBOL_NAMESPACE   "API_"
    SYMBOLS            ${SYMBOLS}
)
