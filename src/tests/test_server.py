import json
from unittest.mock import patch

from falcon import testing
import requests

from src.tests import mocks

from src import server

req_params = {
    "headers": {
        "Content-Type": "application/json"
    },
}


class ServerTestCase(testing.TestCase):
    @patch("src.server.redis_db", mocks.redis_db)
    def setUp(self):
        super(ServerTestCase, self).setUp()
        # Initialize the server we"re testing
        self.api = server.app


class RequireJSONMiddlewareTestCase(ServerTestCase):
    def setUp(self):
        super(RequireJSONMiddlewareTestCase, self).setUp()
        self.url = "/v1/generate_hash/"

    def test_require_json_requests(self):
        resp = self.simulate_post(
            self.url,
            headers={
                "Content-Type": "multipart/form-data"
            },
            body="",
        )
        self.assertEqual(resp.status_code, 415)
        self.assertEqual(resp.json["title"], "Unsupported media type")
        self.assertEqual(resp.json["description"], "This API only supports JSON-encoded requests")


@patch("src.server.redis_db", mocks.redis_db)
class GenerateHashTestCase(ServerTestCase):
    def setUp(self):
        super(GenerateHashTestCase, self).setUp()
        self.url = "/v1/generate_hash/"

    def test_generate_hash_require_username(self):
        resp = self.simulate_post(
            self.url,
            body=json.dumps({}),
            **req_params,
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json["title"], "Missing parameter")
        self.assertEqual(resp.json["description"], "The \"username\" parameter is required.")

    def test_return_hash_for_username(self):
        resp = self.simulate_post(
            self.url,
            body=json.dumps({"username": "foobar"}),
            **req_params,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.json["hash"])

    def test_returns_same_hash_for_same_username(self):
        username = "foobar"
        resp1 = self.simulate_post(
            self.url,
            body=json.dumps({"username": username}),
            **req_params,
        )

        resp2 = self.simulate_post(
            self.url,
            body=json.dumps({"username": username}),
            **req_params,
        )

        self.assertEqual(resp1.json["hash"], resp2.json["hash"])


@patch("src.server.redis_db", mocks.redis_db)
class ValidateUserResourceTestCase(ServerTestCase):
    def setUp(self):
        super(ValidateUserResourceTestCase, self).setUp()
        self.url = "/v1/validate_user/"
        mocks.redis_db.flushdb()

    def test_require_username(self):
        resp = self.simulate_post(
            self.url,
            body=json.dumps({}),
            **req_params,
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json["title"], "Missing parameter")
        self.assertEqual(resp.json["description"], "The \"username\" parameter is required.")

    def test_prompt_user_to_generate_hash_when_none_found(self):
        resp = self.simulate_post(
            self.url,
            body=json.dumps({"username": "foobar"}),
            **req_params,
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json["title"], "Hash Missing")
        self.assertEqual(
            resp.json["description"],
            "A hash does not exist for this username. Run /generate_hash/ first",
        )

    @patch.object(requests.Session, "get")
    def test_validate_hash_is_in_user_profile(self, mock_get):
        username = "foobar"
        # Generate a hash for the user
        resp1 = self.simulate_post(
            "/v1/generate_hash/",
            body=json.dumps({"username": username}),
            **req_params,
        )

        # The user has put their hash in their profile
        mock_get.return_value = mocks.ProfileMock(text=resp1.json["hash"])

        # Validate the existence of the hash in the profile
        resp2 = self.simulate_post(
            self.url,
            body=json.dumps({"username": username}),
            **req_params,
        )

        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json["validated"], True)

    @patch.object(requests.Session, "get")
    def test_validate_hash_is_not_in_user_profile(self, mock_get):
        username = "foobar"
        # Generate a hash for the user
        self.simulate_post(
            "/v1/generate_hash/",
            body=json.dumps({"username": username}),
            **req_params,
        )

        # The user has put their hash in their profile
        mock_get.return_value = mocks.ProfileMock(text="hash_is_not_here")

        # Won"t be able to find hash in the user"s profile
        resp = self.simulate_post(
            self.url,
            body=json.dumps({"username": username}),
            **req_params,
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["validated"], False)
