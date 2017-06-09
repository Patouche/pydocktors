pydoctors
=========

[![Build Status](https://travis-ci.org/Patouche/pydoctors.svg?branch=developpment)](https://travis-ci.org/Patouche/pydoctors)
[![Coverage](https://codecov.io/gh/Patouche/pydoctors/branch/developpment/graph/badge.svg)](https://codecov.io/gh/Patouche/pydoctors)


## What is it ?

On top of docker, pydoctors is a simple way to declare a decorator to start and shutdown a docker container.

## How to use it ?

You can use it anywhere you want in your python code ! This include test and code... For example, if you have a application that require a database (for example, MySQL or Neo4J) but you don't want to install the database globally on your system, you can use the docker decorator ! Or you may need to load a application such as Nginx or Eureka when running your code locally without installing it, the docker decorator is made for you ! 

```python
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
```

## FAQ

### Why this name ?

Because it's the contraction of 3 famous words : `python`, `docker` and `decorators`

LICENSE : MIT
