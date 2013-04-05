# -*- coding: utf-8 *-*
import datetime
import re
import tornado.web

from bson.objectid import ObjectId
from selene import helpers
from selene.web import BaseHandler
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
        self.render('newpost.html', message='', post={}, new=True)

    @tornado.web.authenticated
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
        existing_post = self.db.posts.find_one({'slug': slug}, {'_id': 1})
        if existing_post:
            self.render('newpost.html', message=('There are already an '
                'existing post with this title or slug.'), post={}, new=True)
            return
        self.db.posts.insert(post)
        if post['status'] == 'published':
            self.redirect('/post/%s' % post['slug'])
        else:
            self.redirect('/')


class PostHandler(BaseHandler):

    def get(self, slug_post):
        post = self.db.posts.find_and_modify({'slug': slug_post,
            'status': 'published'}, update={'$inc': {'views': 1}}, new=True)
        if not post:
            raise tornado.web.HTTPError(404)
        comments = list(self.db.comments.find({'postid': post['_id']}))
        older = self.db.posts.find({'_id': {'$lt': post['_id']},
            'status': 'published'}).sort('date', -1).limit(1)
        newer = self.db.posts.find({'_id': {'$gt': post['_id']},
            'status': 'published'}).sort('date', 1).limit(1)
        older = None if older.count() == 0 else older[0]
        newer = None if newer.count() == 0 else newer[0]
        self.render('post.html', post=post, comments=comments, older=older,
            newer=newer)


class EditPostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, slug):
        post = self.db.posts.find_one({'slug': slug})
        if not post:
            raise tornado.web.HTTPError(404)
        self.render("newpost.html", message='', post=post, new=False)

    @tornado.web.authenticated
    def post(self, slug):
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
        self.db.posts.update({'slug': slug}, {'$set': new_post})
        if new_post['status'] == 'published':
            self.redirect('/post/%s' % new_slug)
        else:
            self.redirect('/')


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

    def get(self):
        self.set_header("Content-Type", "text/xml; charset=UTF-8")
        self.render("rss.xml",
            posts=self.db.posts.find().sort("date", -1).limit(10),
            options=options)


class NewCommentHandler(BaseHandler):

    def post(self, slug):
        post = self.db.posts.find_one({'slug': slug}, {'_id': 1})
        if not post:
            raise tornado.web.HTTPError(500)
        if not self.current_user:
            name = self.get_argument('name')
            email = self.get_argument('email')
        else:
            name = self.current_user['name']
            email = self.current_user['email']
        self.db.comments.insert({'postid': post['_id'],
                                 'name': name,
                                 'email': email,
                                 'content': self.get_argument('content'),
                                 'date': datetime.datetime.now(),
                                 'likes': 0,
                                 'dislikes': 0})
        self.redirect('/post/%s' % slug)


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
        self.redirect('/post/%s' % post['slug'])


class EditCommentHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, comment_id):
        comment = self.db.comments.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            raise tornado.web.HTTPError(404)
        post = self.db.posts.find_one({'_id': comment['postid']})
        self.render('editcomment.html', post=post, comment=comment)

    @tornado.web.authenticated
    def post(self, comment_id):
        comment = self.db.comments.find_one({'_id': ObjectId(comment_id)},
            {'postid': 1})
        if not comment:
            raise tornado.web.HTTPError(404)
        self.db.comments.update({'_id': ObjectId(comment_id)}, {'$set': {
            'name': self.get_argument('name'),
            'email': self.get_argument('email'),
            'content': self.get_argument('content')
        }})
        post = self.db.posts.find_one({'_id': comment['postid']})
        self.redirect('/post/%s' % post['slug'])


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
        self.redirect('/post/%s' % post['slug'])
