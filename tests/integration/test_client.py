import os
import time
import unittest

import kidibox
from kidibox.exceptions import ApiError


class ClientTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = os.environ['KIDIBOX_URL']
        cls.username = os.environ.get('KIDIBOX_USERNAME', 'test-runner')
        cls.password = os.environ.get('KIDIBOX_PASSWORD', 'test-runner')
        cls.link = os.environ['KIDIBOX_LINK']
        cls.client = kidibox.connect(
            cls.url, cls.username, cls.password, verify=False)

    def wait_download_complete(self):
        while True:
            results = self.client.get(self.torrent_id)
            if results['percentDone'] == 1:
                break
            time.sleep(1)

    def test_00_register(self):
        try:
            self.client.register()
        except ApiError as exc:
            if exc.response.status_code == 409:
                self.skipTest("already registered")
            raise

    def test_10_authenticate(self):
        self.assertFalse(self.client.is_authenticated())
        self.client.authenticate()
        self.assertTrue(self.client.is_authenticated())

    def test_20_create(self):
        try:
            result = self.client.create(self.link)
        except ApiError as exc:
            if exc.response.status_code == 409:
                self.skipTest("torrent already exists")
            raise
        self.assertIn('id', result)
        type(self).torrent_id = result['id']

    def test_30_duplicate(self):
        with self.assertRaises(ApiError) as cm:
            result = self.client.create(self.link)
        self.assertEqual(cm.exception.response.status_code, 409)

    def test_50_get(self):
        if not hasattr(self, 'torrent_id'):
            self.skipTest("torrent not loaded")
        result = self.client.get(self.torrent_id)
        self.assertEqual(
            set(result.keys()),
            set("""
                id name hashString createdAt userName rateDownload files status
                percentDone downloadedEver totalSize rateUpload uploadedEver
            """.split()))

    def test_50_list(self):
        result = self.client.list()
        self.assertIsInstance(result['torrents'], list)

    def test_50_get_token(self):
        if not hasattr(self, 'torrent_id'):
            self.skipTest("torrent not loaded")
        self.wait_download_complete()
        result = self.client.get_token(self.torrent_id, 0)
        self.assertIn('token', result)
        type(self).token = result['token']

    def test_60_download(self):
        if not hasattr(self, 'token'):
            self.skipTest("token not available")
        filename, content_it = self.client.download(self.token)
        self.assertIsInstance(filename, str)
        content = b''.join(content_it)
        self.assertNotEqual(content, b'')
