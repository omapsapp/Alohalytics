.PHONY: all indent clean

ALOHALYTICS_ROOT=../Alohalytics
UTF8PROC_ROOT=../3party/utf8proc

C=gcc
CPP=g++
CFLAGS=-Wall -W
CPPFLAGS=-std=c++11 ${CFLAGS} -I${ALOHALYTICS_ROOT}/src
LDFLAGS=-lz -pthread
MORE_SOURCES=${ALOHALYTICS_ROOT}/src/posix/file_manager_posix_impl.cc

PWD=$(shell pwd)
SRC=$(wildcard *.cc)
BIN=$(SRC:%.cc=build/%)
OBJ=build/file_manager_posix_impl.o
C_OBJ=build/utf8proc.o
OS := $(shell uname)

all: build ${BIN}

indent:
	(find . -name "*.cc" -o -name "*.h") | xargs clang-format -i

clean:
	rm -rf build

build:
	mkdir -p $@

build/%: %.cc ${OBJ} ${C_OBJ}
	${CPP} ${CPPFLAGS} ${OBJ} ${C_OBJ} -o $@ $< ${LDFLAGS}

${OBJ}: ${MORE_SOURCES}
	${CPP} ${CPPFLAGS} -c ${MORE_SOURCES} -o $@

${C_OBJ}: ${UTF8PROC_ROOT}/utf8proc.c
	${C} ${CFLAGS} -c ${UTF8PROC_ROOT}/utf8proc.c -o $@
