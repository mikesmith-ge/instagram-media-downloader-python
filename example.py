#!/usr/bin/env python3
"""
Example usage of Instagram Downloader
"""

from instagram_downloader import InstagramDownloader

# Initialize downloader
downloader = InstagramDownloader()

# Example 1: Download single post
print("Example 1: Single post download")
print("-" * 50)

try:
    media = downloader.download('https://www.instagram.com/p/ABC123/')
    
    if media['type'] == 'image':
        print(f"Image URL: {media['url']}")
    elif media['type'] == 'video':
        print(f"Video URL: {media['url']}")
        print(f"Thumbnail: {media['thumbnail']}")
        
except Exception as e:
    print(f"Error: {e}")

print()

# Example 2: Batch processing
print("Example 2: Batch processing")
print("-" * 50)

urls = [
    'https://www.instagram.com/p/ABC123/',
    'https://www.instagram.com/reel/XYZ789/',
]

for url in urls:
    try:
        media = downloader.get_media_info(url)
        print(f"✓ {media['type']}: {url}")
    except Exception as e:
        print(f"✗ Error for {url}: {e}")
