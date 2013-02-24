# -*- coding: utf-8 *-*
import datetime
import tornado.web

from selene import helpers
from selene.handlers import BaseHandler
from tornado.options import options


class HomeHandler(BaseHandler):

    def get(self):
        posts = self.db.posts.find({'status': 'published'}).sort('date', -1)
        self.render("home.html", posts=posts)


class NewPostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render('newpost.html', message='', post={}, new=True)

    @tornado.web.authenticated
    def post(self):
        slug_flag = self.get_argument('slug', False)
        if slug_flag:
            slug = self.get_argument('customslug', '')
        else:
            slug = helpers.get_slug(self.get_argument('title'))
        post = {
            'title': self.get_argument('title'),
            'slug': slug,
            'date': datetime.datetime.now(),
            'tags': helpers.remove_duplicates(self.get_argument('tags')),
            'content': self.get_argument('content'),
            'status': self.get_argument('status'),
            'author': self.current_user['name'],
            'votes': 0,
            'views': 0
        }
        self.db.posts.insert(post)
        self.redirect('/post/%s' % post['slug'])


class PostHandler(BaseHandler):

    def get(self, slug_post):
        post = self.db.posts.find_and_modify({'slug': slug_post,
            'status': 'published'}, update={'$inc': {'views': 1}}, new=True)
        if not post:
            raise tornado.web.HTTPError(404)
        comments = list(self.db.comments.find({'postid': post['_id']}))
        self.render('post.html', post=post, comments=comments)


class EditPostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, slug):
        post = self.db.posts.find_one({'slug': slug})
        if not post:
            raise tornado.web.HTTPError(404)
        self.render("newpost.html", message='', post=post, new=False)

    @tornado.web.authenticated
    def post(self, slug):
        new_post = {
            'title': self.get_argument('title'),
            'tags': helpers.remove_duplicates(self.get_argument('tags')),
            'content': self.get_argument('content'),
            'status': self.get_argument('status')
        }
        self.db.posts.update({'slug': slug}, {'$set': new_post})
        self.redirect('/post/%s' % slug)


class DeletePostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, slug):
        post = self.db.posts.find_one({'slug': slug}, {'title': 1, 'slug': 1})
        self.render("deletepost.html", post=post)

    @tornado.web.authenticated
    def post(self, slug):
        post = self.db.posts.find({'slug': slug})
        if not post:
            raise tornado.web.HTTPError(404)
        self.db.posts.remove({'slug': slug})
        self.redirect('/posts')


class VotePostHandler(BaseHandler):

    def post(self, slug):
        post = self.db.posts.find({'slug': slug})
        if not post:
            raise tornado.web.HTTPError(404)
        self.db.posts.update({'slug': slug}, {'$inc': {'votes': 1}})
        self.redirect('/post/%s' % slug)


class PostsHandlers(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        posts = self.db.posts.find().sort('date', -1)
        self.render("posts.html", posts=posts)


class TagHandler(BaseHandler):

    def get(self, tag):
        posts = self.db.posts.find({'tags': tag}).sort('date', -1)
        if not posts.count():
            raise tornado.web.HTTPError(404)
        self.render('tag.html', tag=tag, posts=posts)


class RssHandler(BaseHandler):

    def get(self):
        self.set_header("Content-Type", "text/xml; charset=UTF-8")
        self.render("rss.xml",
            posts=self.db.posts.find().sort("date", -1).limit(10),
            options=options)


class NewCommentHandler(BaseHandler):

    def post(self, slug):
        post_id = self.db.posts.find_one({'slug': slug}, {'_id': 1})['_id']
        self.db.comments.insert({'postid': post_id,
                                 'name': self.get_argument('name'),
                                 'email': self.get_argument('email'),
                                 'content': self.get_argument('content'),
                                 'date': datetime.datetime.now()})
        self.redirect('/post/%s' % slug)
