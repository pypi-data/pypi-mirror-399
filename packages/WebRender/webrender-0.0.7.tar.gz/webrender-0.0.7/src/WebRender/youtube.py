from WebRender.custom_execution import InvalidURLException
from WebRender.logger import logger
import re
from IPython.display import HTML, display


def render_youtube_video(url: str, width: int = 760, height: int = 440):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(regex, url)

    if not match:
        raise InvalidURLException('Provided URL is invalid', url=url)

    video_id = match.group(1)

    embed_url = f"https://www.youtube.com/embed/{video_id}"

    iframe = f"""
    <iframe width="{width}" height="{height}"
    src="{embed_url}"
    title="YouTube video player"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen>
    </iframe>
    """

    display(HTML(iframe))

    logger.info("Video rendered successfully")

    return 'success'
