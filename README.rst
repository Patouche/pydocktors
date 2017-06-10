==========
pydocktors
==========

.. image:: https://travis-ci.org/Patouche/pydocktors.svg?branch=developpment
    :target: https://travis-ci.org/Patouche/pydocktors
.. image:: https://codecov.io/gh/Patouche/pydocktors/branch/developpment/graph/badge.svg
    :target: https://codecov.io/gh/Patouche/pydocktors
.. image:: https://img.shields.io/pypi/v/pydocktors.svg
    :target: https://pypi.python.org/pypi/pydocktors

------------
What is it ?
------------

On top of docker, pydocktors is a simple way to declare a decorator to start and shutdown a docker container.

---------------
Why to use it ?
---------------

You can use it anywhere you want in your python code ! This include test and code...

For example, if you have a application that require a database (for example, MySQL or Neo4J) but you don't want to install the database globally on your system, you can use the docker decorator !

Or you may need to load a application such as Nginx or Eureka when running your code locally without installing it, this docker decorator is made for you !

--------
Examples
--------

All of them are also available in the `examples <./examples/README.md>`_. Each example are designed to be independent.

Starting a Nginx with a your content and your configuration::

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
        logger.info('Nginx container with id %s is %s. Visit http://localhost:8080/', container.id, container.status)

FAQ
---

*Why this name ?*

Because it's the contraction of 3 famous words : *python*, *docker* and *decorators*

**Authors :** Patrick Allain
**License :** MIT
