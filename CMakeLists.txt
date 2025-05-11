cmake_minimum_required(VERSION 3.18)

project(ispc_texcomp)

if (MSVC)
install(FILES
	build/ispc_texcomp.dll
	DESTINATION bin)
else ()
install(FILES
	build/libispc_texcomp.dylib
	DESTINATION bin)
endif ()




install(FILES
	ispc_texcomp/ispc_texcomp.h
	DESTINATION include/ispc_texcomp)