import sys
import os
import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import re

# Ensure backend can be imported from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from backend.fb import parse_facebook_date, get_post_details_from_ancestors, clean_facebook_url
    from selenium.webdriver.common.by import By
except ImportError as e:
    # If we are running in an environment without dependencies installed, skip
    print(f"Skipping tests due to import error: {e}")
    parse_facebook_date = None

class TestFacebookScraper(unittest.TestCase):

    def setUp(self):
        if parse_facebook_date is None:
            self.skipTest("backend.fb could not be imported")

    def test_date_parsing(self):
        now = datetime.now()

        # 1. Just now
        self.assertAlmostEqual(
            datetime.strptime(parse_facebook_date("Just now"), "%Y-%m-%d %H:%M:%S"),
            now,
            delta=timedelta(seconds=10)
        )

        # 2. 2 hrs
        two_hours_ago = now - timedelta(hours=2)
        parsed = datetime.strptime(parse_facebook_date("2 hrs"), "%Y-%m-%d %H:%M:%S")
        self.assertAlmostEqual(parsed, two_hours_ago, delta=timedelta(seconds=60))

        # 3. Yesterday at HH:MM PM
        yesterday_10pm_str = "Yesterday at 10:00 PM"
        parsed_y_10pm = datetime.strptime(parse_facebook_date(yesterday_10pm_str), "%Y-%m-%d %H:%M:%S")

        expected_y_10pm = (now - timedelta(days=1)).replace(hour=22, minute=0, second=0, microsecond=0)
        self.assertEqual(parsed_y_10pm.date(), expected_y_10pm.date())
        self.assertEqual(parsed_y_10pm.hour, 22)
        self.assertEqual(parsed_y_10pm.minute, 0)

        # 4. June 15 at 5:30 PM (Implied Current Year)
        june_15_str = "June 15 at 5:30 PM"
        parsed_j15 = datetime.strptime(parse_facebook_date(june_15_str), "%Y-%m-%d %H:%M:%S")
        self.assertEqual(parsed_j15.month, 6)
        self.assertEqual(parsed_j15.day, 15)
        self.assertEqual(parsed_j15.hour, 17)
        self.assertEqual(parsed_j15.minute, 30)

        # Expectation logic:
        june_15_this_year = datetime(now.year, 6, 15, 17, 30)
        if june_15_this_year > now + timedelta(days=2):
             expected_year = now.year - 1
        else:
             expected_year = now.year

        self.assertEqual(parsed_j15.year, expected_year)

    def test_url_extraction_scoring(self):
        # Mock Driver
        mock_driver = MagicMock()

        # Mock Elements
        link_garbage = MagicMock()
        link_garbage.get_attribute.side_effect = lambda x: "https://facebook.com/hashtag/garbage" if x == "href" else ""
        link_garbage.text = "#garbage"
        link_garbage.find_elements.return_value = []

        link_post = MagicMock()
        link_post.get_attribute.side_effect = lambda x: "https://facebook.com/username/posts/12345" if x == "href" else ""
        link_post.text = "Some text"
        link_post.find_elements.return_value = []

        link_timestamp = MagicMock()
        link_timestamp.get_attribute.side_effect = lambda x: "https://facebook.com/username/posts/99999" if x == "href" else ("2 hrs" if x == "aria-label" else "")
        link_timestamp.text = "2 hrs"
        link_timestamp.find_elements.return_value = []

        parent = MagicMock()
        parent.find_elements.return_value = [link_garbage, link_post, link_timestamp]
        parent.get_attribute.return_value = ""

        caption_el = MagicMock()
        caption_el.find_element.return_value = parent
        caption_el.find_elements.return_value = []
        caption_el.get_attribute.return_value = ""

        mock_driver.execute_script.side_effect = lambda script, el: el.text if hasattr(el, 'text') else ""

        url, date = get_post_details_from_ancestors(mock_driver, caption_el)

        self.assertEqual(url, "https://facebook.com/username/posts/99999")
        self.assertEqual(date, "2 hrs")

if __name__ == "__main__":
    unittest.main()
