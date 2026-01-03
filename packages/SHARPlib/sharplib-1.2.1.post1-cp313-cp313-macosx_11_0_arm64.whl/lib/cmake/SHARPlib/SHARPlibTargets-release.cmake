#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "SHARPlib::SHARPlib" for configuration "Release"
set_property(TARGET SHARPlib::SHARPlib APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(SHARPlib::SHARPlib PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libSHARPlib.a"
  )

list(APPEND _cmake_import_check_targets SHARPlib::SHARPlib )
list(APPEND _cmake_import_check_files_for_SHARPlib::SHARPlib "${_IMPORT_PREFIX}/lib/libSHARPlib.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
