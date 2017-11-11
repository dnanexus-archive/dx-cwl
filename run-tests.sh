#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

dx login --token $DXTOKEN --noprojects
dx rmproject -y cwltests || true
dx new project -s cwltests

DXPROJ=`dx env | grep --color=never project- | cut -f2`

## BASICS

## Upload all test files to the temporary project

dx upload -r tests

# Run a simple help command
./dx-cwl -h

## CORE INTEGRATION TESTS (eventually run GNU parallel)
#./dx-cwl compile-workflow tests/md5sum/md5sum.cwl --token $DXTOKEN --project $DXPROJ
#./dx-cwl run-workflow dx-cwl-run/md5sum/md5sum /tests/md5sum/md5sum.cwl.json --token $DXTOKEN --project $DXPROJ --wait

## A bunch of example tests

## bcbio

## CWL CONFORMANCE TESTS (after completing core integration tests)


rm -rf common-workflow-language
git clone https://github.com/common-workflow-language/common-workflow-language.git
cd common-workflow-language
dx upload -r v1.0/v1.0
chmod 777 run_test.sh
rm -f commands.txt
for testnum in 21; do
  echo "./run_test.sh -n${testnum} RUNNER=$DIR/dx-cwl-runner" >> commands.txt
done

parallel --joblog joblog.txt < commands.txt
# Print results
awk '$7 == 0 {print "PASSED " $0} $7 == 1 {print "FAILED " $0} NR == 1 {print "     " $0}' joblog.txt || true
/drone/src/github.com/dnanexus/dx-cwl/dx-cwl-runner --outdir=/tmp/tmpRd0M6B --quiet v1.0/count-lines1-wf.cwl v1.0/wc-job.json
cd ..

dx rmproject -y $DXPROJ


