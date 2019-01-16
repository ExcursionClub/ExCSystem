import unittest

from selenium import webdriver


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_get_browser_title(self):
        self.browser.get('http://localhost:8000/kiosk')
        self.assertIn('Kiosk', self.browser.title)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
