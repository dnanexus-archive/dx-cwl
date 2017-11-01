#!/bin/bash -e


dx login --token $DXTOKEN --noprojects
dx new project -s cwltests

DXPROJ=`dx env | grep --color=never project- | cut -f2`

## BASICS

## Upload all test files to the temporary project

dx upload -r tests

# Run a simple help command
./dx-cwl -h

## CORE INTEGRATION TESTS (eventually run GNU parallel)
./dx-cwl compile-workflow tests/md5sum/md5sum.cwl --token $DXTOKEN --project $DXPROJ
./dx-cwl run-workflow dx-cwl-run/md5sum/md5sum /tests/md5sum/md5sum.cwl.json --token $DXTOKEN --project $DXPROJ --wait


## CWL CONFORMANCE TESTS (after completing core integration tests)

## CLEANUP

dx rmproject -y $DXPROJ
