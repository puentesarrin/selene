# -*- coding: utf-8 *-*
import datetime
import re
import tornado.web

from bson.objectid import ObjectId
from selene import constants, forms, helpers, options as opts, text
from selene.base import BaseHandler
from tornado.options import options


class HomeHandler(BaseHandler):

    def get(self, page=1):
        def find_comments(post):
            post['comments'] = list(self.db.comments.find({'postid':
                post['_id']}))
            return post

        page = int(page)
        posts = self.db.posts.find({'status': 'published'}).sort('date',
            -1).skip((page - 1) * options.page_size_posts).limit(
                options.page_size_posts)
        posts = map(find_comments, posts)
        total = self.db.posts.find({'status': 'published'}).count()
        self.render("home.html", posts=posts, total=total, page=int(page),
            page_size=options.page_size_posts)


class NewPostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render('newpost.html',
            form=forms.PostForm(locale_code=self.locale.code,
                status_choices=opts.STATUSES,
                text_type_choices=opts.get_allowed_text_types()))

    @tornado.web.authenticated
    def post(self):
        form = forms.PostForm(self.request.arguments,
            locale_code=self.locale.code, status_choices=opts.STATUSES,
            text_type_choices=opts.get_allowed_text_types())
        if form.validate():
            if form.data['custom_slug']:
                slug = form.data['slug']
            else:
                slug = text.get_slug(form.data['title'],
                    stop_words=options.slug_stop_words)
            if self.db.posts.find_one({'slug': slug}, {'_id': 1}) or \
                slug.strip() == '':
                self.render('newpost.html',
                    message=constants.POST_IS_ALREADY_REGISTERED, form=form)
            else:
                html_content, plain_content = text.get_html_and_plain(
                    form.data['content'], form.data['text_type'])
                post = form.data
                post.update({
                    'slug': slug,
                    'date': datetime.datetime.now(),
                    'tags': helpers.remove_duplicates(form.data['tags']),
                    'html_content': html_content,
                    'plain_content': plain_content,
                    'author': self.current_user['full_name'],
                    'email': self.current_user['email'],
                    'votes': 0,
                    'views': 0
                })
                self.db.posts.insert(post)
                if post['status'] == 'published':
                    self.redirect(self.reverse_url('post', post['slug']))
                else:
                    self.redirect(self.reverse_url('home'))
        else:
            self.render('newpost.html', message=form.errors, form=form)


class PostHandler(BaseHandler):

    def get(self, slug_post):
        post = self.db.posts.find_and_modify({'slug': slug_post,
            'status': 'published'}, update={'$inc': {'views': 1}}, new=True)
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
        data = {}
        if self.current_user:
            data.update({
                'name': self.current_user['full_name'],
                'email': self.current_user['email']
            })
        comment_form = forms.CommentForm(locale_code=self.locale.code, **data)
        self.render('post.html', post=post, comments=comments, older=older,
            newer=newer, form_message=None, comment_form=comment_form)


class EditPostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, slug):
        post = self.db.posts.find_one({'slug': slug}, {'_id': 0})
        if not post:
            raise tornado.web.HTTPError(404)
        post['tags'] = ','.join(post['tags'])
        form = forms.PostForm(locale_code=self.locale.code,
            status_choices=opts.STATUSES,
            text_type_choices=opts.get_allowed_text_types(), **post)
        self.render("editpost.html", form=form)

    @tornado.web.authenticated
    def post(self, slug):
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
        else:
            self.render('editpost.html', message=form.errors, form=form)


class DeletePostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, slug):
        post = self.db.posts.find_one({'slug': slug}, {'title': 1, 'slug': 1})
        self.render("deletepost.html", post=post)

    @tornado.web.authenticated
    def post(self, slug):
        post = self.db.posts.find_one({'slug': slug})
        if not post:
            raise tornado.web.HTTPError(404)
        self.db.comments.remove({'postid': post['_id']})
        self.db.posts.remove({'slug': slug})
        self.redirect(self.reverse_url('posts'))


class VotePostHandler(BaseHandler):

    def post(self, slug):
        post = self.db.posts.find({'slug': slug})
        if not post:
            raise tornado.web.HTTPError(404)
        self.db.posts.update({'slug': slug}, {'$inc': {'votes': 1}})
        self.redirect(self.reverse_url('post', slug))


class PostsHandlers(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        title = self.get_argument('title', '')
        title_filter = re.compile('.*%s.*' % title, re.IGNORECASE)
        posts = self.db.posts.find({'title': title_filter}).sort('date', -1)
        self.render("posts.html", title=title, posts=posts)


class TagHandler(BaseHandler):

    def get(self, tag, page=1):
        def find_comments(post):
            post['comments'] = list(self.db.comments.find({'postid':
                post['_id']}))
            return post

        page = int(page)
        posts = self.db.posts.find({'tags': tag, 'status': 'published'}).sort(
            'date', -1).skip((page - 1) * options.page_size_posts).limit(
                options.page_size_tag_posts)
        if not posts.count():
            raise tornado.web.HTTPError(404)
        posts = map(find_comments, posts)
        total = self.db.posts.find({'tags': tag, 'status': 'published'}).count()
        self.render('tag.html', tag=tag, posts=posts, total=total, page=page,
            page_size=options.page_size_tag_posts)


class TagsHandlers(BaseHandler):

    def get(self):
        tags = self.db.posts.aggregate([
            {'$match': {'status': 'published'}},
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags', 'sum': {'$sum': 1}}},
            {'$sort': {'_id': 1}}
        ])['result']
        self.render('tags.html', tags=tags)


class SearchHandler(BaseHandler):

    def get(self):
        page = int(self.get_argument('page', 1))
        form = forms.SearchForm(locale_code=self.locale.code,
            q=self.get_argument('q', ''))
        if form.data['q']:
            if not options.db_use_fts:
                q_filter = re.compile('.*%s.*' % form.data['q'], re.IGNORECASE)
                posts = list(self.db.posts.find({'plain_content': q_filter,
                    'status': 'published'}).sort('date', -1).skip((page - 1) *
                    options.page_size_search_posts).limit(
                        options.page_size_search_posts))
                total = self.db.posts.find({'plain_content': q_filter,
                    'status': 'published'}).count()
            else:
                text_output = self.db.command("text", "posts",
                    search=form.data['q'], filter={'status': 'published'})
                posts = [result['obj'] for result in text_output['results']]
                total = len(posts)
        else:
            posts = []
            total = 0
        self.render('search.html', posts=posts, form=form, total=total,
            page=page, page_size=options.page_size_search_posts)


class NewCommentHandler(BaseHandler):

    def post(self, slug):
        post = self.db.posts.find_one({'slug': slug}, {'_id': 1})
        if not post:
            raise tornado.web.HTTPError(500)
        data = {'content': self.get_argument('content', '')}
        if not self.current_user:
            data.update({
                'name': self.get_argument('name', ''),
                'email': self.get_argument('email', '')
            })
        else:
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


class LikeCommentHandler(BaseHandler):

    def post(self, comment_id, action):
        if action not in ['like', 'dislike']:
            raise tornado.web.HTTPError(404)
        comment_id = ObjectId(comment_id)
        comment = self.db.comments.find_and_modify({'_id': comment_id},
            fields={'postid': 1}, update={'$inc': {action + 's': 1}}, new=True)
        if not comment:
            raise tornado.web.HTTPError(404)
        post = self.db.posts.find_one({'_id': comment['postid']})
        self.redirect(self.reverse_url('post', post['slug']))


class EditCommentHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, comment_id):
        comment = self.db.comments.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            raise tornado.web.HTTPError(404)
        post = self.db.posts.find_one({'_id': comment['postid']})
        self.render('editcomment.html', post=post,
            form=forms.CommentForm(locale_code=self.locale.code, **comment))

    @tornado.web.authenticated
    def post(self, comment_id):
        comment = self.db.comments.find_one({'_id': ObjectId(comment_id)},
            {'postid': 1})
        if not comment:
            raise tornado.web.HTTPError(404)
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


class DeleteCommentHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, comment_id):
        comment = self.db.comments.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            raise tornado.web.HTTPError(404)
        post = self.db.posts.find_one({'_id': comment['postid']})
        self.render('deletecomment.html', post=post, comment=comment)

    @tornado.web.authenticated
    def post(self, comment_id):
        comment = self.db.comments.find_one({'_id': ObjectId(comment_id)},
            {'postid': 1})
        if not comment:
            raise tornado.web.HTTPError(404)
        post = self.db.posts.find_one({'_id': comment['postid']})
        self.db.comments.remove({'_id': ObjectId(comment_id)})
        self.redirect(self.reverse_url('post', post['slug']))
