import platform

import pymongo
import tornado
import tornado.web
from tornado.options import options

from selene import forms, version
from selene.constants import PostStatus
from selene.web import BaseHandler, admin_required, authenticated_async


class AdminDashboardHandler(BaseHandler):
    async def _dashboard_context(self):
        site_settings = await self.get_site_settings_async()
        posts = await self.db.posts.find().sort('date', -1).to_list(None)
        await self.hydrate_posts(posts)
        stats = {
            'users': await self.db.users.count_documents({}),
            'posts': await self.db.posts.count_documents({}),
            'published_posts': await self.db.posts.count_documents({'status': PostStatus.PUBLISHED.value}),
            'draft_posts': await self.db.posts.count_documents({'status': PostStatus.UNPUBLISHED.value}),
            'comments': await self.db.comments.count_documents({}),
        }
        status = {
            'python': platform.python_version(),
            'tornado': tornado.version,
            'pymongo': pymongo.version,
            'selene': version,
        }
        try:
            await self.db.client.admin.command('ping')
            status['database'] = 'ok'
        except Exception:
            status['database'] = 'unavailable'
        form = forms.SiteSettingsForm(
            locale_code=self.locale.code,
            title=site_settings.get('title', options.title),
            slogan=site_settings.get('slogan', options.slogan),
        )
        return {'form': form, 'posts': posts, 'site_settings': site_settings, 'stats': stats, 'status': status}

    @authenticated_async
    @admin_required
    async def get(self):
        await self.render('admin.html', **await self._dashboard_context())

    @authenticated_async
    @admin_required
    async def post(self):
        context = await self._dashboard_context()
        form = forms.SiteSettingsForm(self.request.arguments, locale_code=self.locale.code)
        if not form.validate():
            context['form'] = form
            await self.render('admin.html', message=form.errors, **context)
            return
        site_settings = {'_id': 'site', 'title': form.data['title'], 'slogan': form.data['slogan']}
        existing = await self.db.settings.find_one({'_id': 'site'})
        if existing:
            await self.db.settings.update_one({'_id': 'site'}, {'$set': {'title': form.data['title'], 'slogan': form.data['slogan']}})
        else:
            await self.db.settings.insert_one(site_settings)
        self._site_settings = site_settings
        self.redirect(self.reverse_url('admin'))
