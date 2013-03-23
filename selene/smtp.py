# -*- coding: utf-8 *-*
import os

from tornado.options import options as opts
from tornado.template import Loader
from tornadomail.backends.smtp import EmailBackend
from tornadomail.message import EmailFromTemplate


class SMTP(EmailBackend):

    def __init__(self):
        super(SMTP, self).__init__(host=opts.smtp_host, port=opts.smtp_port,
            username=opts.smtp_username, password=opts.smtp_password,
            use_tls=opts.smtp_use_tls,
            template_loader=Loader(os.path.join(opts.themes_directory,
                opts.selected_theme, 'messages')),
            url=opts.base_url)

    def send(self, subject, template, to, params, callback=None):
        title = ' - '.join([opts.title, subject])
        params.update({'title': title, 'base_url': opts.base_url})
        message = _Message(title, template, opts.smtp_username, to.split(','),
            self, **params)
        if not callback:
            message.send()
        else:
            message.send(callback=callback)


class _Message(EmailFromTemplate):

    def __init__(self, subject, template, from_email, to, connection,
        **params):
        super(_Message, self).__init__(subject, template, params, from_email,
            to, connection=connection)
