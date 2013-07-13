# -*- coding: utf-8 -*-
import logging
import pymongo

from tornado.options import options


def configure_mongolog():
    """This method use a sync connection via PyMongo because the Python's
    logging module is blocking. However we set the write concern to 0 for no
    expecting a result."""
    client = pymongo.MongoClient(options.logging_db_uri, w=0)

    from mongolog.handlers import MongoHandler
    col = client[options.logging_db_name][options.logging_db_collection]
    logging.getLogger().addHandler(MongoHandler.to(collection=col))