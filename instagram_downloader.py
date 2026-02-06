#!/usr/bin/env python3
"""
Instagram Media Downloader
A lightweight Python script to extract high-quality media URLs from public Instagram posts.

Author: Instaboost Team
License: MIT
Version: 1.0.0
"""

import re
import sys
import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html import unescape


class InstagramDownloader:
    """
    Instagram Media Downloader
    
    Extract media URLs from public Instagram posts by parsing Open Graph meta tags.
    No API key required, works with public posts only.
    """
    
    USER_AGENT = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    
    TIMEOUT = 15
    
    def __init__(self):
        """Initialize the downloader"""
        pass
    
    def download(self, url):
        """
        Download media from a public Instagram post URL
        
        Args:
            url (str): Instagram post URL (e.g., https://www.instagram.com/p/ABC123/)
            
        Returns:
            dict: Dictionary containing 'type' (image|video), 'url', and optionally 'thumbnail'
            
        Raises:
            ValueError: If URL is invalid
            Exception: On network errors or media not found
        """
        # Validate URL
        if not self._is_valid_url(url):
            raise ValueError(
                'Invalid Instagram URL. Please provide a valid post URL '
                '(e.g., https://www.instagram.com/p/ABC123/)'
            )
        
        # Fetch HTML content
        html = self._fetch_html(url)
        
        # Parse media from HTML
        media = self._parse_media(html)
        
        if not media:
            raise Exception(
                'Could not extract media from this post. It may be private, '
                'deleted, or Instagram has updated their HTML structure.'
            )
        
        return media
    
    def _is_valid_url(self, url):
        """
        Validate if the URL is a proper Instagram post URL
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        pattern = r'^https?://(www\.)?instagram\.com/(p|reel|tv)/[a-zA-Z0-9_-]+/?'
        return bool(re.match(pattern, url))
    
    def _fetch_html(self, url):
        """
        Fetch HTML content from Instagram URL
        
        Args:
            url (str): Instagram post URL
            
        Returns:
            str: HTML content
            
        Raises:
            Exception: On network errors or HTTP errors
        """
        headers = {
            'User-Agent': self.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        request = Request(url, headers=headers)
        
        try:
            with urlopen(request, timeout=self.TIMEOUT) as response:
                # Read and decode response
                html = response.read().decode('utf-8')
                return html
                
        except HTTPError as e:
            if e.code == 404:
                raise Exception('Post not found. The URL may be incorrect or the post has been deleted.')
            elif e.code in (403, 429):
                raise Exception(
                    'Access denied or rate limited by Instagram. '
                    'Please try again later or use a professional API service.'
                )
            else:
                raise Exception(f'HTTP error: {e.code}')
                
        except URLError as e:
            raise Exception(f'Network error: {e.reason}')
    
    def _parse_media(self, html):
        """
        Parse media URLs from HTML using Open Graph meta tags
        
        Args:
            html (str): HTML content
            
        Returns:
            dict: Media information or empty dict if not found
        """
        media = {}
        
        # Try to extract og:video first
        video_pattern = r'<meta\s+property=["\']og:video["\']\s+content=["\'](.*?)["\']'
        video_match = re.search(video_pattern, html, re.IGNORECASE)
        
        if video_match:
            media['type'] = 'video'
            media['url'] = unescape(video_match.group(1))
            
            # Try to get video thumbnail
            thumb_pattern = r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']'
            thumb_match = re.search(thumb_pattern, html, re.IGNORECASE)
            
            if thumb_match:
                media['thumbnail'] = unescape(thumb_match.group(1))
        else:
            # Fallback to og:image for images
            image_pattern = r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']'
            image_match = re.search(image_pattern, html, re.IGNORECASE)
            
            if image_match:
                media['type'] = 'image'
                media['url'] = unescape(image_match.group(1))
        
        return media
    
    def get_media_info(self, url):
        """
        Get media info without downloading (useful for previews)
        
        Args:
            url (str): Instagram post URL
            
        Returns:
            dict: Media information
        """
        return self.download(url)


def main():
    """Command-line interface"""
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
        '-v', '--version',
        action='version',
        version='Instagram Downloader 1.0.0'
    )
    
    args = parser.parse_args()
    
    if not args.url:
        parser.print_help()
        sys.exit(1)
    
    downloader = InstagramDownloader()
    
    try:
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
