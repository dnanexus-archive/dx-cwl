#!/bin/bash -e

apt-get update
apt-get install -y wget git make python-setuptools python-pip python-virtualenv python-dev g++ cmake libboost1.55-all-dev libcurl4-openssl-dev zlib1g-dev libbz2-dev flex bison autoconf curl parallel

pip install cwltool PyYAML

# Obtain and install the latest stable toolkit
git clone https://github.com/dnanexus/dx-toolkit.git
cd dx-toolkit && git checkout stable && make python dx-docker && cd ..
