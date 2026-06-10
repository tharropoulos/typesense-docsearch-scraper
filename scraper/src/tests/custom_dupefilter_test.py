import pytest
from scrapy.http import Request
from scrapy.utils.misc import build_from_crawler
from scrapy.utils.test import get_crawler

from ..custom_dupefilter import CustomDupeFilter


@pytest.fixture
def build_dupefilter():
    instances = []

    def _build(use_anchors):
        crawler = get_crawler(
            settings_dict={
                "DUPEFILTER_USE_ANCHORS": use_anchors,
            }
        )
        df = build_from_crawler(CustomDupeFilter, crawler)
        instances.append(df)
        return df

    yield _build

    for df in instances:
        df.close("finished")


def test_use_anchors_flag_propagates_through_build_from_crawler(build_dupefilter):
    """Scrapy 2.12+ uses build_from_crawler; the flag must survive that path."""
    df = build_dupefilter(use_anchors=True)
    assert df.use_anchors is True


def test_anchored_urls_are_distinct_when_use_anchors_enabled(build_dupefilter):
    df = build_dupefilter(use_anchors=True)

    assert df.request_seen(Request("https://example.com/page#a")) is False
    assert df.request_seen(Request("https://example.com/page#b")) is False


def test_anchored_urls_collapse_when_use_anchors_disabled(build_dupefilter):
    df = build_dupefilter(use_anchors=False)

    assert df.request_seen(Request("https://example.com/page#a")) is False
    assert df.request_seen(Request("https://example.com/page#b")) is True
