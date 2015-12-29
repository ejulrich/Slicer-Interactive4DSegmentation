cmake_minimum_required(VERSION 2.8.9)

project(Interactive4DSegmentation)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/Interactive4DSegmentation")
set(EXTENSION_CATEGORY "Segmentation")
set(EXTENSION_CONTRIBUTORS "Ethan Ulrich (University of Iowa)")
set(EXTENSION_DESCRIPTION "The Interactive 4-D Segmentation extension provides tools for 4-D segmentation of objects in multiple volumes.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/Interactive4DSegmentation.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/Interactive4DSegmentation/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(Segment4D)
add_subdirectory(Load4D)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
