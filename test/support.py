from types import SimpleNamespace

from bson.objectid import ObjectId
from tornado.options import Error, options

from selene import options as selene_options
from selene.constants import TextType


def ensure_options():
    try:
        selene_options.define_options()
    except Error:
        pass
    options.cookie_secret = 'test-cookie-secret'
    options.themes_directory = 'themes'
    options.selected_theme = 'default'
    options.default_locale = 'en_US'
    options.default_language = 'en_US'
    options.debug = False
    options.static_url_prefix = None
    options.google_login_enabled = False
    options.google_oauth_key = None
    options.google_oauth_secret = None
    options.facebook_login_enabled = False
    options.facebook_api_key = None
    options.facebook_secret = None
    options.twitter_login_enabled = False
    options.twitter_consumer_key = None
    options.twitter_consumer_secret = None
    options.recent_posts_limit = 10
    options.recent_comments_limit = 10
    options.tag_cloud_limit = 20
    options.gravatar_for_posts = False
    options.gravatar_for_comments = False
    options.page_size_posts = 10
    options.page_size_tag_posts = 10
    options.page_size_search_posts = 10
    options.base_url = 'http://localhost'
    options.title = 'Selene'
    options.slogan = 'A simple CMS for blogging built with Tornado and MongoDB'
    options.allowed_text_types = [text_type.value for text_type in TextType]


def matches(document, query):
    for key, expected in query.items():
        if key == '$or':
            if not any(matches(document, item) for item in expected):
                return False
            continue
        if key == '$and':
            if not all(matches(document, item) for item in expected):
                return False
            continue
        value = document.get(key)
        if hasattr(expected, 'search'):
            if not expected.search(value or ''):
                return False
        elif isinstance(expected, dict):
            if '$lt' in expected and not (value < expected['$lt']):
                return False
            if '$gt' in expected and not (value > expected['$gt']):
                return False
            if '$text' in expected:
                continue
        elif value != expected:
            return False
    return True


class FakeCursor:
    def __init__(self, documents):
        self.documents = list(documents)
        self.start = 0
        self.stop = None

    def sort(self, key, direction):
        reverse = direction < 0
        self.documents.sort(key=lambda item: item.get(key), reverse=reverse)
        return self

    def skip(self, count):
        self.start = count
        return self

    def limit(self, count):
        self.stop = self.start + count
        return self

    async def to_list(self, length=None):
        stop = self.stop
        if length is not None:
            stop = self.start + length
        return list(self.documents[self.start : stop])


class FakeCollection:
    def __init__(self, documents=None):
        self.documents = list(documents or [])

    def find(self, query=None, projection=None):
        query = query or {}
        return FakeCursor([doc.copy() for doc in self.documents if matches(doc, query)])

    async def find_one(self, query=None, projection=None):
        query = query or {}
        for doc in self.documents:
            if matches(doc, query):
                return doc.copy()
        return None

    async def count_documents(self, query=None):
        query = query or {}
        return len([doc for doc in self.documents if matches(doc, query)])

    async def aggregate(self, pipeline):
        return FakeCursor([])

    async def create_index(self, keys):
        return 'idx'

    async def insert_one(self, document):
        document = document.copy()
        document.setdefault('_id', ObjectId())
        self.documents.append(document)
        return SimpleNamespace(inserted_id=document['_id'])

    async def update_one(self, query, update):
        matched = 0
        for doc in self.documents:
            if matches(doc, query):
                matched = 1
                if '$set' in update:
                    doc.update(update['$set'])
                if '$inc' in update:
                    for key, value in update['$inc'].items():
                        doc[key] = doc.get(key, 0) + value
                break
        return SimpleNamespace(matched_count=matched)

    async def delete_one(self, query):
        return SimpleNamespace(deleted_count=0)

    async def delete_many(self, query):
        return SimpleNamespace(deleted_count=0)

    async def find_one_and_update(self, query, update, **kwargs):
        for doc in self.documents:
            if matches(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                if '$inc' in update:
                    for key, value in update['$inc'].items():
                        doc[key] = doc.get(key, 0) + value
                if kwargs.get('return_document'):
                    return doc.copy()
                return doc.copy()
        return None


class FakeDB:
    def __init__(self):
        self.posts = FakeCollection()
        self.comments = FakeCollection()
        self.users = FakeCollection()
        self.settings = FakeCollection()
        self.client = SimpleNamespace(admin=SimpleNamespace(command=self.command))

    async def command(self, *args, **kwargs):
        return {}
