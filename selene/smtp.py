import logging
import os
from email.message import EmailMessage
from textwrap import indent

import aiosmtplib
from tornado.options import options as opts
from tornado.template import Loader


class SMTP:
    _warned_unconfigured = False

    def __init__(self) -> None:
        self.enabled = bool(opts.smtp_enabled)
        self.template_loader = Loader(os.path.join(opts.themes_directory, opts.selected_theme, 'messages'))
        if not self.enabled and not self.__class__._warned_unconfigured:
            logging.warning('SMTP is not configured; email delivery is disabled and messages will be logged.')
            self.__class__._warned_unconfigured = True

    async def send(self, subject: str, template: str, to: str, params: dict[str, object]) -> bool:
        title = ' - '.join([opts.title, subject])
        params = {**params, 'title': title, 'base_url': opts.base_url}
        body = self.template_loader.load(template).generate(**params)
        if isinstance(body, bytes):
            body = body.decode('utf-8')

        message = EmailMessage()
        message['Subject'] = title
        message['From'] = opts.smtp_username or 'selene@localhost'
        message['To'] = to
        message.set_content(body, subtype='html')

        if not self.enabled:
            logging.warning(
                'SMTP disabled; email preview:\nTo: %s\nSubject: %s\nBody:\n%s',
                to,
                title,
                indent(body, '  '),
            )
            return False

        smtp_client = aiosmtplib.SMTP(hostname=opts.smtp_host, port=opts.smtp_port, start_tls=opts.smtp_use_tls)
        async with smtp_client:
            if opts.smtp_username and opts.smtp_password:
                await smtp_client.login(opts.smtp_username, opts.smtp_password)
            await smtp_client.send_message(message)
        return True
