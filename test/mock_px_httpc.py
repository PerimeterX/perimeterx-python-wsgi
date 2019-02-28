import unittest

class MockHttpC(unittest.TestCase):

    def __init__(self, full_url, config, method, body):
        self.full_url = full_url
        self.config = config
        self.method = method
        self.body = body

    def send(self, full_url, config, method, body, headers):
        asrt = unittest.TestCase
        asrt.assertEqual(full_url, self.full_url)
        asrt.assertEqual(config, self.config)
        asrt.assertEqual(method, self.method)
        asrt.assertEqual(body, self.body)
        asrt.assertEqual(headers, self.headers)
