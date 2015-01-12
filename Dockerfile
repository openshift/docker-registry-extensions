FROM centos:centos7
MAINTAINER Andy Goldstein <agoldste@redhat.com>

# Set up default settings
ENV DOCKER_REGISTRY_CONFIG /openshift-docker-registry-extensions/config_openshift.yml
ENV SETTINGS_FLAVOR dev

EXPOSE 5000

CMD exec docker-registry

ADD . /openshift-docker-registry-extensions

# Update installed packages and install dependencies
RUN yum update -y && \
    yum install -y epel-release && \
    yum install -y python-pip \
                   python-devel \
                   python-boto \
                   python-redis \
                   python-blinker \
                   python-flask \
                   c-ares \
                   libev \
                   python-greenlet \
                   unzip \
                   xz-devel \
                   gcc && \
    curl -L -O https://github.com/openshift/docker-registry/archive/master.zip && \
    unzip master.zip && \
    rm -f master.zip && \
    mv /docker-registry-master /docker-registry && \
    cp /docker-registry/config/boto.cfg /etc/boto.cfg && \
    pip install /docker-registry/depends/docker-registry-core && \
    pip install file:///docker-registry/#egg=docker-registry[bugsnag,newrelic] && \
    rm -rf /docker-registry && \
    pip install /openshift-docker-registry-extensions && \
    yum remove -y epel-release \
                  python-devel \
                  unzip \
                  gcc cpp glibc-devel glibc-headers kernel-headers libmpc mpfr && \
    yum clean all && \
    rm -rf /tmp/pip*
