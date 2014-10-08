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
registry_url = None

if cfg.extensions is not None and cfg.extensions.openshift is not None:
    cfg = cfg.extensions.openshift

    openshift_url = cfg.openshift_url
    logger.info("OpenShift URL: {0}".format(openshift_url))

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
    params = {"sync": "true"}
    headers = {}
    # headers = {'Authorization': self.authorization}

    name = "{0}/{1}/{2}".format(registry_url, namespace, repository).strip('/')
    ref = "{0}:{1}".format(name, image_id)
    body = {
        "kind": "ImageRepositoryMapping",
        "version": "v1beta1",
        "dockerImageRepository": name,
        "image": {
            "id": image_id,
            "dockerImageReference": ref,
            "metadata": {
                "Id": image['id'],
                "Parent": image['parent'] if 'parent' in image else '',
                "Comment": image['comment'] if 'comment' in image else '',
                "Created": image['created'] if 'created' in image else '',
                "Container": image['container'] if 'container' in image else '',
                "ContainerConfig": image['container_config'] if 'container_config' in image else '',
                "DockerVersion": image['docker_version'] if 'docker_version' in image else '',
                "Author": image['author'] if 'author' in image else '',
                "Config": image['config'] if 'config' in image else '',
                "Architecture": image['architecture'] if 'architecture' in image else '',
                "Size": image['Size'] if 'Size' in image else ''
            }
        },
        "tag": tag
    }
    logger.debug("saving\n" + json.dumps(body))

    resp = requests.post(url, params=params, verify=True, headers=headers,
                         data=json.dumps(body))

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
