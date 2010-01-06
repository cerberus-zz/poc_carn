# Makefile for ideorum
SHELL := /bin/bash

# Internal variables.
file_version=0.1.0
root_dir=.
app_engine_dir=${root_dir}/external/google_appengine
app_cfg=${app_engine_dir}/appcfg.py
app_server=${app_engine_dir}/dev_appserver.py

src_dir=${root_dir}/src
tests_dir=${root_dir}/tests


# orchestrator targets

prepare_build: clean

test: unit func

all: prepare_build compile test

run_unit: prepare_build compile unit
run_functional: prepare_build compile func

clean:
	@rm -rf .coverage
	@rm -f ${compile_log_file} >> /dev/null
	@rm -f -r ${src_dir}/*.pyc >> /dev/null

# action targets

compile:
	@echo "Compiling source code..."
	@python -m compileall ${src_dir}

unit: compile
	@echo "Running unit tests..."
	@nosetests -d -s --verbose --with-coverage --cover-erase --cover-package=libmagic tests/unit

func: compile
	@echo "Running functional tests..."
	@nosetests -d -s --verbose --with-coverage --cover-erase --cover-package=libmagic tests/functional

run:
	${app_server} --debug src/

rundb:
	${app_server} --clear_datastore src/

upload:
	${app_cfg} update src/

