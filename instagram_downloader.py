#!/usr/bin/env python3
"""
Instagram Media Downloader
A lightweight Python script to extract high-quality media URLs from public Instagram posts.

Author: Instaboost Team
License: MIT
Version: 1.1.0
"""

import re
import sys
import argparse
from urllib.request import Request, urlopen, ProxyHandler, build_opener
from urllib.error import URLError, HTTPError
from html import unescape


class InstagramDownloader:
    """
    Instagram Media Downloader
    
    Extract media URLs from public Instagram posts by parsing Open Graph meta tags.
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
        self._opener = self._build_opener(proxy)
    
    def _build_opener(self, proxy):
        """
        Build URL opener with optional proxy configuration
        
        Args:
            proxy (str|None): Proxy URL string
            
        Returns:
            urllib opener instance
        """
        if not proxy:
            return None
        
        # Parse proxy URL to determine protocol
        if proxy.startswith('socks'):
            # SOCKS proxy requires requests library
            try:
                import requests
                self._use_requests = True
                return None  # Will use requests directly
            except ImportError:
                raise ImportError(
                    'SOCKS proxy support requires the requests library.\n'
                    'Install it with: pip install requests[socks]\n'
                    'Or use an HTTP proxy instead (no extra dependencies needed).'
                )
        else:
            # HTTP/HTTPS proxy — works with stdlib urllib, zero extra deps
            self._use_requests = False
            proxy_dict = {
                'http': proxy,
                'https': proxy,
            }
            proxy_handler = ProxyHandler(proxy_dict)
            return build_opener(proxy_handler)
    
    def download(self, url):
        """
        Download media from a public Instagram post URL
        
        Args:
            url (str): Instagram post URL (e.g., https://www.instagram.com/p/ABC123/)
            
        Returns:
            dict: {'type': 'image'|'video', 'url': '...', 'thumbnail': '...' (video only)}
            
        Raises:
            ValueError: If URL is invalid
            Exception: On network errors or media not found
        """
        if not self._is_valid_url(url):
            raise ValueError(
                'Invalid Instagram URL. Please provide a valid post URL '
                '(e.g., https://www.instagram.com/p/ABC123/)'
            )
        
        html = self._fetch_html(url)
        media = self._parse_media(html)
        
        if not media:
            raise Exception(
                'Could not extract media from this post. It may be private, '
                'deleted, or Instagram has updated their HTML structure.'
            )
        
        return media
    
    def _is_valid_url(self, url):
        """Validate Instagram post URL"""
        pattern = r'^https?://(www\.)?instagram\.com/(p|reel|tv)/[a-zA-Z0-9_-]+/?'
        return bool(re.match(pattern, url))
    
    def _fetch_html(self, url):
        """
        Fetch HTML content, routing through proxy if configured
        
        Args:
            url (str): Instagram post URL
            
        Returns:
            str: HTML content
        """
        headers = {
            'User-Agent': self.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # SOCKS proxy path — uses requests library
        if self.proxy and getattr(self, '_use_requests', False):
            return self._fetch_with_requests(url, headers)
        
        # HTTP proxy or direct — uses stdlib urllib
        return self._fetch_with_urllib(url, headers)
    
    def _fetch_with_urllib(self, url, headers):
        """Fetch using urllib (HTTP proxy or direct connection)"""
        request = Request(url, headers=headers)
        
        try:
            opener = self._opener if self._opener else urlopen
            
            if self._opener:
                response = self._opener.open(request, timeout=self.TIMEOUT)
                html = response.read().decode('utf-8')
                response.close()
                return html
            else:
                with urlopen(request, timeout=self.TIMEOUT) as response:
                    return response.read().decode('utf-8')
                    
        except HTTPError as e:
            self._handle_http_error(e.code)
        except URLError as e:
            raise Exception(f'Network error: {e.reason}')
    
    def _fetch_with_requests(self, url, headers):
        """Fetch using requests library (SOCKS proxy path)"""
        import requests
        
        proxies = {
            'http': self.proxy,
            'https': self.proxy,
        }
        
        try:
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=self.TIMEOUT
            )
            self._handle_http_error(response.status_code)
            return response.text
            
        except requests.exceptions.ConnectionError as e:
            raise Exception(f'Network error (proxy may be unreachable): {e}')
        except requests.exceptions.Timeout:
            raise Exception('Request timed out')
    
    def _handle_http_error(self, status_code):
        """Raise appropriate exception for HTTP error codes"""
        if status_code == 404:
            raise Exception(
                'Post not found. The URL may be incorrect or the post has been deleted.'
            )
        elif status_code == 403:
            raise Exception(
                'Access denied by Instagram. '
                'Try using a different proxy or wait before retrying.'
            )
        elif status_code == 429:
            raise Exception(
                'Rate limited by Instagram. '
                'Use a proxy to rotate IPs or consider the Instaboost API: https://instaboost.ge'
            )
        elif status_code != 200:
            raise Exception(f'HTTP error: {status_code}')
    
    def _parse_media(self, html):
        """Parse og:video and og:image meta tags from HTML"""
        media = {}
        
        # Check for video first
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
            # Fallback to image
            image_match = re.search(
                r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']',
                html, re.IGNORECASE
            )
            if image_match:
                media['type'] = 'image'
                media['url'] = unescape(image_match.group(1))
        
        return media
    
    def get_media_info(self, url):
        """Alias for download() — useful for preview workflows"""
        return self.download(url)


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
        version='Instagram Downloader 1.1.0'
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
        print(f'Type: {media["type"]}')
        print(f'URL: {media["url"]}')
        
        if 'thumbnail' in media:
            print(f'Thumbnail: {media["thumbnail"]}')
            
    except Exception as e:
        print(f'\n✗ Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
