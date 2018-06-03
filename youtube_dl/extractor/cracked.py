from __future__ import unicode_literals

import re
import datetime
import calendar

from .common import InfoExtractor
from .youtube import YoutubeIE
from ..utils import (
    parse_iso8601,
    str_to_int,
    int_or_none,
)


class CrackedIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?cracked\.com/video_(?P<id>\d+)_[\da-z-]+\.html'
    _TESTS = [{
        'url': 'http://www.cracked.com/video_19070_if-animal-actors-got-e21-true-hollywood-stories.html',
        'md5': '89b90b9824e3806ca95072c4d78f13f7',
        'info_dict': {
            'id': '19070',
            'ext': 'mp4',
            'title': 'If Animal Actors Got E! True Hollywood Stories',
            'timestamp': 1404950400,
            'upload_date': '20140710',
        }
    }, {
        # youtube embed
        'url': 'http://www.cracked.com/video_19006_4-plot-holes-you-didnt-notice-in-your-favorite-movies.html',
        'md5': '784f07e398eb09423262722a64d180b9',
        'info_dict': {
            'id': 'EjI00A3rZD0',
            'ext': 'mp4',
            'title': "4 Plot Holes You Didn't Notice in Your Favorite Movies - The Spit Take",
            'description': 'md5:c603708c718b796fe6079e2b3351ffc7',
            'upload_date': '20140725',
            'uploader_id': 'Cracked',
            'uploader': 'Cracked',
        }
    }]

    @staticmethod
    def _parse_us_time(month, day, year):
        month_to_int = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
        m = month_to_int.get(month)
        y = int_or_none(year)
        d = int_or_none(day)
        if m and d and y:
            return calendar.timegm(datetime.date(y, m, d).timetuple())

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)

        youtube_url = YoutubeIE._extract_url(webpage)
        if youtube_url:
            return self.url_result(youtube_url, ie=YoutubeIE.ie_key())

        video_url = self._html_search_regex(
            [r'var\s+CK_vidSrc\s*=\s*"([^"]+)"', r'<video\s+src="([^"]+)"'],
            webpage, 'video URL')

        title = self._search_regex(
            [r'property="?og:title"?\s+content="([^"]+)"', r'class="?title"?>([^<]+)'],
            webpage, 'title')

        description = self._search_regex(
            r'name="?(?:og:)?description"?\s+content="([^"]+)"',
            webpage, 'description', default=None)

        timestamp = self._html_search_regex(
            r'"date"\s*:\s*"([^"]+)"', webpage, 'upload date', default=None)
        if timestamp:
            timestamp = parse_iso8601(timestamp[:-6])
        else:
            time_match = re.search(
                r'<li[^>]+class=["\']?[^"\']*date-published[^"\']*["\']?[^>]*>(\w+)\s*(\d+),\s*(\d+)</li>', webpage)
            if time_match:
                timestamp = self._parse_us_time(time_match.group(1), time_match.group(2), time_match.group(3))

        view_count = str_to_int(self._html_search_regex(
            r'<span\s+class="?views"? id="?viewCounts"?>([\d,\.]+) Views</span>',
            webpage, 'view count', default=None))
        comment_count = str_to_int(self._html_search_regex(
            r'<span\s+(?:id="?commentCounts"?|class="?comments-count"?)>([\d,\.]+)</',
            webpage, 'comment count', fatal=False))

        m = re.search(r'_(?P<width>\d+)X(?P<height>\d+)\.mp4$', video_url)
        if m:
            width = int(m.group('width'))
            height = int(m.group('height'))
        else:
            width = height = None

        return {
            'id': video_id,
            'url': video_url,
            'title': title,
            'description': description,
            'timestamp': timestamp,
            'view_count': view_count,
            'comment_count': comment_count,
            'height': height,
            'width': width,
        }
