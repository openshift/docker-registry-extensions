#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools

setuptools.setup(
    name  = "openshift-docker-registry-extensions",
    version = "0.1",
    description = "OpenShift Docker Registry Extensions",
    long_description = open('./README.md').read(),
    author = "OpenShift",
    author_email = "openshift@redhat.com",
    url = "http://openshift.com",
    license = open('./LICENSE').read(),

    classifiers = [
      'Development Status :: 3 - Alpha',
      'Topic :: Utilities',
      'License :: OSI Approved :: Apache Software License'
    ],

    entry_points = {
      'docker_registry.extensions': [
        'tag_created = openshift.tag_created'
      ]
    },

    packages = ['openshift'],

    install_requires=['docker-registry-core>=2,<3'],
)
