import unittest

import kidibox


class TestResponse(object):
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


class TestSession(kidibox.session.Session):
    def get(self, url, **kwargs):
        if url in [
                    'foobar.com/torrents',
                    'foobar.com/torrents/1',
                    'foobar.com/torrents/1/files/0/token',
                ]:
            return TestResponse({'test': 'ok'})
        else:
            return TestResponse({
                'test': 'failed',
                'url': url,
            })

    def post(self, url, **kwargs):
        if url == 'foobar.com/authenticate':
            return TestResponse({'token': 'xxx'})
        elif url in [
                    'foobar.com/register',
                    'foobar.com/torrents/link',
                ]:
            return TestResponse(kwargs['json'])
        else:
            return TestResponse({
                'test': 'failed',
                'url': url,
            })


class TestClient(kidibox.client.Client):
    session_class = TestSession


class ClientTestCase(unittest.TestCase):
    def test_register(self):
        client = TestClient("foobar.com", "foo", "bar")
        result = client.register()
        self.assertEqual(result, {
            'username': 'foo',
            'password': 'bar',
        })

    def test_authenticate(self):
        client = TestClient("foobar.com", "foo", "bar")
        self.assertFalse(client.is_authenticated())
        client.authenticate()
        self.assertEqual(client.session.token, 'xxx')
        self.assertTrue(client.is_authenticated())

    def test_require_authentication(self):
        client = TestClient("foobar.com", "foo", "bar")
        self.assertFalse(client.is_authenticated())
        result = client.list()
        self.assertTrue(client.is_authenticated())

    def test_list(self):
        client = TestClient("foobar.com", "foo", "bar")
        client.authenticate()
        result = client.list()
        self.assertEqual(result, {'test': 'ok'})

    def test_create(self):
        client = TestClient("foobar.com", "foo", "bar")
        client.authenticate()
        result = client.create('xxx')
        self.assertEqual(result, {'link': 'xxx'})

    def test_get(self):
        client = TestClient("foobar.com", "foo", "bar")
        client.authenticate()
        result = client.get(1)
        self.assertEqual(result, {'test': 'ok'})

    def test_get_token(self):
        client = TestClient("foobar.com", "foo", "bar")
        client.authenticate()
        result = client.get_token(1, 0)
        self.assertEqual(result, {'test': 'ok'})
