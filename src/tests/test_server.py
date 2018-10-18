import json
from unittest.mock import patch
from falcon import testing

from src.tests import mocks

from src import server


class ServerTestCase(testing.TestBase):
    @patch('src.server.redis_db', mocks.redis_db)
    def setUp(self):
        super(ServerTestCase, self).setUp()
        # Initialize the server we're testing
        self.api = server.app


@patch('src.server.redis_db', mocks.redis_db)
class GenerateHashTestCase(ServerTestCase):
    def setUp(self):
        super(GenerateHashTestCase, self).setUp()
        self.url = '/v1/generate_hash/'

    def test_require_json(self):
        resp = self.simulate_request(
            self.url,
            method='POST',
            headers={
                'Content-Type': 'multipart/form-data'
            },
            body='',
            decode='utf-8',
        )
        resp = json.loads(resp)
        self.assertEqual(resp['title'], 'Unsupported media type')
        self.assertEqual(resp['description'], 'This API only supports JSON-encoded requests')

    def test_generate_hash_require_username(self):
        resp = self.simulate_request(
            self.url,
            method='POST',
            headers={
                'Content-Type': 'application/json',
            },
            body=json.dumps({}),
            decode='utf-8',
        )
        resp = json.loads(resp)
        self.assertEqual(resp['title'], 'Missing parameter')
        self.assertEqual(resp['description'], 'The "username" parameter is required.')

    def test_return_hash_for_username(self):
        resp = self.simulate_request(
            self.url,
            method='POST',
            headers={
                'Content-Type': 'application/json',
            },
            body=json.dumps({'username': 'foobar'}),
            decode='utf-8',
        )
        resp = json.loads(resp)
        self.assertIsNotNone(resp['hash'])
