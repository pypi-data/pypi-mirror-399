# WebRender: A Simple Web Content Renderer for Python

[![PyPI Version](https://img.shields.io/pypi/v/WebRender.svg)](https://pypi.org/project/WebRender/)
[![Build Status](https://img.shields.io/travis/com/ranak8811/Web-Render-PyPi-Package.svg)](https://travis-ci.com/ranak8811/Web-Render-PyPi-Package)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

WebRender is a Python package that provides a simple and effective way to render web content within environments like Jupyter Notebooks and IPython. It's designed to overcome common embedding restrictions, allowing you to display any website or embed YouTube videos seamlessly.

## Key Features

- **Render Any Website:** Utilizes Selenium to capture and display a screenshot of any URL, bypassing `X-Frame-Options` restrictions.
- **Embed YouTube Videos:** Easily embed YouTube videos with just the URL.
- **Jupyter/IPython Integration:** Designed to work smoothly within Jupyter Notebooks and IPython environments.
- **Automatic Driver Management:** Uses `webdriver-manager` to automatically handle the required Chrome WebDriver.

## Installation

You can install WebRender directly from PyPI:

```bash
pip install WebRender
```

## Usage

WebRender is simple to use. Here are a couple of examples:

### Rendering a Website

You can render any website using the `render_site` function. This will take a screenshot of the page and display it.

```python
from WebRender.site import render_site

# Render Google's homepage
render_site('https://www.google.com')

# Render a specific article
render_site('https://en.wikipedia.org/wiki/Main_Page')
```

### Embedding a YouTube Video

Use the `render_youtube_video` function to embed a YouTube video directly in your notebook.

```python
from WebRender.youtube import render_youtube_video

# Embed a YouTube video by URL
render_youtube_video('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
```

## Dependencies

- **Python 3.8+**
- **Google Chrome:** This package requires Google Chrome to be installed on your system.
- The necessary Python packages (`selenium`, `webdriver-manager`, etc.) will be installed automatically.

## Contributing

Contributions are welcome! If you have a feature request, bug report, or want to contribute to the code, please feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/ranak8811/Web-Render-PyPi-Package).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
