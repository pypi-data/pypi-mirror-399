from IPython import display
import urllib.request
from WebRender.custom_execution import InvalidURLException
from WebRender.logger import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os

def is_valid_url(URL: str) -> bool:
    try:
        response_status = urllib.request.urlopen(URL).getcode()
        assert response_status == 200
        logger.debug(f"response_status: {response_status}")
        return True
    except:
        return False

def render_site(URL: str, width: int = 1280, height: int = 720) -> str:
    try:
        if is_valid_url(URL):
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument(f"--window-size={width},{height}")
            
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
            
            driver.get(URL)
            
            screenshot_path = "screenshot.png"
            driver.save_screenshot(screenshot_path)
            
            driver.quit()
            
            display.display(display.Image(filename=screenshot_path))
            os.remove(screenshot_path)
            
            return 'success'
        else:
            raise InvalidURLException
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e