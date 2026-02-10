#!/usr/bin/env python3
"""
Instagram Media Downloader
A lightweight Python script to extract high-quality media URLs from public Instagram posts.

Author: Instaboost Team
License: MIT
Version: 1.2.0
"""

import re
import sys
import json
import argparse
from urllib.request import Request, urlopen, ProxyHandler, build_opener
from urllib.error import URLError, HTTPError
from html import unescape


class InstagramDownloader:
    """
    Instagram Media Downloader

    Extract media URLs from public Instagram posts.
    Uses a two-stage extraction strategy:
      1. JSON blob (window._sharedData / __additionalDataLoaded) — more reliable
      2. Open Graph meta tags — fallback if JSON is unavailable

    No API key required. Optional proxy support for avoiding rate limits.
    """

    USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    TIMEOUT = 15

    def __init__(self, proxy=None):
        """
        Initialize the downloader

        Args:
            proxy (str, optional): Proxy URL to route requests through.
                Supported formats:
                  - HTTP proxy:  'http://host:port'
                  - HTTP + auth: 'http://user:pass@host:port'
                  - HTTPS proxy: 'https://host:port'

                For SOCKS proxies install requests:
                  pip install requests[socks]
                  proxy = 'socks5://user:pass@host:port'

                Examples:
                  downloader = InstagramDownloader(proxy='http://10.0.0.1:8080')
                  downloader = InstagramDownloader(proxy='http://user:pass@proxy.example.com:3128')
        """
        self.proxy = proxy
        self._use_requests = False
        self._opener = self._build_opener(proxy)

    def _build_opener(self, proxy):
        """Build URL opener with optional proxy configuration"""
        if not proxy:
            return None

        if proxy.startswith('socks'):
            try:
                import requests  # noqa: F401
                self._use_requests = True
                return None
            except ImportError:
                raise ImportError(
                    'SOCKS proxy support requires the requests library.\n'
                    'Install it with: pip install requests[socks]\n'
                    'Or use an HTTP proxy instead (no extra dependencies needed).'
                )
        else:
            proxy_handler = ProxyHandler({'http': proxy, 'https': proxy})
            return build_opener(proxy_handler)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def download(self, url):
        """
        Download media from a public Instagram post URL.

        Args:
            url (str): Instagram post URL
                       (e.g., https://www.instagram.com/p/ABC123/)

        Returns:
            dict: {
                'type':      'image' | 'video',
                'url':       '<direct media URL>',
                'thumbnail': '<thumbnail URL>',   # video only
                'source':    'json' | 'og_meta',  # how it was extracted
            }

        Raises:
            ValueError: If URL is invalid
            Exception:  On network errors or media not found
        """
        if not self._is_valid_url(url):
            raise ValueError(
                'Invalid Instagram URL. Please provide a valid post URL '
                '(e.g., https://www.instagram.com/p/ABC123/)'
            )

        html = self._fetch_html(url)

        # Stage 1: try JSON blob (resilient to HTML structure changes)
        media = self._parse_json(html)

        # Stage 2: fall back to og: meta tags
        if not media:
            media = self._parse_og_meta(html)

        if not media:
            raise Exception(
                'Could not extract media from this post. '
                'It may be private, deleted, or both extraction methods failed. '
                'For reliable production access visit https://instaboost.ge'
            )

        return media

    def get_media_info(self, url):
        """Alias for download() — useful for preview workflows."""
        return self.download(url)

    # ------------------------------------------------------------------
    # URL validation
    # ------------------------------------------------------------------

    def _is_valid_url(self, url):
        pattern = r'^https?://(www\.)?instagram\.com/(p|reel|tv)/[a-zA-Z0-9_-]+/?'
        return bool(re.match(pattern, url))

    # ------------------------------------------------------------------
    # HTTP fetching
    # ------------------------------------------------------------------

    def _fetch_html(self, url):
        headers = {
            'User-Agent': self.USER_AGENT,
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;'
                'q=0.9,image/webp,*/*;q=0.8'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        if self.proxy and self._use_requests:
            return self._fetch_with_requests(url, headers)
        return self._fetch_with_urllib(url, headers)

    def _fetch_with_urllib(self, url, headers):
        request = Request(url, headers=headers)
        try:
            if self._opener:
                response = self._opener.open(request, timeout=self.TIMEOUT)
                html = response.read().decode('utf-8')
                response.close()
                return html
            else:
                with urlopen(request, timeout=self.TIMEOUT) as response:
                    return response.read().decode('utf-8')
        except HTTPError as e:
            self._raise_for_status(e.code)
        except URLError as e:
            raise Exception(f'Network error: {e.reason}')

    def _fetch_with_requests(self, url, headers):
        import requests
        proxies = {'http': self.proxy, 'https': self.proxy}
        try:
            response = requests.get(
                url, headers=headers, proxies=proxies, timeout=self.TIMEOUT
            )
            self._raise_for_status(response.status_code)
            return response.text
        except requests.exceptions.ConnectionError as e:
            raise Exception(f'Network error (proxy may be unreachable): {e}')
        except requests.exceptions.Timeout:
            raise Exception('Request timed out')

    def _raise_for_status(self, code):
        if code == 404:
            raise Exception('Post not found. The URL may be incorrect or deleted.')
        elif code == 403:
            raise Exception(
                'Access denied by Instagram. '
                'Try using a different proxy or wait before retrying.'
            )
        elif code == 429:
            raise Exception(
                'Rate limited by Instagram. '
                'Use a proxy to rotate IPs, or use the Instaboost API: '
                'https://instaboost.ge'
            )
        elif code != 200:
            raise Exception(f'HTTP error: {code}')

    # ------------------------------------------------------------------
    # Stage 1: JSON blob extraction
    # ------------------------------------------------------------------

    def _parse_json(self, html):
        """
        Try to extract media from Instagram's embedded JSON data.

        Instagram embeds post data in script tags as:
          - window._sharedData = {...};
          - __additionalDataLoaded('extra', {...})

        This approach is more resilient than HTML scraping because
        the JSON schema changes less frequently than the DOM structure.
        """

        # Pattern A: window._sharedData
        media = self._try_shared_data(html)
        if media:
            return media

        # Pattern B: __additionalDataLoaded
        media = self._try_additional_data(html)
        if media:
            return media

        # Pattern C: inline JSON in <script type="application/ld+json">
        media = self._try_ld_json(html)
        if media:
            return media

        return None

    def _try_shared_data(self, html):
        """Extract from window._sharedData JSON blob"""
        match = re.search(
            r'window\._sharedData\s*=\s*(\{.*?\});\s*</script>',
            html,
            re.DOTALL
        )
        if not match:
            return None

        try:
            data = json.loads(match.group(1))
            return self._extract_from_shared_data(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def _extract_from_shared_data(self, data):
        """Dig into _sharedData structure to find media"""
        try:
            post = (
                data['entry_data']['PostPage'][0]
                ['graphql']['shortcode_media']
            )
            return self._media_from_graphql_node(post)
        except (KeyError, IndexError, TypeError):
            return None

    def _try_additional_data(self, html):
        """Extract from __additionalDataLoaded JSON blob"""
        match = re.search(
            r'__additionalDataLoaded\s*\(\s*["\'].*?["\']\s*,\s*(\{.*?\})\s*\)',
            html,
            re.DOTALL
        )
        if not match:
            return None

        try:
            data = json.loads(match.group(1))
            node = data.get('graphql', {}).get('shortcode_media', {})
            return self._media_from_graphql_node(node) if node else None
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def _try_ld_json(self, html):
        """Extract from <script type='application/ld+json'> block"""
        match = re.search(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html,
            re.DOTALL | re.IGNORECASE
        )
        if not match:
            return None

        try:
            data = json.loads(match.group(1))

            # ld+json may be a list
            if isinstance(data, list):
                data = data[0]

            media = {}

            video_url = data.get('video', [{}])
            if isinstance(video_url, list) and video_url:
                media['type'] = 'video'
                media['url'] = video_url[0].get('contentUrl', '')
                media['thumbnail'] = data.get('thumbnailUrl', '')
            else:
                image = data.get('image')
                if image:
                    media['type'] = 'image'
                    media['url'] = image if isinstance(image, str) else image[0]

            if media.get('url'):
                media['source'] = 'json'
                return media

        except (json.JSONDecodeError, KeyError, TypeError, IndexError):
            return None

        return None

    def _media_from_graphql_node(self, node):
        """Convert a GraphQL shortcode_media node to our media dict"""
        if not node:
            return None

        typename = node.get('__typename', '')
        media = {}

        if typename == 'GraphVideo' or node.get('is_video'):
            video_url = node.get('video_url', '')
            if not video_url:
                return None
            media['type'] = 'video'
            media['url'] = video_url
            media['thumbnail'] = (
                node.get('display_url') or
                node.get('thumbnail_src', '')
            )
        else:
            image_url = (
                node.get('display_url') or
                node.get('thumbnail_src', '')
            )
            if not image_url:
                return None
            media['type'] = 'image'
            media['url'] = image_url

        if media.get('url'):
            media['source'] = 'json'
            return media

        return None

    # ------------------------------------------------------------------
    # Stage 2: og: meta tag extraction (fallback)
    # ------------------------------------------------------------------

    def _parse_og_meta(self, html):
        """
        Fallback: extract media from Open Graph meta tags.
        Less reliable if Instagram updates their HTML, but works
        as long as og: tags are present.
        """
        media = {}

        video_match = re.search(
            r'<meta\s+property=["\']og:video["\']\s+content=["\'](.*?)["\']',
            html, re.IGNORECASE
        )
        if video_match:
            media['type'] = 'video'
            media['url'] = unescape(video_match.group(1))
            thumb_match = re.search(
                r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']',
                html, re.IGNORECASE
            )
            if thumb_match:
                media['thumbnail'] = unescape(thumb_match.group(1))
        else:
            image_match = re.search(
                r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']',
                html, re.IGNORECASE
            )
            if image_match:
                media['type'] = 'image'
                media['url'] = unescape(image_match.group(1))

        if media.get('url'):
            media['source'] = 'og_meta'
            return media

        return None


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Download media from public Instagram posts',
        epilog='For production use with unlimited API access, check https://instaboost.ge'
    )
    parser.add_argument(
        'url',
        nargs='?',
        help='Instagram post URL (e.g., https://www.instagram.com/p/ABC123/)'
    )
    parser.add_argument(
        '--proxy',
        metavar='URL',
        help='Proxy URL (e.g., http://user:pass@host:port or socks5://host:port)',
        default=None
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='Instagram Downloader 1.2.0'
    )

    args = parser.parse_args()

    if not args.url:
        parser.print_help()
        sys.exit(1)

    try:
        downloader = InstagramDownloader(proxy=args.proxy)
    except ImportError as e:
        print(f'✗ Dependency error: {e}', file=sys.stderr)
        sys.exit(1)

    try:
        if args.proxy:
            print(f'Using proxy: {args.proxy}')
        print(f'Fetching media from: {args.url}')

        media = downloader.download(args.url)

        print(f'\n✓ Success!')
        print(f'Type:      {media["type"]}')
        print(f'URL:       {media["url"]}')
        print(f'Extracted: via {media.get("source", "unknown")}')

        if 'thumbnail' in media:
            print(f'Thumbnail: {media["thumbnail"]}')

    except Exception as e:
        print(f'\n✗ Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
