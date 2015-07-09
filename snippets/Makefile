.PHONY: all indent clean

ALOHALYTICS_ROOT=../Alohalytics
CPP=g++
CPPFLAGS=-std=c++11 -Wall -W -I${ALOHALYTICS_ROOT}/src
LDFLAGS=-lz -pthread
MORE_SOURCES=${ALOHALYTICS_ROOT}/src/posix/file_manager_posix_impl.cc

PWD=$(shell pwd)
SRC=$(wildcard *.cc)
BIN=$(SRC:%.cc=build/%)
OBJ=build/file_manager_posix_impl.obj
OS := $(shell uname)

all: build ${BIN}

indent:
	(find . -name "*.cc") | xargs clang-format -i

clean:
	rm -rf build

build:
	mkdir -p $@

build/%: %.cc ${OBJ}
	${CPP} ${CPPFLAGS} ${OBJ} -o $@ $< ${LDFLAGS}

${OBJ}: ${MORE_SOURCES}
	${CPP} ${CPPFLAGS} -c ${MORE_SOURCES} -o $@
