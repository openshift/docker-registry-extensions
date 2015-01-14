import json
import logging

import requests

from docker_registry.lib import config
import docker_registry.lib.signals
from docker_registry import storage
from docker_registry import tags

logger = logging.getLogger(__name__)

logger.info("Loading OpenShift tag_created extension")

cfg = config.load()
store = storage.load()

openshift_url = None
openshift_insecure = False
openshift_ca_bundle = None
openshift_client_cert = None
openshift_client_key = None
registry_url = None

if cfg.extensions is not None and cfg.extensions.openshift is not None:
    cfg = cfg.extensions.openshift

    openshift_url = cfg.openshift_url
    logger.info("OpenShift URL: {0}".format(openshift_url))

    openshift_insecure = cfg.openshift_insecure
    logger.info("OpenShift insecure: {0}".format(openshift_insecure))

    openshift_ca_bundle = cfg.openshift_ca_bundle
    logger.info("OpenShift CA bundle: {0}".format(openshift_ca_bundle))

    openshift_client_cert = cfg.openshift_client_cert
    logger.info("OpenShift client certificate: {0}".format(openshift_client_cert))

    openshift_client_key = cfg.openshift_client_key
    logger.info("OpenShift client key: {0}".format(openshift_client_key))

    if cfg.registry_url is not None:
        registry_url = cfg.registry_url
    logger.info("Registry URL: {0}".format(registry_url))


def tag_created(sender, namespace, repository, tag, value):
    logger.debug("[openshift] namespace={0}; repository={1} tag={2} value={3}".
                 format(namespace, repository, tag, value))
    try:
        if tag != value:
            store.put_content(
                store.tag_path(namespace, repository, value), value)

            data = tags.create_tag_json(user_agent='')
            json_path = store.repository_tag_json_path(namespace, repository, value)
            store.put_content(json_path, data)

        data = store.get_content(store.image_json_path(value))
        image = json.loads(data)
        _post_repository_binding(namespace, repository, tag, value, image)
    except Exception:
        logger.exception("unable to create openshift ImageRepositoryMapping")


def _post_repository_binding(namespace, repository, tag, image_id, image):
    url = '{0}/imageRepositoryMappings'.format(openshift_url)
    params = {"sync": "true", "namespace": namespace}
    headers = {}
    # headers = {'Authorization': self.authorization}

    name = "{0}/{1}/{2}".format(registry_url, namespace, repository).strip('/')
    ref = "{0}:{1}".format(name, image_id)
    body = {
        "kind": "ImageRepositoryMapping",
        "apiVersion": "v1beta1",
        "metadata": {
            "name": repository,
            "namespace": namespace,
        },
        "dockerImageRepository": name,
        "image": {
            "metadata": {
                "name": image_id,
            },
            "dockerImageReference": ref,
            "dockerImageMetadata": {
                "Id": image['id'],
                "Parent": image.get('parent', ''),
                "Comment": image.get('comment', ''),
                "Created": image.get('created', ''),
                "Container": image.get('container', ''),
                "ContainerConfig": image.get('container_config', ''),
                "DockerVersion": image.get('docker_version', ''),
                "Author": image.get('author', ''),
                "Config": image.get('config', ''),
                "Architecture": image.get('architecture', ''),
                "Size": image.get('Size', ''),
            }
        },
        "tag": tag
    }
    logger.debug("saving\n" + json.dumps(body))

    postArgs = {
        'params': params,
        'headers': headers,
        'data': json.dumps(body),
    }

    if openshift_ca_bundle is not None:
        postArgs["verify"] = openshift_ca_bundle
    elif openshift_insecure:
        postArgs["verify"] = False
    else:
        postArgs["verify"] = True

    if openshift_client_cert is not None and openshift_client_key is not None:
        postArgs["cert"] = (openshift_client_cert, openshift_client_key)
    elif openshift_client_cert is not None:
        postArgs["cert"] = openshift_client_cert

    resp = requests.post(url, **postArgs)

    if resp.status_code == 422:
        logger.debug('openshift#_post_repository_binding: invalid request: %s' % resp.text)
        return False

    if resp.status_code != 200:
        logger.debug('openshift#_post_repository_binding: update returns status {0}\n{1}'.  # nopep8
                     format(resp.status_code, resp.text))
        return False

    return True

if openshift_url is not None and registry_url is not None:
    docker_registry.lib.signals.tag_created.connect(tag_created)
    logger.info("OpenShift tag_created extension enabled")
else:
    logger.info("OpenShift tag_created extension disabled - missing openshift_url and/or registry_url")
