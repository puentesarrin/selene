from email.utils import format_datetime
from xml.sax.saxutils import escape

from tornado.options import options

import selene
from selene.constants import PostStatus
from selene.web import BaseHandler


class RSSHandler(BaseHandler):
    async def get(self):
        self.set_header('Content-Type', 'application/rss+xml; charset=utf-8')
        posts = (
            await self.db.posts.find({'status': PostStatus.PUBLISHED.value}).sort('date', -1).limit(10).to_list(None)
        )
        await self.render('rss.xml', posts=posts)


class AtomHandler(BaseHandler):
    async def get(self):
        posts = (
            await self.db.posts.find({'status': PostStatus.PUBLISHED.value}).sort('date', -1).limit(10).to_list(None)
        )
        updated = posts[0]['date'] if posts else None
        entries = []
        for post in posts:
            url = f'{options.base_url.rstrip("/")}{self.reverse_url("post", post["slug"])}'
            entry = f'''
  <entry>
    <title>{escape(post['title'])}</title>
    <link href="{escape(url)}"/>
    <id>{escape(url)}</id>
    <updated>{format_datetime(post['date'])}</updated>
    <author><name>{escape(post.get('author') or '')}</name></author>
    <content type="html">{escape(post.get('html_content') or '')}</content>
  </entry>'''
            entries.append(entry)
        feed = f'''<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{escape(options.title)}</title>
  <link href="{escape(options.base_url.rstrip('/') + self.reverse_url('atom'))}" rel="self"/>
  <link href="{escape(options.base_url)}"/>
  <id>{escape(options.base_url)}</id>
  <generator uri="https://github.com/puentesarrin/selene" version="{escape(selene.version)}">Selene</generator>
  <updated>{format_datetime(updated) if updated else ''}</updated>{''.join(entries)}
</feed>'''
        self.set_header('Content-Type', 'application/atom+xml; charset=UTF-8')
        self.write(feed)
