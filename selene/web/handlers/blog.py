# -*- coding: utf-8 *-*
import datetime
import re
import tornado.gen
import tornado.web

from bson.objectid import ObjectId
from motor import Op
from selene import helpers
from selene.web import authenticated_async, BaseHandler
from selene import constants, forms, helpers, options as opts, text
from selene.base import BaseHandler
from tornado.options import options


class HomeHandler(BaseHandler):

    @tornado.gen.engine
    @tornado.web.asynchronous
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
        self.render('newpost.html',
            form=forms.PostForm(locale_code=self.locale.code,
                status_choices=opts.STATUSES,
                text_type_choices=opts.get_allowed_text_types()))

    @authenticated_async
    @tornado.gen.engine
    def post(self):
        slug_flag = self.get_argument('slug', False)
        if slug_flag:
            slug = self.get_argument('customslug', '')
        else:
            slug = helpers.get_slug(self.get_argument('title'),
                stop_words=options.slug_stop_words)
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
            'email': self.current_user['email'],
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
            self.render('newpost.html', message=form.errors, form=form)


class PostHandler(BaseHandler):

    @tornado.gen.engine
    @tornado.web.asynchronous
    def get(self, slug_post):
        post = yield Op(self.db.posts.find_and_modify, {'slug': slug_post,
            'status': 'published'}, update={'$inc': {'views': 1}}, new=True)
        if not post:
            raise tornado.web.HTTPError(404)
<<<<<<< HEAD:selene/handlers/blog_handlers.py

        comments = yield Op(self.db.comments.find({'postid':
            post['_id']}).to_list)
        older = None
        newer = None
        older_cursor = self.db.posts.find({'_id': {'$lt': post['_id']},
=======
        comments = list(self.db.comments.find({'postid':
            post['_id']}).sort('date', 1))
        older = self.db.posts.find({'_id': {'$lt': post['_id']},
>>>>>>> master:selene/web/handlers/blog.py
            'status': 'published'}).sort('date', -1).limit(1)
        newer_cursor = self.db.posts.find({'_id': {'$gt': post['_id']},
            'status': 'published'}).sort('date', 1).limit(1)
<<<<<<< HEAD:selene/handlers/blog_handlers.py
        while (yield older_cursor.fetch_next):
            older = older_cursor.next_object()
        while (yield newer_cursor.fetch_next):
            newer = newer_cursor.next_object()
=======
        older = None if older.count() == 0 else older[0]
        newer = None if newer.count() == 0 else newer[0]
        data = {}
        if self.current_user:
            data.update({
                'name': self.current_user['full_name'],
                'email': self.current_user['email']
            })
        comment_form = forms.CommentForm(locale_code=self.locale.code, **data)
>>>>>>> master:selene/web/handlers/blog.py
        self.render('post.html', post=post, comments=comments, older=older,
            newer=newer, form_message=None, comment_form=comment_form)


class EditPostHandler(BaseHandler):

    @authenticated_async
    @tornado.gen.engine
    def get(self, slug):
<<<<<<< HEAD:selene/handlers/blog_handlers.py
        post = yield Op(self.db.posts.find_one, {'slug': slug})
=======
        post = self.db.posts.find_one({'slug': slug}, {'_id': 0})
>>>>>>> master:selene/web/handlers/blog.py
        if not post:
            raise tornado.web.HTTPError(404)
        post['tags'] = ','.join(post['tags'])
        form = forms.PostForm(locale_code=self.locale.code,
            status_choices=opts.STATUSES,
            text_type_choices=opts.get_allowed_text_types(), **post)
        self.render("editpost.html", form=form)

    @authenticated_async
    @tornado.gen.engine
    def post(self, slug):
<<<<<<< HEAD:selene/handlers/blog_handlers.py
        slug_flag = self.get_argument('slug', False)
        if slug_flag:
            new_slug = self.get_argument('customslug', '')
        else:
            new_slug = helpers.get_slug(self.get_argument('title'),
                stop_words=options.slug_stop_words)
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
=======
        form = forms.PostForm(self.request.arguments,
            locale_code=self.locale.code, status_choices=opts.STATUSES,
            text_type_choices=opts.get_allowed_text_types())
        if form.validate():
            if form.data['custom_slug']:
                slug = form.data['slug']
            else:
                slug = text.get_slug(form.data['title'],
                    stop_words=options.slug_stop_words)
            html_content, plain_content = text.get_html_and_plain(
                form.data['content'], form.data['text_type'])
            post = form.data
            post.update({
                'slug': slug,
                'tags': helpers.remove_duplicates(form.data['tags']),
                'html_content': html_content,
                'plain_content': plain_content,
            })
            self.db.posts.update({'slug': slug}, {'$set': post})
            if post['status'] == 'published':
                self.redirect(self.reverse_url('post', slug))
            else:
                self.redirect(self.reverse_url('home'))
>>>>>>> master:selene/web/handlers/blog.py
        else:
            self.render('editpost.html', message=form.errors, form=form)


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
        self.redirect(self.reverse_url('posts'))


class VotePostHandler(BaseHandler):

    @tornado.gen.engine
    @tornado.web.asynchronous
    def post(self, slug):
        post = yield Op(self.db.posts.find({'slug': slug}).count)
        if not post:
            raise tornado.web.HTTPError(404)
<<<<<<< HEAD:selene/handlers/blog_handlers.py
        yield Op(self.db.posts.update, {'slug': slug}, {'$inc': {'votes': 1}})
        self.redirect('/post/%s' % slug)
=======
        self.db.posts.update({'slug': slug}, {'$inc': {'votes': 1}})
        self.redirect(self.reverse_url('post', slug))
>>>>>>> master:selene/web/handlers/blog.py


class PostsHandlers(BaseHandler):

    @authenticated_async
    @tornado.gen.engine
    @tornado.web.asynchronous
    def get(self):
        title = self.get_argument('title', '')
        title_filter = re.compile('.*%s.*' % title, re.IGNORECASE)
        posts = yield Op(self.db.posts.find({'title':
            title_filter}).sort('date', -1).to_list)
        self.render("posts.html", title=title, posts=posts)


class TagHandler(BaseHandler):

    @tornado.gen.engine
    @tornado.web.asynchronous
    def get(self, tag, page=1):
        @tornado.gen.engine
        def find_comments(post, callback):
            post['comments'] = yield Op(self.db.comments.find({'postid':
                post['_id']}).to_list)
            callback(post)

        page = int(page)
        posts = yield Op(self.db.posts.find({'tags': tag,
            'status': 'published'}).sort('date', -1).skip(
                (page - 1) * options.page_size_posts).limit(
                    options.page_size_tag_posts).to_list)
        if not len(posts):
            raise tornado.web.HTTPError(404)
        for post in posts:
            find_comments(post, (yield tornado.gen.Callback(post['_id'])))
        posts = yield tornado.gen.WaitAll([post['_id'] for post in posts])
        total = yield Op(self.db.posts.find({'tags': tag,
            'status': 'published'}).count)
        self.render('tag.html', tag=tag, posts=posts, total=total, page=page,
            page_size=options.page_size_tag_posts)


class TagsHandlers(BaseHandler):

    @tornado.gen.engine
    @tornado.web.asynchronous
    def get(self):
        tags = yield Op(self.db.posts.aggregate, [
            {'$match': {'status': 'published'}},
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags', 'sum': {'$sum': 1}}},
            {'$sort': {'_id': 1}}
        ])
        self.render('tags.html', tags=tags['result'])


class SearchHandler(BaseHandler):

    @tornado.gen.engine
    @tornado.web.asynchronous
    def get(self):
        page = int(self.get_argument('page', 1))
        form = forms.SearchForm(locale_code=self.locale.code,
            q=self.get_argument('q', ''))
        if form.data['q']:
            if not options.db_use_fts:
<<<<<<< HEAD:selene/handlers/blog_handlers.py
                q_filter = re.compile('.*%s.*' % q, re.IGNORECASE)
                posts = yield Op(self.db.posts.find({'plain_content': q_filter,
=======
                q_filter = re.compile('.*%s.*' % form.data['q'], re.IGNORECASE)
                posts = list(self.db.posts.find({'plain_content': q_filter,
>>>>>>> master:selene/web/handlers/blog.py
                    'status': 'published'}).sort('date', -1).skip((page - 1) *
                    options.page_size_search_posts).limit(
                        options.page_size_search_posts).to_list)
                total = yield Op(self.db.posts.find({'plain_content': q_filter,
                    'status': 'published'}).count)
            else:
<<<<<<< HEAD:selene/handlers/blog_handlers.py
                text_output = yield Op(self.db.command, "text", "posts",
                    search=q, filter={'status': 'published'})
=======
                text_output = self.db.command("text", "posts",
                    search=form.data['q'], filter={'status': 'published'})
>>>>>>> master:selene/web/handlers/blog.py
                posts = [result['obj'] for result in text_output['results']]
                total = len(posts)
        else:
            posts = []
            total = 0
<<<<<<< HEAD:selene/handlers/blog_handlers.py
        self.render('search.html', posts=posts, q=q, total=total, page=page,
            page_size=options.page_size_search_posts)


class RssHandler(BaseHandler):

    @tornado.gen.engine
    @tornado.web.asynchronous
    def get(self):
        posts = yield Op(self.db.posts.find().sort("date",
            -1).limit(10).to_list)
        self.set_header("Content-Type", "text/xml; charset=UTF-8")
        self.render("rss.xml", posts=posts, options=options)
=======
        self.render('search.html', posts=posts, form=form, total=total,
            page=page, page_size=options.page_size_search_posts)
>>>>>>> master:selene/web/handlers/blog.py


class NewCommentHandler(BaseHandler):

    @tornado.gen.engine
    @tornado.web.asynchronous
    def post(self, slug):
        post = yield Op(self.db.posts.find_one, {'slug': slug}, {'_id': 1})
        if not post:
            raise tornado.web.HTTPError(500)
        data = {'content': self.get_argument('content', '')}
        if not self.current_user:
            data.update({
                'name': self.get_argument('name', ''),
                'email': self.get_argument('email', '')
            })
        else:
<<<<<<< HEAD:selene/handlers/blog_handlers.py
            name = self.current_user['name']
            email = self.current_user['email']
        yield Op(self.db.comments.insert, {
            'postid': post['_id'], 'name': name, 'email': email,
            'content': self.get_argument('content'),
            'date': datetime.datetime.now(), 'likes': 0, 'dislikes': 0})
        self.redirect('/post/%s' % slug)
=======
            data.update({
                'name': self.current_user['full_name'],
                'email': self.current_user['email']
            })
        form = forms.CommentForm(locale_code=self.locale.code, **data)
        if form.validate():
            comment = form.data
            comment.update({
                'postid': post['_id'],
                'date': datetime.datetime.now(),
                'likes': 0,
                'dislikes': 0
            })
            self.db.comments.insert(comment)
            self.redirect(self.reverse_url('post', slug))
        else:
            post = self.db.posts.find_one({'slug': slug, 'status': 'published'})
            if not post:
                raise tornado.web.HTTPError(404)
            comments = list(self.db.comments.find({'postid':
                post['_id']}).sort('date', 1))
            older = self.db.posts.find({'_id': {'$lt': post['_id']},
                'status': 'published'}).sort('date', -1).limit(1)
            newer = self.db.posts.find({'_id': {'$gt': post['_id']},
                'status': 'published'}).sort('date', 1).limit(1)
            older = None if older.count() == 0 else older[0]
            newer = None if newer.count() == 0 else newer[0]
            self.render('post.html', post=post, comments=comments, older=older,
                newer=newer, form_message=form.errors, comment_form=form)
>>>>>>> master:selene/web/handlers/blog.py


class LikeCommentHandler(BaseHandler):

    @tornado.gen.engine
    @tornado.web.asynchronous
    def post(self, comment_id, action):
        if action not in ['like', 'dislike']:
            raise tornado.web.HTTPError(404)
        comment_id = ObjectId(comment_id)
        comment = yield Op(self.db.comments.find_and_modify,
            {'_id': comment_id}, fields={'postid': 1},
            update={'$inc': {action + 's': 1}}, new=True)
        if not comment:
            raise tornado.web.HTTPError(404)
<<<<<<< HEAD:selene/handlers/blog_handlers.py
        post = yield Op(self.db.posts.find_one, {'_id': comment['postid']})
        self.redirect('/post/%s' % post['slug'])
=======
        post = self.db.posts.find_one({'_id': comment['postid']})
        self.redirect(self.reverse_url('post', post['slug']))
>>>>>>> master:selene/web/handlers/blog.py


class EditCommentHandler(BaseHandler):

    @authenticated_async
    @tornado.gen.engine
    @tornado.web.asynchronous
    def get(self, comment_id):
        comment = yield Op(self.db.comments.find_one,
            {'_id': ObjectId(comment_id)})
        if not comment:
            raise tornado.web.HTTPError(404)
<<<<<<< HEAD:selene/handlers/blog_handlers.py
        post = yield Op(self.db.posts.find_one, {'_id': comment['postid']})
        self.render('editcomment.html', post=post, comment=comment)
=======
        post = self.db.posts.find_one({'_id': comment['postid']})
        self.render('editcomment.html', post=post,
            form=forms.CommentForm(locale_code=self.locale.code, **comment))
>>>>>>> master:selene/web/handlers/blog.py

    @authenticated_async
    @tornado.gen.engine
    @tornado.web.asynchronous
    def post(self, comment_id):
        comment = yield Op(self.db.comments.find_one,
            {'_id': ObjectId(comment_id)}, {'postid': 1})
        if not comment:
            raise tornado.web.HTTPError(404)
<<<<<<< HEAD:selene/handlers/blog_handlers.py
        yield Op(self.db.comments.update, {'_id': ObjectId(comment_id)}, {
            '$set': {
                'name': self.get_argument('name'),
                'email': self.get_argument('email'),
                'content': self.get_argument('content')
            }
        })
        post = yield Op(self.db.posts.find_one, {'_id': comment['postid']})
        self.redirect('/post/%s' % post['slug'])
=======
        form = forms.CommentForm(self.request.arguments,
            locale_code=self.locale.code)
        if form.validate():
            self.db.comments.update({'_id': ObjectId(comment_id)},
                {'$set': form.data})
            post = self.db.posts.find_one({'_id': comment['postid']})
            self.redirect(self.reverse_url('post', post['slug']))
        else:
            post = self.db.posts.find_one({'_id': comment['postid']})
            self.render('editcomment.html', post=post,
                message=form.errors, form=form)
>>>>>>> master:selene/web/handlers/blog.py


class DeleteCommentHandler(BaseHandler):

    @authenticated_async
    @tornado.gen.engine
    @tornado.web.asynchronous
    def get(self, comment_id):
        comment = yield Op(self.db.comments.find_one,
            {'_id': ObjectId(comment_id)})
        if not comment:
            raise tornado.web.HTTPError(404)
        post = yield Op(self.db.posts.find_one, {'_id': comment['postid']})
        self.render('deletecomment.html', post=post, comment=comment)

    @authenticated_async
    @tornado.gen.engine
    @tornado.web.asynchronous
    def post(self, comment_id):
        comment = yield Op(self.db.comments.find_one,
            {'_id': ObjectId(comment_id)}, {'postid': 1})
        if not comment:
            raise tornado.web.HTTPError(404)
<<<<<<< HEAD:selene/handlers/blog_handlers.py
        post = yield Op(self.db.posts.find_one, {'_id': comment['postid']})
        yield Op(self.db.comments.remove, {'_id': ObjectId(comment_id)})
        self.redirect('/post/%s' % post['slug'])
=======
        post = self.db.posts.find_one({'_id': comment['postid']})
        self.db.comments.remove({'_id': ObjectId(comment_id)})
        self.redirect(self.reverse_url('post', post['slug']))
>>>>>>> master:selene/web/handlers/blog.py
