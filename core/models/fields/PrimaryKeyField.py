from time import time
from django.db.models import BigIntegerField
import secrets

START_TIME = 1537758068554


def make_id():
    """
    Construct a BigInteger ID from the time and 23 random bits.

    Only 1 in 8.3 million chance of getting the same result, even when two  objects are created at the exact same time
    inspired by http://instagram-engineering.tumblr.com/post/10853187575/sharding-ids-at-instagram
    """
    t = int(time()*1000) - START_TIME
    u = secrets.SystemRandom().getrandbits(23)
    new_id = (t << 23) | u
    return new_id


def reverse_id(big_id):
    """Get the creation time from the id"""
    t = big_id >> 23
    return t + START_TIME


class PrimaryKeyField(BigIntegerField):
    """Primary key field that uses unique and semi-random BigIntegers to identify objects in a non-guessable way"""

    def __init__(self, *args, **kwargs):

        kwargs['primary_key'] = True
        kwargs['default'] = make_id

        super(PrimaryKeyField, self).__init__(*args, **kwargs)
