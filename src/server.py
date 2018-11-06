import json
import re
import os

import falcon
import redis
import requests

from . import helpers

"""
Settings
"""

# The number of minutes hashes are good for before they're deleted
HASH_LIFESPAN_MINS = os.getenv('HASH_LIFESPAN_MINS', 5)
# Cookies we'll need to spoof before we can verify a user's profile
SA_COOKIES = {
    'sessionid': os.getenv('COOKIE_SESSIONID'),
    'sessionhash': os.getenv('COOKIE_SESSIONHASH'),
    'bbuserid': os.getenv('COOKIE_BBUSERID'),
    'bbpassword': os.getenv('COOKIE_BBPASSWORD'),
}
# URL in the following format: redis://[username:password]@localhost:6379.
# DB number can be specified by updating "0" below
REDIS_URL = os.getenv('REDIS_URL', '') + '/0'

# A URL to look up SA users by their username
SA_PROFILE_URL = 'http://forums.somethingawful.com/member.php?action=getinfo&username='

"""
Begin Server
"""

# Connect to the Redis DB (and automatically decode values because they're all going to be strings)
redis_db = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)


class RequireJSON(object):
    """
    The API is only intended to handle application/json requests
    """
    def process_request(self, req, resp):
        if req.method in ['POST']:
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports JSON-encoded requests'
                )


class GenerateHashResource:
    """
    Generate a unique identifier that a goon can post to their profile to verify their identity
    """
    def on_post(self, req, resp):
        # Get the username
        body = helpers.get_json(req)
        username = helpers.get_username(body)

        user_hash = redis_db.get(username)
        if not user_hash:
            user_hash = helpers.get_hash()
            redis_db.setex(username, HASH_LIFESPAN_MINS * 60, user_hash)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'hash': user_hash})


class ValidateUserResource:
    """
    Check the goon's profile page for the presence of their hash
    """
    def on_post(self, req, resp):
        body = helpers.get_json(req)
        username = helpers.get_username(body)

        user_hash = redis_db.get(username)
        if not user_hash:
            raise falcon.HTTPBadRequest(
                'Hash Missing',
                'A hash does not exist for this username. Run /generate_hash/ first'
            )

        # The URL to the user's profile page
        profile_url = SA_PROFILE_URL + username

        # We can't view user profiles unless we're logged in, so we'll need to use a
        # requests session and set some cookies
        session = requests.Session()
        raw_profile = session.get(profile_url, cookies=SA_COOKIES)

        # Do a regex search to find the user's hash in their profile page
        result = re.search(user_hash, raw_profile.text)

        resp.status = falcon.HTTP_200
        resp.body = json.dumps({'validated': result is not None})


app = falcon.API(middleware=[
    RequireJSON()
])
generate_hash = GenerateHashResource()
validate_user = ValidateUserResource()
app.add_route('/v1/generate_hash', generate_hash)
app.add_route('/v1/validate_user', validate_user)
