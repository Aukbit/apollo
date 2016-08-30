
import re
import random
import string
import datetime
import hashlib

PUNCT_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in PUNCT_RE.split(text.lower()):
        word = word.encode('translit/long')
        if word:
            result.append(word)
    return unicode(delim.join(result))


def random_token(extra=None, hash_func=hashlib.sha256):
    if extra is None:
        extra = []
    bits = extra + [str(random.SystemRandom().getrandbits(512))]
    return hash_func("".join(bits).encode('utf-8')).hexdigest()


def random_hexdigit(y=6):
   return ''.join(random.choice(string.hexdigits) for x in range(y))


def random_lowerdigit(y=6):
   return ''.join(random.choice(string.lowercase + string.digits) for x in range(y))

def hash_md5(text_string=None):
    if text_string:
        return hashlib.md5(text_string).hexdigest()
    return None
