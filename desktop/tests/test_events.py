# desktop/tests/test_events.py

import os
import sys

# Ensure the `desktop/` directory is on sys.path so we can import gsp_toolkit
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path  = os.path.join(repo_root, "src")
sys.path.insert(0, src_path)

import pytest
from gsp_toolkit.events import subscribe, publish, clear_subscribers

def test_publish_and_subscribe():
    clear_subscribers()
    results = []
    def handler(evt, data):
        results.append((evt, data))
    subscribe(handler)
    publish("status", "OK")
    publish("progress", 42)
    assert results == [("status", "OK"), ("progress", 42)]

def test_duplicate_subscribe():
    clear_subscribers()
    results = []
    def handler(evt, data):
        results.append((evt, data))
    subscribe(handler)
    subscribe(handler)
    publish("x", 1)
    assert results == [("x", 1)]

def test_exception_in_subscriber():
    clear_subscribers()
    events = []
    def bad(evt, data):
        raise RuntimeError("fail")
    def good(evt, data):
        events.append((evt, data))
    subscribe(bad)
    subscribe(good)
    # Should not raise, and the good handler still runs
    publish("test", {"a": 1})
    assert events == [("test", {"a": 1})]
