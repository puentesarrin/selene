import asyncio
import logging

from pymongo import AsyncMongoClient
from tornado.options import options as opts

from selene import Selene, log, options


async def main():
    options.setup_options('selene.conf')
    if opts.logging_db:
        log.configure_mongolog()

    client = AsyncMongoClient(opts.db_uri)
    db = client[opts.db_name]
    logging.info('Connected to MongoDB.')

    app = Selene(db)
    app.listen(opts.port)
    logging.info(f'Web server listening on {opts.port} port.')
    await asyncio.Event().wait()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Exiting with keyboard interrupt.')
