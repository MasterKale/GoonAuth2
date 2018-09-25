import falcon
import json
import uuid


def get_json(req: falcon.Request) -> dict:
    """
    Turn a request stream into a JSON dictionary
    """
    try:
        body = req.stream.read()
        raw_json = json.loads(body.decode('utf-8'))
    except Exception as ex:
        ex_type = type(ex)
        str_error = str(ex)

        if ex_type is ValueError:
            str_error = 'You must specify a JSON-encoded body'

        raise falcon.HTTPBadRequest('JSON Error', str_error)

    return raw_json


def get_username(body: dict) -> str:
    """
    Pass in the request body (the output from json.loads()) and check for a username
    """
    if 'username' not in body:
        raise falcon.HTTPMissingParam('username')

    if not body['username']:
        raise falcon.HTTPInvalidParam(
            'Username cannot be blank',
            'username'
        )

    return body['username'].replace(' ', '%20')


def get_hash() -> str:
    """
    Return a 32-character long random string
    """
    return str(uuid.uuid4()).replace('-', '')[:32]
