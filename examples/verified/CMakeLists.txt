cmake_minimum_required(VERSION 3.20)

project(SharpRuntimeWebsiteExamples LANGUAGES CXX C)

if(NOT DEFINED SHARP_RUNTIME_SOURCE_DIR)
    message(FATAL_ERROR "SHARP_RUNTIME_SOURCE_DIR must name the pinned Sharp Runtime checkout")
endif()

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(
    SHARP_RUNTIME_COMPONENTS
    Console
    Collections.Core
    IO
    Text.Json
    Threading.Tasks
    Threading.Channels
    Net
    Net.Http
    Net.WebSockets
    CACHE STRING "Components used by website verification examples" FORCE
)
set(SHARP_RUNTIME_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(SHARP_RUNTIME_BUILD_BENCHMARKS OFF CACHE BOOL "" FORCE)
add_subdirectory("${SHARP_RUNTIME_SOURCE_DIR}" sharp-runtime)

function(add_website_example name component)
    add_executable("${name}" "${name}.cpp")
    target_link_libraries("${name}" PRIVATE "SharpRuntime::${component}")
    if(MSVC)
        target_compile_options("${name}" PRIVATE /W4 /WX)
    else()
        # Match the runtime's own public-consumer warning profile. -Wpedantic would reject
        # the intentional GNU/Clang unsigned __int128 spelling exposed by Decimal.hpp.
        target_compile_options("${name}" PRIVATE -Wall -Wextra -Werror)
    endif()
endfunction()

add_website_example(example_hello_console Console)
add_website_example(example_ported_class Core.Base)
add_website_example(example_arrays_spans Core.Base)
add_website_example(example_collections Collections.Core)
add_website_example(example_memory_stream IO)
add_website_example(example_filesystem IO)
add_website_example(example_json Text.Json)
add_website_example(example_tasks Threading.Tasks)
add_website_example(example_channels Threading.Channels)
add_website_example(example_network_types Net)
add_website_example(example_http_configuration Net.Http)
add_website_example(example_websocket_shape Net.WebSockets)

add_custom_target(
    website_examples
    DEPENDS
        example_hello_console
        example_ported_class
        example_arrays_spans
        example_collections
        example_memory_stream
        example_filesystem
        example_json
        example_tasks
        example_channels
        example_network_types
        example_http_configuration
        example_websocket_shape
)
