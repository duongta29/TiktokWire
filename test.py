from seleniumwire import webdriver
import time
from seleniumwire.utils import decode as sw_decode
import config
import unicodedata
import json

options = webdriver.ChromeOptions()
options.add_argument('--mute-audio')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--start-maximized")
options.add_argument('--disable-infobars')
options.add_argument('--disable-notifications')
options.add_argument('--disable-popup-blocking')
options.add_argument('--disable-save-password-bubble')
options.add_argument('--disable-translate')
options.add_argument('--disable-web-security')
options.add_argument('--disable-extensions')
options.add_argument(f'--proxy-server={config.proxy}')
# response = driver.get('https://tiktok.com/@vtv24news/video/7295647630204407041')
driver = webdriver.Chrome(options=options)
driver.get('https://tiktok.com')
def interceptor(request, response):  # A response interceptor takes two args
    if "comment/list/?WebIdLastTime" in request.url:
        # response.headers['New-Header'] = 'Some Value'
        data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
        data = data.decode("utf8")
        data = json.loads(data)
        print(data)

driver.response_interceptor = interceptor

time.sleep(1000)