import unittest
from src.utils.downloader import BiliDownloader

class TestBiliDownloader(unittest.TestCase):
    def setUp(self):
        self.downloader = BiliDownloader()

    def test_extract_bvid(self):
        test_cases = [
            ("https://www.bilibili.com/video/BV1xx411c7mD", "BV1xx411c7mD"),
            ("BV1xx411c7mD", "BV1xx411c7mD"),
            ("https://www.bilibili.com/video/BV1xx411c7mD?p=1", "BV1xx411c7mD"),
        ]
        
        for input_url, expected_bvid in test_cases:
            with self.subTest(input_url=input_url):
                result = self.downloader.extract_bvid(input_url)
                self.assertEqual(result, expected_bvid)

    def test_invalid_url(self):
        with self.assertRaises(ValueError):
            self.downloader.extract_bvid("https://www.example.com")

if __name__ == '__main__':
    unittest.main() 