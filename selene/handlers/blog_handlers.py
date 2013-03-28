# -*- coding: utf-8 *-*
import datetime
import re
import tornado.gen
import tornado.web

from bson.objectid import ObjectId
from motor import Op
from selene import helpers
from selene.handlers import BaseHandler, authenticated_async
from tornado.options import options


class HomeHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, page=1):
        @tornado.gen.engine
        def find_comments(post, callback):
            post['comments'] = yield Op(self.db.comments.find({'postid':
                post['_id']}).to_list)
            callback(post)

        page = int(page)
        posts = yield Op(self.db.posts.find({'status': 'published'}).sort(
            'date', -1).skip((page - 1) * options.page_size_posts).limit(
                options.page_size_posts).to_list)
        for post in posts:
            find_comments(post, (yield tornado.gen.Callback(post['_id'])))
        posts = yield tornado.gen.WaitAll([post['_id'] for post in posts])
        total = yield Op(self.db.posts.find({'status': 'published'}).count)
        self.render("home.html", posts=posts, total=total, page=int(page),
            page_size=options.page_size_posts)


class NewPostHandler(BaseHandler):

    @authenticated_async
    def get(self):
        self.render('newpost.html', message='', post={}, new=True)

    @authenticated_async
    @tornado.gen.engine
    def post(self):
        slug_flag = self.get_argument('slug', False)
        if slug_flag:
            slug = self.get_argument('customslug', '')
        else:
            slug = helpers.get_slug(self.get_argument('title'))
        html_content, plain_content = helpers.get_html_and_plain(
            self.get_argument('content'), self.get_argument('text_type'))
        post = {
            'title': self.get_argument('title'),
            'slug': slug,
            'date': datetime.datetime.now(),
            'tags': helpers.remove_duplicates(self.get_argument('tags')),
            'text_type': self.get_argument('text_type'),
            'content': self.get_argument('content'),
            'html_content': html_content,
            'plain_content': plain_content,
            'status': self.get_argument('status'),
            'text_type': self.get_argument('text_type'),
            'author': self.current_user['name'],
            'votes': 0,
            'views': 0
        }
        existing_post = yield Op(self.db.posts.find_one, {'slug': slug},
            {'_id': 1})
        if existing_post:
            self.render('newpost.html', message=('There are already an '
                'existing post with this title or slug.'), post={}, new=True)
            return
        yield Op(self.db.posts.insert, post)
        if post['status'] == 'published':
            self.redirect('/post/%s' % post['slug'])
        else:
            self.redirect('/')


class PostHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, slug_post):
        post = yield Op(self.db.posts.find_and_modify, {'slug': slug_post,
            'status': 'published'}, update={'$inc': {'views': 1}}, new=True)
        if not post:
            raise tornado.web.HTTPError(404)

        comments = yield Op(self.db.comments.find({'postid':
            post['_id']}).to_list)
        older = None
        newer = None
        older_cursor = self.db.posts.find({'_id': {'$lt': post['_id']},
            'status': 'published'}).sort('date', -1).limit(1)
        newer_cursor = self.db.posts.find({'_id': {'$gt': post['_id']},
            'status': 'published'}).sort('date', 1).limit(1)
        while (yield older_cursor.fetch_next):
            older = older_cursor.next_object()
        while (yield newer_cursor.fetch_next):
            newer = newer_cursor.next_object()
        self.render('post.html', post=post, comments=comments, older=older,
            newer=newer)


class EditPostHandler(BaseHandler):

    @authenticated_async
    @tornado.gen.engine
    def get(self, slug):
        post = yield Op(self.db.posts.find_one, {'slug': slug})
        if not post:
            raise tornado.web.HTTPError(404)
        self.render("newpost.html", message='', post=post, new=False)

    @authenticated_async
    @tornado.gen.engine
    def post(self, slug):
        slug_flag = self.get_argument('slug', False)
        if slug_flag:
            new_slug = self.get_argument('customslug', '')
        else:
            new_slug = helpers.get_slug(self.get_argument('title'))
        html_content, plain_content = helpers.get_html_and_plain(
            self.get_argument('content'), self.get_argument('text_type'))
        new_post = {
            'title': self.get_argument('title'),
            'slug': new_slug,
            'tags': helpers.remove_duplicates(self.get_argument('tags')),
            'content': self.get_argument('content'),
            'html_content': html_content,
            'plain_content': plain_content,
            'status': self.get_argument('status'),
            'text_type': self.get_argument('text_type')
        }
        yield Op(self.db.posts.update, {'slug': slug}, {'$set': new_post})
        if new_post['status'] == 'published':
            self.redirect('/post/%s' % new_slug)
        else:
            self.redirect('/')


class DeletePostHandler(BaseHandler):

    @authenticated_async
    @tornado.gen.engine
    def get(self, slug):
        post = yield Op(self.db.posts.find_one, {'slug': slug},
            {'title': 1, 'slug': 1})
        self.render("deletepost.html", post=post)

    @authenticated_async
    @tornado.gen.engine
    def post(self, slug):
        post = yield Op(self.db.posts.find_one, {'slug': slug})
        if not post:
            raise tornado.web.HTTPError(404)
        self.db.comments.remove({'postid': post['_id']})
        self.db.posts.remove({'slug': slug})
        self.redirect('/posts')


class VotePostHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, slug):
        post = yield Op(self.db.posts.find({'slug': slug}).count)
        if not post:
            raise tornado.web.HTTPError(404)
        yield Op(self.db.posts.update, {'slug': slug}, {'$inc': {'votes': 1}})
        self.redirect('/post/%s' % slug)


class PostsHandlers(BaseHandler):

    @authenticated_async
    def get(self):
        title = self.get_argument('title', '')
        title_filter = re.compile('.*%s.*' % title, re.IGNORECASE)
        posts = self.db.posts.find({'title': title_filter}).sort('date', -1)
        self.render("posts.html", title=title, posts=posts)


class TagHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, tag, page=1):
        @tornado.gen.engine
        def find_comments(post, callback):
            post['comments'] = yield Op(self.db.comments.find, {'postid':
                post['_id']})
            callback(post)

        page = int(page)
        posts = self.db.posts.find({'tags': tag, 'status': 'published'}).sort(
            'date', -1).skip((page - 1) * options.page_size_posts).limit(
                options.page_size_tag_posts)
        if not posts.count():
            raise tornado.web.HTTPError(404)
        posts = map(find_comments, posts)
        total = yield Op(self.db.posts.find({'tags': tag,
            'status': 'published'}).count)
        self.render('tag.html', tag=tag, posts=posts, total=total, page=page,
            page_size=options.page_size_tag_posts)


class TagsHandlers(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        tags = yield Op(self.db.posts.aggregate, [
            {'$match': {'status': 'published'}},
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags', 'sum': {'$sum': 1}}},
            {'$sort': {'_id': 1}}
        ])
        self.render('tags.html', tags=tags['result'])


class SearchHandler(BaseHandler):

    def get(self):
        page = int(self.get_argument('page', 1))
        q = self.get_argument('q', '')
        if q:
            if not options.db_use_fts:
                q_filter = re.compile('.*%s.*' % q, re.IGNORECASE)
                posts = list(self.db.posts.find({'plain_content': q_filter,
                    'status': 'published'}).sort('date', -1).skip((page - 1) *
                    options.page_size_search_posts).limit(
                        options.page_size_search_posts))
                total = self.db.posts.find({'plain_content': q_filter,
                    'status': 'published'}).count()
            else:
                text_output = self.db.command("text", "posts", search=q,
                    filter={'status': 'published'})
                posts = [result['obj'] for result in text_output['results']]
                total = len(posts)
        else:
            posts = []
            total = 0
        self.render('search.html', posts=posts, q=q, total=total, page=page,
            page_size=options.page_size_search_posts)


class RssHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        posts = yield Op(self.db.posts.find().sort("date",
            -1).limit(10).to_list)
        self.set_header("Content-Type", "text/xml; charset=UTF-8")
        self.render("rss.xml", posts=posts, options=options)


class NewCommentHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, slug):
        post = yield Op(self.db.posts.find_one, {'slug': slug}, {'_id': 1})
        if not post:
            raise tornado.web.HTTPError(500)
        if not self.current_user:
            name = self.get_argument('name')
            email = self.get_argument('email')
        else:
            name = self.current_user['name']
            email = self.current_user['email']
        yield Op(self.db.comments.insert, {
            'postid': post['_id'], 'name': name, 'email': email,
            'content': self.get_argument('content'),
            'date': datetime.datetime.now(), 'likes': 0, 'dislikes': 0})
        self.redirect('/post/%s' % slug)


class LikeCommentHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, comment_id, action):
        if action not in ['like', 'dislike']:
            raise tornado.web.HTTPError(404)
        comment_id = ObjectId(comment_id)
        comment = yield Op(self.db.comments.find_and_modify,
            {'_id': comment_id}, fields={'postid': 1},
            update={'$inc': {action + 's': 1}}, new=True)
        if not comment:
            raise tornado.web.HTTPError(404)
        post = yield Op(self.db.posts.find_one, {'_id': comment['postid']})
        self.redirect('/post/%s' % post['slug'])


class EditCommentHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    @authenticated_async
    def get(self, comment_id):
        comment = yield Op(self.db.comments.find_one,
            {'_id': ObjectId(comment_id)})
        if not comment:
            raise tornado.web.HTTPError(404)
        post = yield Op(self.db.posts.find_one, {'_id': comment['postid']})
        self.render('editcomment.html', post=post, comment=comment)

    @tornado.web.asynchronous
    @tornado.gen.engine
    @authenticated_async
    def post(self, comment_id):
        comment = yield Op(self.db.comments.find_one,
            {'_id': ObjectId(comment_id)}, {'postid': 1})
        if not comment:
            raise tornado.web.HTTPError(404)
        yield Op(self.db.comments.update, {'_id': ObjectId(comment_id)}, {
            '$set': {
                'name': self.get_argument('name'),
                'email': self.get_argument('email'),
                'content': self.get_argument('content')
            }
        })
        post = yield Op(self.db.posts.find_one, {'_id': comment['postid']})
        self.redirect('/post/%s' % post['slug'])


class DeleteCommentHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    @authenticated_async
    def get(self, comment_id):
        comment = yield Op(self.db.comments.find_one,
            {'_id': ObjectId(comment_id)})
        if not comment:
            raise tornado.web.HTTPError(404)
        post = yield Op(self.db.posts.find_one, {'_id': comment['postid']})
        self.render('deletecomment.html', post=post, comment=comment)

    @tornado.web.asynchronous
    @tornado.gen.engine
    @authenticated_async
    def post(self, comment_id):
        comment = yield Op(self.db.comments.find_one,
            {'_id': ObjectId(comment_id)}, {'postid': 1})
        if not comment:
            raise tornado.web.HTTPError(404)
        post = yield Op(self.db.posts.find_one, {'_id': comment['postid']})
        yield Op(self.db.comments.remove, {'_id': ObjectId(comment_id)})
        self.redirect('/post/%s' % post['slug'])
