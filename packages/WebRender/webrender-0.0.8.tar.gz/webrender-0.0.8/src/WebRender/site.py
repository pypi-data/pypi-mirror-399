from IPython import display
import urllib.request
from WebRender.custom_execution import InvalidURLException
from WebRender.logger import logger


def is_valid_url(URL: str) -> bool:
    try:
        response_status = urllib.request.urlopen(URL).getcode()
        assert response_status == 200
        logger.debug(f"response_status: {response_status}")
        return True
    except:
        return False

def render_site(URL: str, width: str = '100%', height: str = '600') -> str:

    try:
        if is_valid_url(URL):
            response = display.IFrame(src=URL, width=width, height=height)
            display.display(response)
            return 'success'
        else:
            raise InvalidURLException
    except Exception as e:
        raise e