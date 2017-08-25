FROM ubuntu:14.04

# Basic package dependencies installs
RUN apt-get update && apt-get install -y python-pip python-dev wget && \
    pip install cwltool PyYAML

# Get and install dx-toolkit
RUN wget https://wiki.dnanexus.com/images/files/dx-toolkit-v0.230.0-ubuntu-14.04-amd64.tar.gz && \
    tar -xzf dx-toolkit-v0.230.0-ubuntu-14.04-amd64.tar.gz

ENV PATH /dx-toolkit/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV PYTHONPATH /dx-toolkit/share/dnanexus/lib/python2.7/site-packages:/dx-toolkit/lib/python:
ENV CLASSPATH /dx-toolkit/lib/java/*:
ENV DNANEXUS_HOME /dx-toolkit

# Set up compiler resources

ADD dx-cwl /
ADD dx-cwl-applet-code.py /
ADD get-cwltool.sh /
ADD resources/ /resources

RUN ./get-cwltool.sh

ENTRYPOINT ["python", "dx-cwl"]
