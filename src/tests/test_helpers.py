import unittest
import re
import json
from unittest.mock import MagicMock
from io import StringIO

import falcon

from src.helpers import get_hash, get_json, get_username


class GetHashTestCase(unittest.TestCase):
    def test_returns_str(self):
        returned = get_hash()
        self.assertEqual(type(returned), str)

    def test_returns_thirty_two_characters(self):
        returned = get_hash()
        self.assertEqual(len(returned), 32)

    def test_contains_only_numbers_and_letters(self):
        returned = get_hash()
        regex_alpha_num = re.compile("^[a-zA-Z0-9]*$")
        self.assertTrue(regex_alpha_num.match(returned) is not None)


class GetJsonTestCase(unittest.TestCase):
    req = MagicMock(spec=falcon.Request)
    stream = MagicMock(spec=StringIO)

    def setUp(self):
        # Fake a data stream Falcon prepares from an HTTP request
        self.stream.decode = MagicMock(return_value=json.dumps({"foo": "bar"}))
        # Prepare a Falcon-request-like mock value
        self.req.stream.read = MagicMock(return_value=self.stream)

    def test_returns_dict(self):
        returned = get_json(self.req)
        self.assertEqual(type(returned), dict)

    def test_returns_json_as_dict(self):
        returned = get_json(self.req)
        self.assertDictEqual({"foo": "bar"}, returned)

    def test_returns_400_on_empty_body(self):
        self.req.stream.read = MagicMock(return_value=None)
        with self.assertRaises(falcon.HTTPBadRequest):
            get_json(self.req)

    def test_returns_400_with_reason(self):
        self.stream.decode = MagicMock(side_effect=ValueError)
        with self.assertRaisesRegex(
            expected_regex="JSON-encoded body", expected_exception=falcon.HTTPBadRequest,
        ):
            get_json(self.req)


class GetUsernameTestCase(unittest.TestCase):
    pass
