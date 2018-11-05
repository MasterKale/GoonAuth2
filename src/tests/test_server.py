import json
from unittest.mock import patch
import falcon
from falcon import testing

from src.tests import mocks

from src import server

req_params = {
    'headers': {
        'Content-Type': 'application/json'
    },
    'decode': 'utf-8',
}


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

    def test_client_must_accept_json(self):
        # TODO: Fix this test to fail after overhaul. Falcon 0.3.0 isn't raising during testing
        #       for some reason
        with self.assertRaises(falcon.HTTPNotAcceptable):
            self.simulate_request(
                self.url,
                method='POST',
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'text/plain',
                },
                body=json.dumps({'username': 'foobar'}),
                decode='utf-8',
            )

    def test_generate_hash_require_username(self):
        resp = self.simulate_request(
            self.url,
            method='POST',
            body=json.dumps({}),
            **req_params,
        )
        resp = json.loads(resp)
        self.assertEqual(resp['title'], 'Missing parameter')
        self.assertEqual(resp['description'], 'The "username" parameter is required.')

    def test_return_hash_for_username(self):
        resp = self.simulate_request(
            self.url,
            method='POST',
            body=json.dumps({'username': 'foobar'}),
            **req_params,
        )
        resp = json.loads(resp)
        self.assertIsNotNone(resp['hash'])

    def test_returns_same_hash_for_same_username(self):
        username = 'foobar'
        resp1 = self.simulate_request(
            self.url,
            method='POST',
            body=json.dumps({'username': username}),
            **req_params,
        )
        resp1 = json.loads(resp1)

        resp2 = self.simulate_request(
            self.url,
            method='POST',
            body=json.dumps({'username': username}),
            **req_params,
        )
        resp2 = json.loads(resp2)

        self.assertEqual(resp1['hash'], resp2['hash'])

