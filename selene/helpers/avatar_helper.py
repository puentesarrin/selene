# -*- coding: utf-8 *-*
import hashlib


def get_avatar(email, size=48):
    md5email = hashlib.md5(email).hexdigest()
    query = "%s?s=%s" % (md5email, size)
    return 'http://gravatar.com/avatar/' + query
