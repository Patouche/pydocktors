# -*- coding: utf-8 -*-
import logging
import os
import time
import markdown2
from jinja2 import Template

import docktors

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('nginx-sample')

SOURCE_DIR = os.path.join(os.path.dirname(__file__), 'content')
TARGET_DIR = os.path.join(os.path.dirname(__file__), '.site')
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


def generate_site(path):
    """
    Recursive function to create html file from markdown file
    with the same directory tree
    """
    src_abs = os.path.join(SOURCE_DIR, path)
    if not os.path.exists(src_abs):
        raise SyntaxError("Path {path} doesn't exist".format(path=src_abs))

    target_abs = os.path.join(TARGET_DIR, path)
    if os.path.isdir(src_abs):
        if not os.path.exists(target_abs):
            logger.info('Creating directory %s', target_abs)
            os.mkdir(target_abs)
        return [generate_site(os.path.join(path, f)) for f in os.listdir(src_abs)]

    logger.info("Parsing : %s", src_abs)
    with open(src_abs, 'ro') as stream:
        content = stream.read()

    if src_abs.endswith('.md'):
        target_abs = os.path.splitext(target_abs)[0] + '.html'
        content = markdown2.markdown(content, extras=["fenced-code-blocks"])
        content = TEMPLATE.render(
            title=os.path.basename(target_abs),
            content=content
        )

    with open(target_abs, 'wb') as stream:
        stream.write(content)

    logger.info('Generated file : %s', target_abs)


@docktors.docker(
    inject_arg=True,
    image='nginx',
    ports=[(80, 8080)],
    volumes=[(TARGET_DIR, '/usr/share/nginx/html', 'ro')],
    wait_for_port=8080,
)
def main(container):
    while True:
        logger.info('Nginx container with id %s is %s. Open in your browser http://localhost:8080/',
                    container.id, container.status)
        generate_site(path='.')
        time.sleep(5)


if __name__ == '__main__':
    main()
