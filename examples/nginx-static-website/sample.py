# -*- coding: utf-8 -*-
import logging
import docktors

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('nginx-sample')


@docktors.docker(
    inject_arg=True,
    image='nginx'
)
def main(docker):
    logger.info('Nginx container with id %s is %s', docker.container.id, docker.container.status)


if __name__ == '__main__':
    main()
