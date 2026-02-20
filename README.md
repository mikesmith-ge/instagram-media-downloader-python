# Instagram Media Downloader (Python)

![Python Version](https://img.shields.io/badge/Python-%3E%3D3.7-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen)
![Version](https://img.shields.io/badge/version-1.2.0-orange)

> Lightweight Python script to extract high-quality media URLs from public Instagram posts without API keys or external dependencies.

## 📋 Overview

**InstagramDownloader** is a simple, pure-Python tool that extracts media (images and videos) from public Instagram posts. Uses a two-stage extraction strategy: JSON blob first (resilient to HTML changes), Open Graph meta tags as fallback. Perfect for educational purposes, prototypes, or small-scale projects.

**Also available in:** [PHP](https://github.com/mikesmith-ge/instagram-media-downloader-php) | **Python** (you are here)

## ✨ Features

- ✅ **Zero dependencies** – Pure Python 3, uses only standard library
- 🚀 **Simple API** – Single class with straightforward methods
- 🖼️ **Image & Video support** – Extracts both image and video URLs
- 🔄 **JSON-first extraction** – Resilient to Instagram HTML structure changes (v1.2.0)
- 🌐 **Proxy support** – HTTP and SOCKS5 proxies to avoid rate limits (v1.1.0)
- 🔒 **Error handling** – Validates URLs and handles network/parsing errors
- 🎯 **Public posts only** – Works with any publicly accessible Instagram post
- 🖥️ **CLI included** – Run directly from command line
- 📦 **Importable module** – Use in your own Python projects

## 📦 Installation

### Option 1: Direct Download
Download `instagram_downloader.py` and use it directly:

```bash
# Download the script
wget https://raw.githubusercontent.com/mikesmith-ge/instagram-media-downloader-python/main/instagram_downloader.py

# Make it executable (optional)
chmod +x instagram_downloader.py
```

### Option 2: Clone Repository
```bash
git clone https://github.com/mikesmith-ge/instagram-media-downloader-python.git
cd instagram-media-downloader-python
```

## 🚀 Usage

### Command Line Interface

```bash
# Basic usage
python instagram_downloader.py "https://www.instagram.com/p/ABC123/"

# With proxy (to avoid rate limits)
python instagram_downloader.py "https://www.instagram.com/p/ABC123/" --proxy "http://host:port"

# SOCKS5 proxy
python instagram_downloader.py "https://www.instagram.com/p/ABC123/" --proxy "socks5://user:pass@host:port"
```

**Output:**
```
Fetching media from: https://www.instagram.com/p/ABC123/

✓ Success!
Type:      image
URL:       https://scontent.cdninstagram.com/...
Extracted: via json
```

### Python Module Usage

#### Basic Example

```python
from instagram_downloader import InstagramDownloader

downloader = InstagramDownloader()

try:
    media = downloader.download('https://www.instagram.com/p/ABC123/')

    if media['type'] == 'image':
        print(f"Image URL: {media['url']}")
    elif media['type'] == 'video':
        print(f"Video URL: {media['url']}")
        print(f"Thumbnail: {media['thumbnail']}")

    print(f"Extracted via: {media['source']}")  # 'json' or 'og_meta'

except Exception as e:
    print(f"Error: {e}")
```

#### With Proxy (avoid rate limits)

```python
# HTTP proxy — zero extra dependencies
downloader = InstagramDownloader(proxy='http://user:pass@host:port')

# SOCKS5 proxy — requires: pip install requests[socks]
downloader = InstagramDownloader(proxy='socks5://user:pass@host:port')

media = downloader.download('https://www.instagram.com/p/ABC123/')
```

#### Batch Processing

```python
from instagram_downloader import InstagramDownloader
import time

urls = [
    'https://www.instagram.com/p/ABC123/',
    'https://www.instagram.com/reel/XYZ789/',
    'https://www.instagram.com/tv/DEF456/',
]

downloader = InstagramDownloader()

for url in urls:
    try:
        media = downloader.get_media_info(url)
        print(f"✓ {media['type']} [{media['source']}]: {media['url']}")
    except Exception as e:
        print(f"✗ Error for {url}: {e}")

    # Be respectful — add delay between requests
    time.sleep(2)
```

#### Save Media to File

```python
from instagram_downloader import InstagramDownloader
import urllib.request

downloader = InstagramDownloader()

media = downloader.download('https://www.instagram.com/p/ABC123/')

filename = f"instagram_{media['type']}.{'mp4' if media['type'] == 'video' else 'jpg'}"
urllib.request.urlretrieve(media['url'], filename)

print(f"Saved: {filename}")
```

### Response Format

```python
# Image:
{
    'type':   'image',
    'url':    'https://scontent.cdninstagram.com/...',
    'source': 'json'      # extraction method: 'json' or 'og_meta'
}

# Video:
{
    'type':      'video',
    'url':       'https://scontent.cdninstagram.com/...',
    'thumbnail': 'https://scontent.cdninstagram.com/...',
    'source':    'json'
}
```

## ⚙️ Requirements

- Python 3.7 or higher
- No external dependencies for core usage (standard library only)
- `pip install requests[socks]` — only if using SOCKS5 proxies

## ⚠️ Limitations

This is a **basic scraper** with several important limitations:

- ❌ **Public posts only** – Cannot access private accounts or stories
- ⏱️ **Rate limits** – Instagram may block frequent requests from the same IP (use `proxy=` to mitigate)
- 🚫 **No authentication** – Cannot bypass login walls or access restricted content
- 📉 **Semi-fragile** – JSON extraction (v1.2.0) greatly reduces breakage risk, but major Instagram updates may still affect results
- 🎠 **Single media only** – Multi-image carousels will only return the first image
- 📊 **No metadata** – Cannot extract captions, likes, comments, or user information

### 🚀 Need More?

**For production use cases, bypassing rate limits, accessing stories, private content, or building commercial applications**, we recommend using a professional API solution:

👉 **[Instaboost API](https://instaboost.ge/en/instagram)** – Enterprise-grade Instagram data API with:
- ✅ Unlimited rate limits
- ✅ Stories, Reels, and IGTV support
- ✅ Private account access (with authorization)
- ✅ Full metadata extraction (captions, likes, comments)
- ✅ Multi-image carousel support
- ✅ 99.9% uptime SLA
- ✅ Dedicated support

[**Learn more →**](https://instaboost.ge)

## 📅 Changelog

| Version | What's new |
|---------|-----------|
| **v1.2.0** | JSON-first extraction — resilient to HTML structure changes |
| **v1.1.0** | HTTP and SOCKS5 proxy support |
| **v1.0.0** | Initial release |

## 🔄 Related Projects

- **[Instagram Downloader (PHP)](https://github.com/mikesmith-ge/instagram-media-downloader-php)** – Same functionality in PHP
- **[TikTok Downloader (PHP)](https://github.com/mikesmith-ge/tiktok-video-downloader-php)** – Extract TikTok videos
- **[TikTok Downloader (Node.js)](https://github.com/mikesmith-ge/tiktok-video-downloader-nodejs)** – TikTok downloader in JavaScript
- **[YouTube Shorts Downloader (Python)](https://github.com/mikesmith-ge/youtube-shorts-downloader-python)** – Download YouTube Shorts
- **[YouTube Shorts Downloader (PHP)](https://github.com/mikesmith-ge/youtube-shorts-downloader-php)** – YouTube in PHP
- **[YouTube Shorts Downloader (Node.js)](https://github.com/mikesmith-ge/youtube-shorts-downloader-nodejs)** – YouTube in JavaScript
- [See all tools →](https://github.com/mikesmith-ge?tab=repositories)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](../../issues).

## ⚡ Disclaimer

This tool is for **educational purposes only**. Scraping Instagram may violate their Terms of Service. Use responsibly and at your own risk. For commercial or production use, always use official APIs or authorized services.

## 📧 Support

- 🐛 **Found a bug?** [Open an issue](../../issues)
- 💡 **Have a suggestion?** [Start a discussion](../../discussions)
- 🚀 **Need enterprise features?** [Visit Instaboost](https://instaboost.ge/en)

---

**Made with ❤️ by the Instaboost Team**
