FROM centos:centos7
MAINTAINER Andy Goldstein <agoldste@redhat.com>

# Update installed packages and install dependencies
RUN yum update -y && yum clean all
RUN yum install -y epel-release && yum clean all
RUN yum install -y python-pip \
                   python-devel \
                   python-backports-lzma \
                   python-boto \
                   python-redis \
                   python-blinker \
                   python-flask \
                   python-gevent \
                   unzip \
                   gcc && \
    yum clean all

# Download the registry source
RUN curl -L -O https://github.com/openshift/docker-registry/archive/master.zip

# Unpack it
RUN unzip master.zip
RUN mv /docker-registry-master /docker-registry

# Install boto.cfg
RUN cp /docker-registry/config/boto.cfg /etc/boto.cfg

# Install core
RUN pip install /docker-registry/depends/docker-registry-core

# Install registry
RUN pip install file:///docker-registry/#egg=docker-registry[bugsnag,newrelic]

# Add our extensions
ADD . /openshift-docker-registry-extensions

# Install our extensions
RUN pip install /openshift-docker-registry-extensions

# Set up default setting
ENV DOCKER_REGISTRY_CONFIG /openshift-docker-registry-extensions/config_openshift.yml
ENV SETTINGS_FLAVOR dev

EXPOSE 5000

CMD exec docker-registry
