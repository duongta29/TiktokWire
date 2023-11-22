from seleniumwire import webdriver
# import seleniumwire.undetected_chromedriver as webdriver
import time
from seleniumwire.utils import decode as sw_decode
import config
import unicodedata
import json
from login import TiktokLogin
from captcha import check_captcha

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
seleniumwire_options = {
    'verify_ssl': True,
    'disable_capture': False,
    'request_storage': 'memory',
    'request_storage_max_size': 0
}
# response = driver.get('https://tiktok.com/@vtv24news/video/7295647630204407041')
driver = webdriver.Chrome(options=options)
# driver.scopes = [
#     '^https://www.tiktok.com/api/comment/list/reply/?WebIdLastTime.*',
#     '^https://www.tiktok.com/api/comment/list/?WebIdLastTime.*'
# ]
# '^comment/list/?WebIdLastTime.*'
driver.get("https://www.google.com")
def interceptor(request, response):  # A response interceptor takes two args
    if "comment/list/?WebIdLastTime" in request.url:
        # response.headers['New-Header'] = 'Some Value'
        data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
        data = data.decode("utf8")
        data = json.loads(data)
        print(data)
        
    if "comment/list/reply/?WebIdLastTime" in request.url:
        # response.headers['New-Header'] = 'Some Value'
        data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
        data = data.decode("utf8")
        data = json.loads(data)
        print(data)


driver.get("https://www.tiktok.com")
time.sleep(5)
check_captcha(driver)
login = TiktokLogin(driver, username="xinhxinh29")
login.loginTiktokwithCookie()
time.sleep(2)
driver.response_interceptor = interceptor
driver.get("https://www.tiktok.com/@yeutoquoc04/video/7293526034404723976")
time.sleep(10000)