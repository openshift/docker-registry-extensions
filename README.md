OpenShift Docker Registry Extensions
====================================

This is the source repository for OpenShift's extensions to the [Docker Registry](https://github.com/docker/docker-registry).

Extensions
----------

### Tag Created
Notifies OpenShift about the new image (tag and metadata). Also automatically adds a tag that matches the image's ID, to support pull-by-id.


Dockerfile
----------
Basis for a CentOS 7 Docker image that combines the Docker Registry with these OpenShift-specific extensions.


Running
-------
To run the registry with the OpenShift extensions, you must at least specify the URL to the OpenShift API Server. The easiest way to do so is to specify the `OPENSHIFT_URL` environment variable when running the registry. For example:

    docker run -e OPENSHIFT_URL=http://some.server/osapi/v1beta1 -p 5000:5000 openshift/docker-registry

Alternatively, you can edit the configuration file, modify the `extensions.openshift.openshift_url` setting, and run as follows:

    docker run -e DOCKER_REGISTRY_CONFIG=/path/to/config/in/container \
               -v `pwd`/config_openshift.yml:/path/to/config/in/container \
               -p 5000:5000 \
               openshift/docker-registry

When the registry sends OpenShift information about a new image and tag, it also needs to tell OpenShift which registry it is. You must set the `REGISTRY_URL` environment variable appropriately. For example, if you were to tag your image as `some.registry:5000/namespace/repo:latest`, you would need to set `REGISTRY_URL` to `some.registry:5000`. If not set, it defaults to `localhost:5000`. This can be set in the same manner as `OPENSHIFT_URL` described above.

More information on the other configuration options is available on the [Docker Registry](https://github.com/docker/docker-registry) page.

License
-------
The files in this repository are licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).
