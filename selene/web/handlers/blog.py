import datetime
import re

import tornado.web
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import OperationFailure
from tornado.options import options

from selene import forms, helpers
from selene import options as opts
from selene.constants import PostStatus
from selene.web import BaseHandler, authenticated_async


async def attach_comments(db, post):
    post['comments'] = await db.comments.find({'postid': post['_id']}).to_list(None)
    return post


class HomeHandler(BaseHandler):
    async def get(self, page=1):
        page = int(page)
        cursor = self.db.posts.find({'status': PostStatus.PUBLISHED.value})
        cursor = cursor.sort('date', -1)
        cursor = cursor.skip((page - 1) * options.page_size_posts)
        cursor = cursor.limit(options.page_size_posts)
        posts = await cursor.to_list(None)
        for post in posts:
            await attach_comments(self.db, post)
        total = await self.db.posts.count_documents({'status': PostStatus.PUBLISHED.value})
        await self.render('home.html', posts=posts, total=total, page=page, page_size=options.page_size_posts)


class NewPostHandler(BaseHandler):
    @authenticated_async
    async def get(self):
        form = forms.PostForm(
            locale_code=self.locale.code,
            status_choices=opts.STATUSES,
            text_type_choices=opts.get_allowed_text_types(),
        )
        await self.render('newpost.html', form=form)

    @authenticated_async
    async def post(self):
        custom_slug = self.get_argument('custom_slug', False)
        if custom_slug:
            slug = helpers.get_slug(
                self.get_argument('slug'),
                options.slug_stop_words,
            )
        else:
            slug = helpers.get_slug(
                self.get_argument('title'),
                options.slug_stop_words,
            )
        html_content, plain_content = helpers.get_html_and_plain(
            self.get_argument('content'), self.get_argument('text_type')
        )
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
            'author_id': self.current_user['_id'],
            'votes': 0,
            'views': 0,
        }
        form = forms.PostForm(
            locale_code=self.locale.code,
            status_choices=opts.STATUSES,
            text_type_choices=opts.get_allowed_text_types(),
            **post,
        )
        existing_post = await self.db.posts.find_one({'slug': slug}, {'_id': 1})
        if existing_post:
            return await self.render(
                'newpost.html',
                message='There are already an existing post with this title or slug.',
                form=form,
                new=True,
            )
        await self.db.posts.insert_one(post)
        if post['status'] == PostStatus.PUBLISHED.value:
            self.redirect(f'/post/{post["slug"]}')
        else:
            await self.render('newpost.html', message='Post saved as unpublished', form=form)


class PostHandler(BaseHandler):
    async def get(self, slug_post):
        post = await self.db.posts.find_one_and_update(
            {'slug': slug_post, 'status': PostStatus.PUBLISHED.value},
            {'$inc': {'views': 1}},
            return_document=ReturnDocument.AFTER,
        )
        if not post:
            raise tornado.web.HTTPError(404)
        comments = await self.db.comments.find({'postid': post['_id']}).to_list(None)
        older_cursor = self.db.posts.find({'_id': {'$lt': post['_id']}, 'status': PostStatus.PUBLISHED.value})
        older_cursor = older_cursor.sort('date', -1)
        older_cursor = older_cursor.limit(1)
        older_list = await older_cursor.to_list(None)
        newer_cursor = self.db.posts.find({'_id': {'$gt': post['_id']}, 'status': PostStatus.PUBLISHED.value})
        newer_cursor = newer_cursor.sort('date', 1)
        newer_cursor = newer_cursor.limit(1)
        newer_list = await newer_cursor.to_list(None)
        older = older_list[0] if older_list else None
        newer = newer_list[0] if newer_list else None
        data = {}
        if self.current_user:
            data.update(
                {
                    'name': self.current_user.get('full_name') or self.current_user.get('name'),
                    'email': self.current_user['email'],
                }
            )
        comment_form = forms.CommentForm(locale_code=self.locale.code, **data)
        await self.render(
            'post.html',
            post=post,
            comments=comments,
            older=older,
            newer=newer,
            form_message=None,
            comment_form=comment_form,
        )


class EditPostHandler(BaseHandler):
    @authenticated_async
    async def get(self, slug):
        post = await self.db.posts.find_one({'slug': slug})
        if not post:
            raise tornado.web.HTTPError(404)
        if not self.can_manage_post(post):
            raise tornado.web.HTTPError(403)
        post['tags'] = ','.join(post['tags'])
        form = forms.PostForm(
            locale_code=self.locale.code,
            status_choices=opts.STATUSES,
            text_type_choices=opts.get_allowed_text_types(),
            **post,
        )
        await self.render('editpost.html', form=form)

    @authenticated_async
    async def post(self, slug):
        custom_slug = self.get_argument('custom_slug', False)
        if custom_slug:
            new_slug = helpers.get_slug(
                self.get_argument('slug'),
                options.slug_stop_words,
            )
        else:
            new_slug = helpers.get_slug(
                self.get_argument('title'),
                options.slug_stop_words,
            )
        html_content, plain_content = helpers.get_html_and_plain(
            self.get_argument('content'), self.get_argument('text_type')
        )
        new_post = {
            'title': self.get_argument('title'),
            'slug': new_slug,
            'tags': helpers.remove_duplicates(self.get_argument('tags')),
            'content': self.get_argument('content'),
            'html_content': html_content,
            'plain_content': plain_content,
            'status': self.get_argument('status'),
            'text_type': self.get_argument('text_type'),
        }
        form = forms.PostForm(
            locale_code=self.locale.code,
            status_choices=opts.STATUSES,
            text_type_choices=opts.get_allowed_text_types(),
            **new_post,
        )
        if not self.can_manage_post(await self.db.posts.find_one({'slug': slug}) or {}):
            raise tornado.web.HTTPError(403)
        await self.db.posts.update_one({'slug': slug}, {'$set': new_post})
        if new_post['status'] == PostStatus.PUBLISHED.value:
            self.redirect(f'/post/{new_slug}')
        else:
            await self.render('editpost.html', message='Post saved as unpublished', form=form)


class DeletePostHandler(BaseHandler):
    @authenticated_async
    async def get(self, slug):
        post = await self.db.posts.find_one({'slug': slug}, {'title': 1, 'slug': 1})
        if not post:
            raise tornado.web.HTTPError(404)
        if not self.can_manage_post(post):
            raise tornado.web.HTTPError(403)
        await self.render('deletepost.html', post=post)

    @authenticated_async
    async def post(self, slug):
        post = await self.db.posts.find_one({'slug': slug})
        if not post:
            raise tornado.web.HTTPError(404)
        if not self.can_manage_post(post):
            raise tornado.web.HTTPError(403)
        await self.db.comments.delete_many({'postid': post['_id']})
        await self.db.posts.delete_one({'slug': slug})
        self.redirect(self.reverse_url('posts'))


class VotePostHandler(BaseHandler):
    async def post(self, slug):
        result = await self.db.posts.update_one({'slug': slug}, {'$inc': {'votes': 1}})
        if not result.matched_count:
            raise tornado.web.HTTPError(404)
        self.redirect(f'/post/{slug}')


class PostsHandlers(BaseHandler):
    @authenticated_async
    async def get(self):
        title = self.get_argument('title', '')
        title_filter = re.compile(rf'.*{re.escape(title)}.*', re.IGNORECASE)
        query = {'title': title_filter}
        if not self.current_user.get('is_admin'):
            query = {'$and': [query, {'$or': [{'author_id': self.current_user['_id']}, {'email': self.current_user['email']}]}]}
        posts_cursor = self.db.posts.find(query)
        posts_cursor = posts_cursor.sort('date', -1)
        posts = await posts_cursor.to_list(None)
        await self.render('posts.html', title=title, posts=posts)


class TagHandler(BaseHandler):
    async def get(self, tag, page=1):
        page = int(page)
        posts_cursor = self.db.posts.find({'tags': tag, 'status': PostStatus.PUBLISHED.value})
        posts_cursor = posts_cursor.sort('date', -1)
        posts_cursor = posts_cursor.skip((page - 1) * options.page_size_posts)
        posts_cursor = posts_cursor.limit(options.page_size_tag_posts)
        posts = await posts_cursor.to_list(None)
        if not posts:
            raise tornado.web.HTTPError(404)
        for post in posts:
            await attach_comments(self.db, post)
        total = await self.db.posts.count_documents({'tags': tag, 'status': PostStatus.PUBLISHED.value})
        await self.render(
            'tag.html', tag=tag, posts=posts, total=total, page=page, page_size=options.page_size_tag_posts
        )


class TagsHandlers(BaseHandler):
    async def get(self):
        tags_cursor = await self.db.posts.aggregate(
            [
                {'$match': {'status': PostStatus.PUBLISHED.value}},
                {'$unwind': '$tags'},
                {'$group': {'_id': '$tags', 'sum': {'$sum': 1}}},
                {'$sort': {'_id': 1}},
            ]
        )
        tags = await tags_cursor.to_list(None)
        await self.render('tags.html', tags=tags)


class SearchHandler(BaseHandler):
    async def get(self):
        page = int(self.get_argument('page', 1))
        q = self.get_argument('q', '')
        form = forms.SearchForm(
            locale_code=self.locale.code,
            q=q,
        )
        if q:
            try:
                query = {'$text': {'$search': q}, 'status': PostStatus.PUBLISHED.value}
                posts_cursor = self.db.posts.find(query)
                posts_cursor = posts_cursor.sort('date', -1)
                posts_cursor = posts_cursor.skip((page - 1) * options.page_size_search_posts)
                posts_cursor = posts_cursor.limit(options.page_size_search_posts)
                posts = await posts_cursor.to_list(None)
                total = await self.db.posts.count_documents(query)
            except OperationFailure:
                q_filter = re.compile(rf'.*{re.escape(q)}.*', re.IGNORECASE)
                posts_cursor = self.db.posts.find({'plain_content': q_filter, 'status': PostStatus.PUBLISHED.value})
                posts_cursor = posts_cursor.sort('date', -1)
                posts_cursor = posts_cursor.skip((page - 1) * options.page_size_search_posts)
                posts_cursor = posts_cursor.limit(options.page_size_search_posts)
                posts = await posts_cursor.to_list(None)
                total = await self.db.posts.count_documents(
                    {'plain_content': q_filter, 'status': PostStatus.PUBLISHED.value}
                )
        else:
            posts = []
            total = 0
        await self.render(
            'search.html', posts=posts, q=q, total=total, page=page, page_size=options.page_size_search_posts, form=form
        )


class RssHandler(BaseHandler):
    async def get(self):
        posts_cursor = self.db.posts.find()
        posts_cursor = posts_cursor.sort('date', -1)
        posts_cursor = posts_cursor.limit(10)
        posts = await posts_cursor.to_list(None)
        self.set_header('Content-Type', 'text/xml; charset=UTF-8')
        await self.render('rss.xml', posts=posts, options=options)


class NewCommentHandler(BaseHandler):
    async def post(self, slug):
        post = await self.db.posts.find_one({'slug': slug}, {'_id': 1})
        if not post:
            raise tornado.web.HTTPError(500)
        comment = {
            'postid': post['_id'],
            'content': self.get_argument('content'),
            'date': datetime.datetime.now(),
            'likes': 0,
            'dislikes': 0,
        }
        if not self.current_user:
            comment['name'] = self.get_argument('name', '')
            comment['email'] = self.get_argument('email', '')
        else:
            comment['author_id'] = self.current_user['_id']
            comment['name'] = self.current_user.get('full_name') or self.current_user.get('name')
            comment['email'] = self.current_user['email']
        await self.db.comments.insert_one(comment)
        self.redirect(f'/post/{slug}')


class LikeCommentHandler(BaseHandler):
    async def post(self, comment_id, action):
        if action not in ['like', 'dislike']:
            raise tornado.web.HTTPError(404)
        comment = await self.db.comments.find_one_and_update(
            {'_id': ObjectId(comment_id)},
            {'$inc': {action + 's': 1}},
            projection={'postid': 1},
            return_document=ReturnDocument.AFTER,
        )
        if not comment:
            raise tornado.web.HTTPError(404)
        post = await self.db.posts.find_one({'_id': comment['postid']})
        self.redirect(f'/post/{post["slug"]}')


class EditCommentHandler(BaseHandler):
    @authenticated_async
    async def get(self, comment_id):
        comment = await self.db.comments.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            raise tornado.web.HTTPError(404)
        if not self.can_manage_comment(comment):
            raise tornado.web.HTTPError(403)
        post = await self.db.posts.find_one({'_id': comment['postid']})
        await self.render('editcomment.html', post=post, comment=comment)

    @authenticated_async
    async def post(self, comment_id):
        comment = await self.db.comments.find_one({'_id': ObjectId(comment_id)}, {'postid': 1})
        if not comment:
            raise tornado.web.HTTPError(404)
        full_comment = await self.db.comments.find_one({'_id': ObjectId(comment_id)})
        if not self.can_manage_comment(full_comment or {}):
            raise tornado.web.HTTPError(403)
        update = {'content': self.get_argument('content')}
        if not (full_comment or {}).get('author_id'):
            update.update({'name': self.get_argument('name'), 'email': self.get_argument('email')})
        await self.db.comments.update_one({'_id': ObjectId(comment_id)}, {'$set': update})
        post = await self.db.posts.find_one({'_id': comment['postid']})
        self.redirect(f'/post/{post["slug"]}')


class DeleteCommentHandler(BaseHandler):
    @authenticated_async
    async def get(self, comment_id):
        comment = await self.db.comments.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            raise tornado.web.HTTPError(404)
        if not self.can_manage_comment(comment):
            raise tornado.web.HTTPError(403)
        post = await self.db.posts.find_one({'_id': comment['postid']})
        await self.render('deletecomment.html', post=post, comment=comment)

    @authenticated_async
    async def post(self, comment_id):
        comment = await self.db.comments.find_one({'_id': ObjectId(comment_id)})
        if not comment:
            raise tornado.web.HTTPError(404)
        if not self.can_manage_comment(comment):
            raise tornado.web.HTTPError(403)
        post = await self.db.posts.find_one({'_id': comment['postid']})
        await self.db.comments.delete_one({'_id': ObjectId(comment_id)})
        self.redirect(f'/post/{post["slug"]}')
