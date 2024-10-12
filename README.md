# Sitemap Utility Suite

A Python-based utility suite designed to fetch and analyze sitemaps and other well-known files from websites.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Components](#components)
- [Contributing](#contributing)
- [License](#license)

## Features

- Fetch and parse XML sitemaps from websites
- Recursively traverse sitemap indices
- Extract sitemap URLs from robots.txt files
- Fetch common well-known files (robots.txt, humans.txt, security.txt)
- Robust error handling and logging
- User-agent spoofing for web requests

---

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/sitemap-utility-suite.git
   cd sitemap-utility-suite
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Installation with documentation dependencies

To install Sitemap Grabber with documentation dependencies:

1. Ensure you have flit installed:
   ```
   pip install flit
   ```

2. Install the package with documentation dependencies:
   ```
   flit install --deps develop --extras docs
   ```

For developers who want to contribute to the project:

1. Install the package with both documentation and development dependencies:
   ```
   flit install --deps develop --extras "docs,dev"
   ```

Alternatively, if you prefer using pip:

```
pip install -e ".[docs,dev]"
```

This will install the package in editable mode along with all necessary
dependencies for building the documentation and development tools.

---

## Usage

Here's a basic example of how to use the SitemapGrabber:

```python
from sitemap_grabber import SitemapGrabber

# Initialize the SitemapGrabber with a website URL
grabber = SitemapGrabber("https://example.com")

# Fetch all sitemaps
grabber.get_all_sitemaps()

# Print the discovered sitemap URLs
for url in grabber.sitemap_urls:
    print(url)
```

To fetch well-known files:

```python
from well_known_files import WellKnownFiles

# Initialize the WellKnownFiles with a website URL
wkf = WellKnownFiles("https://example.com")

# Fetch robots.txt
robots_txt = wkf.fetch("robots.txt")
print(robots_txt)

# Fetch security.txt
security_txt = wkf.fetch("security.txt")
print(security_txt)
```

## Components

### SitemapGrabber

The `SitemapGrabber` class is responsible for discovering and fetching XML sitemaps from a given website. It can:

- Extract sitemap URLs from robots.txt
- Check common sitemap locations
- Recursively traverse sitemap indices
- Handle relative and absolute URLs

### WellKnownFiles

The `WellKnownFiles` class fetches common well-known files from websites, including:

- robots.txt
- humans.txt
- security.txt

It includes caching to avoid redundant requests and can handle various edge cases in HTTP responses.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

For more information or to report issues, please visit the [GitHub repository](https://github.com/yourusername/sitemap-utility-suite).
