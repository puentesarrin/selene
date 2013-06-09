# -*- coding: utf-8 -*-
import logging
import pymongo

from tornado.options import options


def configure_mongolog():
    client = pymongo.MongoClient(options.logging_db_uri, w=0)

    from mongolog.handlers import MongoHandler
    col = client[options.logging_db_name][options.logging_db_collection]
    logging.getLogger().addHandler(MongoHandler.to(collection=col))