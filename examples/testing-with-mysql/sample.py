# -*- coding: utf-8 -*-
import json
from contextlib import closing

import docktors
import logging
import MySQLdb

logging.basicConfig(
    format='[%(name)s][%(asctime)s][%(levelname)s] %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%dT%I:%M:%S'
)
logger = logging.getLogger(__name__)


def mysql_main(user='root', password='', database='mysql', host='127.0.0.1', port=3306):
    db = MySQLdb.connect(host=host, port=port, user=user, password=password, database=database)
    with closing(db.cursor()) as cursor:
        cursor.execute(query='SHOW TABLES')
        result = [i[0] for i in cursor.fetchall()]
        logger.info('Show tables result : %s', json.dumps(result, indent=2))


if __name__ == '__main__':
    mysql_main(password='s3cr3t')
