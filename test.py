from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
from seleniumwire.utils import decode as sw_decode
import time
import config 
import json
import pickle
from typing import List
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unidecode import unidecode
from post_tiktok_etractor import PostTikTokExtractor, PostCommentExtractor, PostReplyExtractor
import unicodedata
from utils.common_utils import CommonUtils
import config
import captcha
from kafka import KafkaProducer
from selenium.webdriver.common.action_chains import ActionChains
# from bs4 import BeautifulSoup
from login import TiktokLogin
producer = KafkaProducer(bootstrap_servers=["10.11.101.129:9092"])
listArgument = [
    '--mute-audio',
    "--incognito",
    "--enable-automation",
    "--allow-pre-commit-input",
    "--no-first-run","--log-level=0",
    "--password-store=basic",
    "--use-mock-keychain",
    "--test-type=webdriver",
    "--enable-blink-features=ShadowDOMV0",
    "--no-service-autorun",
    "--disable-backgrounding-occluded-windows",
    '--disable-blink-features=AutomationControlled',
    "--ignore-certificate-errors",
    '--disable-infobars',
    '--disable-notifications',
    '--disable-save-password-bubble',
    "--disable-setuid-sandbox",
    "--hide-scrollbars",
    "--disable-gpu",
    "--disable-permissions-api",
    "--disable-background-networking",
    "--disable-2d-canvas-clip-aa",
    "--enable-precise-memory-info",
    "--disable-client-side-phishing-detection",
    "--disable-default-apps",
    "--disable-hang-monitor",
    "--disable-translate",
    "--disable-prompt-on-repost",
    "--disable-sync",
    "--disable-popup-blocking",
    "--no-sandbox",
    '--disable-web-security',
    '--disable-extensions',
    "--no-zygote",
    "--blink-settings=imagesEnabled=false",
    #"--disable-features=SubresourceWebBundle",
    "--load-extension=C:\\Users\\Anh Duong\\Desktop\\sonet-chromium_08112023\\nomovdo",
    #"--headless",
    "--sonet-diswebgl",
    "--sonet-disencryption",
    #"--incognito",
    "--sonet-fingerprinting-client-rects-noise",
    "--sonet-fingerprinting-canvas-image-data-noise",
    "--sonet-fingerprinting-audio-context-data-noise"
]
listArgument2 = [
    "--incognito",
    "--sonet-fingerprinting-client-rects-noise",
    "--sonet-fingerprinting-canvas-image-data-noise",
    "--sonet-fingerprinting-audio-context-data-noise"
]
s = Service("C:\\Users\\Anh Duong\\Desktop\\sonet-chromium_08112023\\chromedriver.exe")
    #s = Service("D:\\ChienND\\OSINT_dubug\\crawler_client\\chromedriver\\chromedriver.exe")
options = Options()
options.binary_location = "C:\\AD\\Osint\\chrome-win\\chrome.exe"
for item in listArgument:
        options.add_argument(item)
# driver = webdriver.Chrome(service=s, options=options)

with open(config.config_path, "r", encoding='latin-1') as f:
    data = f.read()
    data = json.loads(data)
    option = data["mode"]["name"]

class CrawlManage(object, ):
    XPATH_VIDEO_SEARCH = '//*[contains(@class, "DivItemContainerForSearch")]'
    XPATH_VIDEO_OTHER = '//*[contains(@class, "DivItemContainerV2")]'
    # XPATH_VIDEO_OTHER = '//*[@class="tiktok-x6y88p-DivItemContainerV2 e19c29qe9"]'
    XPATH_VIDEO_USER = '//*[@data-e2e="user-post-item-desc"]'

    def __init__(self, driver = webdriver.Chrome(service=s, options=options) , config=config) -> None:
#         driver.scopes = [
#     '.*comment.*'
# ]
        self.driver = driver
        self.config = config
        self.actions = ActionChains(self.driver)
        self.link = None
        self.comments = []
        self.reply = []

    def parse_keyword(self, option, page) -> List[str]:
        keyword_list_raw_dict = []
        keyword_list: List[str] = []
        with open(self.config.config_path, "r", encoding='utf-8') as f:
            data = f.read()
            keyword_list_raw = json.loads(data)
            if option == "search_post":
                keyword_list_raw_dict = keyword_list_raw["mode"]["keyword"]
            elif option == "search_user":
                keyword_list_raw_dict = keyword_list_raw["mode"][f"list_page{page}"]
        return keyword_list_raw_dict

    def check_login_div(self):
        print("Check login div")
        try:
            button = self.driver.find_element(By.XPATH, '//*[@data-e2e="modal-close-inner-button"]')
            button.click()
        except:
            # try:
            #     login = self.driver.find_element(By.XPATH, '//*[@id="login-modal"]')
            #     self.driver.close()
            #     time.sleep(3)
            #     self.driver=webdriver.Chrome(options=chrome_options)
            #     return self.crawl_post(self.link, self.source_id)
            # except:
            print("No login div")

    def clickViewmore(self,cmt):
        pass
    
    def crawl_comment(self):
        comments = []
        list_comment = self.comments
        self.comments = []
        list_replies = self.reply
        self.reply = []
        for comment_dict in list_comment:
            comment_extractor: PostCommentExtractor = PostCommentExtractor(driver=self.driver, comment_dict = comment_dict)
            comment = comment_extractor.extract()
            comments.append(comment)
            with open("result.txt", "a", encoding="utf-8") as file:
                file.write(f"{str(comment)}\n")
                if comment.is_valid:
                    file.write("🇧🇷" * 50 + "\n")
                else:
                    file.write("🎈" * 50 + "\n")
            try: 
                if comment_dict["reply_comment"] is not None:
                    list_reply = comment_dict["reply_comment"]
                    for reply_dict in list_reply:
                        reply_extractor: PostReplyExtractor = PostReplyExtractor(driver = self.driver, reply_dict = reply_dict) 
                        reply = reply_extractor.extract()
                        comments.append(comment)
                        with open("result.txt", "a", encoding="utf-8") as file:
                            file.write(f"{str(reply)}\n")
                            if reply.is_valid:
                                file.write("🇧🇷" * 50 + "\n")
                            else:
                                file.write("🎈" * 50 + "\n")  
            except Exception as e:
                 print(e)
        for reply_dict in list_replies:
            reply_extractor: PostReplyExtractor = PostReplyExtractor(driver = self.driver, reply_dict = reply_dict) 
            reply = reply_extractor.extract()
            comments.append(comment)
            with open("result.txt", "a", encoding="utf-8") as file:
                file.write(f"{str(reply)}\n")
                if reply.is_valid:
                    file.write("🇧🇷" * 50 + "\n")
                else:
                    file.write("🎈" * 50 + "\n")
        return comments
        
            
        
    def interceptor_post(self, request, response):
        if "comment/list/?WebIdLastTime" in request.url:
            data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
            try:
                data = data.decode("utf8")
            except:
                pass
            data = json.loads(data)
            list_comment = data["comments"]
            for comment in list_comment:
                self.comments.append(comment) 
        if "comment/list/reply/?WebIdLastTime" in request.url:
            data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
            try:
                data = data.decode("utf8")
            except:
                pass
            data = json.loads(data)
            list_reply = data["comments"]
            for reply in list_reply:
                self.reply.append(reply)

    def scroll_comment(self):
            cmts = []
            check = 1
            while (len(cmts) != check):
                    # comments_section = self.driver.find_element(By.XPATH, '//*[@data-e2e="search-comment-container"]/div')
                    # actions.move_to_element(comments_section)
                check = len(cmts)
                cmts = []
                self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                cmts = self.driver.find_elements(
                        By.XPATH, '//*[contains(@class, "DivCommentItemContainer")]')
                time.sleep(2)
            try:
                    self.driver.execute_script("window.scrollTo(0, 0);")
            except:
                    pass
            for cmt in cmts:
                BOOL = True
                while(BOOL):
                    try:
                        # reply_div = cmt.find_element(By.XPATH, './/div[contains(@class, "DivReplyActionContainer")]')
                        reply_button = cmt.find_element(By.XPATH, './/p[contains(@data-e2e, "view-more-")]')
                        reply_button.click()
                        self.driver.execute_script("window.scrollTo(0, 1000);")
                        time.sleep(2)
                    except Exception as e:
                        BOOL = False
            

    def crawl_post(self, link):
        self.driver.response_interceptor = self.interceptor_post
        segments = link.split("/")
        source_id = segments[-1]
        try:
            posts=[]
            self.comments =[]
            self.driver.get(link) 
            # self.driver.get(link)
            # time.sleep(3)
            self.driver.implicitly_wait(5)
            # self.check_login_div()
            # time.sleep(3)
            print(f" >>> Crawling: {link} ...")
            post_extractor: PostTikTokExtractor = PostTikTokExtractor(
                driver=self.driver, link=link, source_id=source_id)
            # data[vid] = self.CrawlVideo(vid)
            post = post_extractor.extract()
            retry_time = 0
            def retry_extract(post, retry_time):
                while not post.is_valid():
                    post = post_extractor.extract()
                    if retry_time > 0:
                        print(
                            f"Try to extract post {retry_time} times {str(post)}")
                        slept_time = CommonUtils.sleep_random_in_range(1, 5)
                        print(f"Slept {slept_time}")
                    retry_time = retry_time + 1
                    if retry_time > 20:
                        print("Retried 20 times, skip post")
                        break
                return
            retry_extract(post, retry_time)
            posts.append(post)
            with open('dataCrawled.txt', 'a') as f:
                f.write(f"{link}\n")
            with open("result.txt", "a", encoding="utf-8") as file:
                file.write(f"{str(post)}\n")
                if post.is_valid:
                    file.write("🇧🇷" * 50 + "\n")
                else:
                    file.write("🎈" * 50 + "\n")
            if posts != [] :
                self.scroll_comment()
                comments = self.crawl_comment()
                del self.driver.response_interceptor
                # print("push kafka")
                try:
                    push_kafka = self.push_kafka(posts,comments)
                    if push_kafka == 1:
                        print("Done push kafka")
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
            captcha.check_captcha(self.driver)
            return self.crawl_post(link)
        
    def push_kafka(self, posts, comments):
        if len(posts) > 0:
            bytes_obj = pickle.dumps([ob.__dict__ for ob in posts])
            producer.send('lnmxh', bytes_obj)
            if len(comments) > 0:
                bytes_obj = pickle.dumps([ob.__dict__ for ob in comments])
                producer.send('lnmxh', bytes_obj)
            return 1
        else:
            return 0

    def run(self, page):
        count = 0
        self.driver.get("https://www.tiktok.com/")
        time.sleep(2)
        captcha.check_captcha(self.driver)
        ttLogin = TiktokLogin(self.driver, username = "xinhxinh29")
        ttLogin.loginTiktokwithCookie()
        # self.check_login_div()
        print("Start crawl")
        # time.sleep(3)
        keywords = self.parse_keyword(option, page)
        for keyword in keywords:
            link_list = self.get_link_list(keyword)
            for link in link_list:
                # self.link = link
                # segments = link.split("/")
                # source_id = segments[-1]
                # count += 1
                # self.source_id = source_id
                start = time.time()
                self.crawl_post(link)
                end = time.time()
                print(f"Time for video {link} is {end - start}")
        time.sleep(30*60)
        return self.run("")
    
    # def run(link):

    def scroll(self, xpath):
        vidList = []
        # time.sleep(3)
        try:
            captcha.check_captcha(self.driver)
        except:
            pass
        with open('dataCrawled.txt', 'r') as f:
            data_crawled = [line.strip() for line in f]
        count = 1
        vid_list_elem = []
        if option == "search_user":
            try:
                no_post = self.driver.find_element(By.XPATH, '//*[@class="tiktok-1ovqurc-PTitle emuynwa1"]').text()
                print("No post")
            except:
                no_post =""
        
            while(len(vid_list_elem) != count and len(vid_list_elem) < self.config.count_of_vid and no_post != "No content"):
                # data-e2e="search-common-link"
                count = len(vid_list_elem)
                try:
                    vid_list_elem = self.driver.find_elements(By.XPATH, xpath)
                except:
                    vid_list_elem = self.driver.find_elements(By.XPATH, xpath)
                for vid in vid_list_elem:
                    link = vid.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    if link in data_crawled:
                        continue
                    elif link in vidList:
                        continue
                    else:
                        vidList.append(link)
                # print("len vid: ", len(vid_list_elem))
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
        else:
        # time.sleep(3)
            while(len(vid_list_elem) != count and len(vid_list_elem) < self.config.count_of_vid):
                    # data-e2e="search-common-link"
                    count = len(vid_list_elem)
                    try:
                        vid_list_elem = self.driver.find_elements(By.XPATH, xpath)
                    except:
                        vid_list_elem = self.driver.find_elements(By.XPATH, xpath)
                    # print("len vid: ", len(vid_list_elem))
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
            for vid in vid_list_elem:
                link = vid.find_element(By.TAG_NAME, 'a').get_attribute('href')
                vidList.append(link)
            if len(vidList) == 0:
                print("Something went wrong")
                self.driver.refresh()
                return self.scroll(xpath)
            print("Count of links: ", len(vidList))
            
            for vid in vidList:
                if vid in data_crawled:
                    vidList.remove(vid)
        return vidList

    def get_link_list(self, keyword) -> list:
        print('-------> GET LINK LIST <-------')
        vidList = []
        # with open()
        # keyword_dict, option = self.parse_keyword()
        if option == "search_post":
            self.driver.get(self.config.search_post_tiktok + keyword)
            # time.sleep(1)
            # captcha.check_captcha(self.driver)
            vidList = self.scroll(xpath=self.XPATH_VIDEO_SEARCH)
        if option == "search_post_android":
            driver_appium = run_appium(keyword)
            post = 0
            link = None
            while post <= 3:
                share = driver_appium.find_element(
                    "id", "com.ss.android.ugc.trill:id/jme")
                share.click()
                copy_link = driver_appium.find_element(
                    "xpath", '//android.widget.Button[@content-desc="Sao chép Liên kết"]/android.widget.ImageView')
                copy_link.click()
                link_old = link
                link = clipboard.paste()
                # while link_old == link:
                #     time.sleep(1)
                time.sleep(5)
                self.driver.get(link)
                vid = self.driver.find_element(
                    By.XPATH, '//meta[@property="og:url"]').get_attribute("content")
                vidList.append(vid)
                # link_list.append(link)
                # with open("link_list_android.txt", "a") as f:
                #     f.write(f"{link}\n")
                perform_swipe(driver_appium)
                post += 1
                # with open("link_list_android.txt", "r") as f:
                #     vidList = [line.strip() for line in f.readlines()]
        elif option == "search_user": 
            self.driver.get(keyword)
            # captcha.check_captcha(self.driver)
            vidList = self.scroll(xpath=self.XPATH_VIDEO_USER)
        elif option == "tag":
            self.driver.get(self.config.hashtag_tiktok + keyword)
            # captcha.check_captcha(self.driver)
            vidList = self.scroll(xpath=self.XPATH_VIDEO_OTHER)
        elif option == "explore":
            self.driver.get(self.config.explore_tiktok)
            # captcha.check_captcha(self.driver)
            div = self.driver.find_elements(
                By.XPATH, '//*[@id="main-content-explore_page"]/div/div[1]/div[1]/div')
            for d in div:
                if d.text == self.config.explore_option:
                    d.click()
                    break
            vidList = self.scroll(xpath=self.XPATH_VIDEO_OTHER)
        return vidList
