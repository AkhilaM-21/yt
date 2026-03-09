
import pytest
import re
from datetime import datetime, timedelta
# Import the functions to be tested.
# Assuming backend is in python path or we append it.
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fb import parse_facebook_date, clean_facebook_url

def test_parse_facebook_date_garbage():
    garbage = "Poor baby monkey, hope to meet his new mom!..."
    assert parse_facebook_date(garbage) == ""

    garbage2 = "Open reel in Reels Viewer"
    assert parse_facebook_date(garbage2) == ""

def test_parse_facebook_date_valid():
    # Mock datetime.now() if necessary, but for relative dates we can check expected range or format

    # "2 days" -> Should return a date string ~2 days ago
    res = parse_facebook_date("2 days")
    assert res != ""
    dt = datetime.strptime(res, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    diff = now - dt
    # Allow small delta
    assert 1.9 < diff.days + diff.seconds/86400 < 2.1

    # "Just now"
    res = parse_facebook_date("Just now")
    dt = datetime.strptime(res, "%Y-%m-%d %H:%M:%S")
    diff = datetime.now() - dt
    assert diff.total_seconds() < 5

    # explicit date "June 15 at 5:30 PM" (Assuming current year)
    res = parse_facebook_date("June 15 at 5:30 PM")
    assert "06-15" in res
    assert "17:30" in res

def test_clean_facebook_url():
    # Basic clean
    assert clean_facebook_url("https://www.facebook.com/reel/123/?s=1") == "https://www.facebook.com/reel/123/"

    # Permalink preservation
    url = "https://www.facebook.com/permalink.php?story_fbid=123&id=456"
    assert clean_facebook_url(url) == url

    # Profile post preservation
    url2 = "https://www.facebook.com/profile.php?story_fbid=123&id=456"
    assert clean_facebook_url(url2) == url2

    # Empty
    assert clean_facebook_url(None) == ""
