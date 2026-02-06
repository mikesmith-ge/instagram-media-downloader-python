# Instagram Media Downloader (Python)

![Python Version](https://img.shields.io/badge/Python-%3E%3D3.7-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen)

> Lightweight Python script to extract high-quality media URLs from public Instagram posts without API keys or external dependencies.

## 📋 Overview

**InstagramDownloader** is a simple, pure-Python tool that extracts media (images and videos) from public Instagram posts by parsing Open Graph meta tags. Perfect for educational purposes, prototypes, or small-scale projects.

**Also available in:** [PHP](https://github.com/mikesmith-ge/instagram-media-downloader-php) | **Python** (you are here)

## ✨ Features

- ✅ **Zero dependencies** – Pure Python 3, uses only standard library
- 🚀 **Simple API** – Single class with straightforward methods
- 🖼️ **Image & Video support** – Extracts both image and video URLs
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

# Make it executable and run directly
chmod +x instagram_downloader.py
./instagram_downloader.py "https://www.instagram.com/reel/XYZ789/"
```

**Output:**
```
Fetching media from: https://www.instagram.com/p/ABC123/

✓ Success!
Type: image
URL: https://scontent.cdninstagram.com/...
```

### Python Module Usage

#### Basic Example

```python
from instagram_downloader import InstagramDownloader

downloader = InstagramDownloader()

try:
    # Download media from a public Instagram post
    media = downloader.download('https://www.instagram.com/p/ABC123/')
    
    # Check media type
    if media['type'] == 'image':
        print(f"Image URL: {media['url']}")
    elif media['type'] == 'video':
        print(f"Video URL: {media['url']}")
        print(f"Thumbnail: {media['thumbnail']}")
        
except Exception as e:
    print(f"Error: {e}")
```

#### Advanced Example: Batch Processing

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
        print(f"✓ {media['type']}: {media['url']}")
    except Exception as e:
        print(f"✗ Error for {url}: {e}")
    
    # Be nice to Instagram - add delay between requests
    time.sleep(2)
```

#### Save Media to File

```python
from instagram_downloader import InstagramDownloader
import urllib.request

downloader = InstagramDownloader()

# Get media URL
media = downloader.download('https://www.instagram.com/p/ABC123/')

# Download the actual file
filename = f"instagram_{media['type']}.{'mp4' if media['type'] == 'video' else 'jpg'}"
urllib.request.urlretrieve(media['url'], filename)

print(f"Downloaded: {filename}")
```

### Response Format

```python
# For images:
{
    'type': 'image',
    'url': 'https://scontent.cdninstagram.com/...'
}

# For videos:
{
    'type': 'video',
    'url': 'https://scontent.cdninstagram.com/...',
    'thumbnail': 'https://scontent.cdninstagram.com/...'
}
```

## ⚙️ Requirements

- Python 3.7 or higher
- No external dependencies (uses only standard library)

## ⚠️ Limitations

This is a **basic scraper** with several important limitations:

- ❌ **Public posts only** – Cannot access private accounts or stories
- ⏱️ **Rate limits** – Instagram may block frequent requests from the same IP
- 🚫 **No authentication** – Cannot bypass login walls or access restricted content
- 📉 **Fragile** – Changes to Instagram's HTML structure may break functionality
- 🎠 **Single media only** – Multi-image carousels will only return the first image
- 📊 **No metadata** – Cannot extract captions, likes, comments, or user information

### 🚀 Need More?

**For production use cases, bypassing rate limits, accessing stories, private content, or building commercial applications**, we recommend using a professional API solution:

👉 **[Instaboost API](https://instaboost.ge/en/instagram)** – Enterprise-grade Instagram data API with:
- ✅ Unlimited rate limits
- ✅ Stories, Reels, and IGTV support
- ✅ Private account access (with authorization)
- ✅ Full metadata extraction
- ✅ Multi-image carousel support
- ✅ 99.9% uptime SLA
- ✅ Dedicated support

[**Learn more →**](https://instaboost.ge)

## 🔄 Related Projects

Looking for other implementations?

- **[PHP Version](https://github.com/mikesmith-ge/instagram-media-downloader-php)** – Same functionality in PHP
- **[TikTok Downloader (PHP)](https://github.com/mikesmith-ge/tiktok-video-downloader-php)** – Extract TikTok videos
- **[TikTok Downloader (Node.js)](https://github.com/mikesmith-ge/tiktok-video-downloader-nodejs)** – TikTok downloader in JavaScript
- More tools coming soon!

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
