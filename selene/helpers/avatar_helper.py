# -*- coding: utf-8 *-*
import hashlib


class Gravatar(object):

    def get_avatar(self, email, size=48):
        md5email = hashlib.md5(email).hexdigest()
        query = "%s?s=%s" % (md5email, size)
        return 'http://gravatar.com/avatar/' + query
