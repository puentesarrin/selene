# -*- coding: utf-8 *-*
import string
import random
import hashlib


def generate_string(size=20,
    chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def generate_md5(input_text=generate_string()):
    return hashlib.md5(input_text).hexdigest()
