# coding: utf-8
from __future__ import unicode_literals

import json
import re

from .common import InfoExtractor
from .facebook import FacebookIE
from .youtube import YoutubeIE


class BuzzFeedIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?buzzfeed\.com/[^?#]*?/(?P<id>[^?#]+)'
    _TESTS = [{
        'url': 'http://www.buzzfeed.com/abagg/this-angry-ram-destroys-a-punching-bag-like-a-boss?utm_term=4ldqpia',
        'info_dict': {
            'id': 'this-angry-ram-destroys-a-punching-bag-like-a-boss',
            'title': 'This Angry Ram Destroys A Punching Bag Like A Boss',
            'description': 'Rambro!',
        },
        'playlist': [{
            'info_dict': {
                'id': 'aVCR29aE_OQ',
                'ext': 'mp4',
                'title': 'Angry Ram destroys a punching bag..',
                'description': 'md5:c59533190ef23fd4458a5e8c8c872345',
                'upload_date': '20141024',
                'uploader_id': 'Buddhanz1',
                'uploader': 'Angry Ram',
            }
        }]
    }, {
        'url': 'http://www.buzzfeed.com/sheridanwatson/look-at-this-cute-dog-omg?utm_term=4ldqpia',
        'params': {
            'skip_download': True,  # Got enough YouTube download tests
        },
        'info_dict': {
            'id': 'look-at-this-cute-dog-omg',
            'description': 're:Munchkin the Teddy Bear is back ?!',
            'title': 'You Need To Stop What You\'re Doing And Watching This Dog Walk On A Treadmill',
        },
        'playlist': [{
            'info_dict': {
                'id': 'mVmBL8B-In0',
                'ext': 'mp4',
                'title': 're:Munchkin the Teddy Bear gets her exercise',
                'description': 'md5:28faab95cda6e361bcff06ec12fc21d8',
                'upload_date': '20141124',
                'uploader_id': 'CindysMunchkin',
                'uploader': 're:^Munchkin the',
            },
        }]
    }, {
        'url': 'http://www.buzzfeed.com/craigsilverman/the-most-adorable-crash-landing-ever#.eq7pX0BAmK',
        'info_dict': {
            'id': 'the-most-adorable-crash-landing-ever',
            'title': 'Watch This Baby Goose Make The Most Adorable Crash Landing',
            'description': 'This gosling knows how to stick a landing.',
        },
        'playlist': [{
            'md5': '2ca4672b84a6a9ab24561c847c8b82dc',
            'info_dict': {
                'id': '971793786185728',
                'ext': 'mp4',
                'title': 'We set up crash pads so that the goslings on our roof would have a safe landi...',
                'uploader': 'Calgary Outdoor Centre-University of Calgary',
                'upload_date': '20150511',
                'timestamp': 1431380091,
            },
        }],
        'add_ie': ['Facebook'],
    }]

    def _real_extract(self, url):
        playlist_id = self._match_id(url)
        webpage = self._download_webpage(url, playlist_id)

        all_buckets = re.findall(
            r'(?s)<div class="video-embed[^"]*"..*?rel:bf_bucket_data=\'([^\']+)\'',
            webpage)

        entries = []
        for bd_json in all_buckets:
            bd = json.loads(bd_json)
            video = bd.get('video') or bd.get('progload_video')
            if not video:
                continue
            entries.append(self.url_result(video['url']))

        facebook_urls = FacebookIE._extract_urls(webpage)
        entries.extend([
            self.url_result(facebook_url)
            for facebook_url in facebook_urls])

        youtube_a_hrefs = [m.group(1) for m in re.finditer(r'<a\s(?:href=[\'"]([^\'"]+)[\'"]|class=[\'"]([^\'"]+)[\'"]|[^>])*>', webpage)
                           if m.group(1) and m.group(2) and re.search(r'^https?://(?:[^.]*\.)?youtube\.com', m.group(1)) and 'subbuzz-youtube__thumb' in m.group(2)]
        entries.extend([
            self.url_result(youtube_url)
            for youtube_url in youtube_a_hrefs])
        

        return {
            '_type': 'playlist',
            'id': playlist_id,
            'title': self._og_search_title(webpage),
            'description': self._og_search_description(webpage),
            'entries': entries,
        }
