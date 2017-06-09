# -*- coding: utf-8 -*-
import calendar
import hashlib
import logging
import os
import time

import datetime
import markdown2
from jinja2 import Template

import docktors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('nginx-sample')

# The source content of the static web site
SOURCE_DIR = os.path.join(os.path.dirname(__file__), 'content')

# The target directory where will be mount the nginx volume
TARGET_DIR = os.path.join(os.path.dirname(__file__), '.tmp')

# In the nginx.conf, we just define .md file to be serve as html
NGINX_CONF = os.path.join(os.path.dirname(__file__), 'nginx.conf')

# The second to wait between 2 refresh
REFRESH_DELAY = 5

# The Jinja template to wrap markdown content
TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{{title}}</title>
    <link media="all" rel="stylesheet" href="/default.css" />
  </head>
  <body>{{content}}</body>
</html>
""")

# Prevent docker creating file as root
if not os.path.exists(TARGET_DIR):
    os.mkdir(TARGET_DIR)


def sha256_checksum(filename):
    """
    Calculate the sha256 of a file.
    """
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        [sha256.update(block) for block in iter(lambda: f.read(65536), b'')]
    return sha256.hexdigest()


def generate_site(path, files_checksum):
    """
    Recursive function to create html file from markdown file
    with the same directory tree.
    """

    files_checksum = dict() if files_checksum is None else files_checksum

    src_abs = os.path.normpath(os.path.join(SOURCE_DIR, path))
    if not os.path.exists(src_abs):
        raise SyntaxError("Path {path} doesn't exist".format(path=src_abs))

    target_abs = os.path.normpath(os.path.join(TARGET_DIR, path))
    if os.path.isdir(src_abs):
        if not os.path.exists(target_abs):
            logger.debug('Creating directory %s', target_abs)
            os.mkdir(target_abs)
        [generate_site(os.path.join(path, f), files_checksum) for f in os.listdir(src_abs)]
        return files_checksum

    checksum = sha256_checksum(src_abs)
    if checksum != files_checksum.get(src_abs):
        with open(src_abs, 'ro') as stream:
            content = stream.read()

        if src_abs.endswith('.md'):
            content = markdown2.markdown(content, extras=["fenced-code-blocks"])
            content = TEMPLATE.render(
                title=os.path.basename(target_abs),
                content=content
            )

        with open(target_abs, 'wb') as stream:
            stream.write(content)

        logger.info('File has been generated : %s', target_abs)

    files_checksum[src_abs] = checksum

    return files_checksum


@docktors.docker(
    inject_arg=True,
    image='nginx',
    ports=[(80, 8080)],
    volumes=[
        (TARGET_DIR, '/usr/share/nginx/html', 'ro'),
        (NGINX_CONF, '/etc/nginx/nginx.conf', 'ro')
    ],
    wait_for_port=8080,
)
def main(container):
    logger.info('Nginx container with id %s is %s. Open in your browser http://localhost:8080/',
                container.id, container.status)
    files_sha256 = None
    while True:
        files_sha256 = generate_site(path='.', files_checksum=files_sha256)
        time.sleep(REFRESH_DELAY)


if __name__ == '__main__':
    main()

