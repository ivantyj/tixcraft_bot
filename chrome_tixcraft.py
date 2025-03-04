#!/usr/bin/env python3
#encoding=utf-8
# 'seleniumwire' and 'selenium 4' raise error when running python 2.x
# PS: python 2.x will be removed in future.
#執行方式：python chrome_tixcraft.py 或 python3 chrome_tixcraft.py
import os
import sys
import platform
import json
import random

from selenium import webdriver
# for close tab.
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import WebDriverException
# for alert 2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# for selenium 4
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
# for wait #1
import time
import re
from datetime import datetime
# for error output
import logging
logging.basicConfig()
logger = logging.getLogger('logger')
# for check reg_info
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

# ocr
import base64
try:
    import ddddocr
    #PS: python 3.11.1 raise PIL conflict.
    from NonBrowser import NonBrowser
except Exception as exc:
    pass

import webbrowser
import argparse
import itertools

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

CONST_APP_VERSION = u"MaxBot (2023.6.7) ver 10"

CONST_MAXBOT_CONFIG_FILE = "settings.json"
CONST_MAXBOT_LAST_URL_FILE = "MAXBOT_LAST_URL.txt"
CONST_MAXBOT_INT28_FILE = "MAXBOT_INT28_IDLE.txt"

CONST_HOMEPAGE_DEFAULT = "https://tixcraft.com"
URL_CHROME_DRIVER = 'https://chromedriver.chromium.org/'

CONST_CHROME_VERSION_NOT_MATCH_EN="Please download the WebDriver version to match your browser version."
CONST_CHROME_VERSION_NOT_MATCH_TW="請下載與您瀏覽器相同版本的WebDriver版本，或更新您的瀏覽器版本。"

CONST_KKTIX_SIGN_IN_URL = "https://kktix.com/users/sign_in?back_to=%s"
CONST_CITYLINE_SIGN_IN_URL = "https://www.cityline.com/Login.html?targetUrl=https%3A%2F%2Fwww.cityline.com%2FEvents.html"
CONST_URBTIX_SIGN_IN_URL = "https://www.urbtix.hk/member-login"
CONST_KHAM_SIGN_IN_URL = "https://kham.com.tw/application/UTK13/UTK1306_.aspx"
CONST_HKTICKETING_SIGN_IN_URL = "https://premier.hkticketing.com/Membership/Login.aspx"

CONST_FROM_TOP_TO_BOTTOM = u"from top to bottom"
CONST_FROM_BOTTOM_TO_TOP = u"from bottom to top"
CONST_RANDOM = u"random"
CONST_SELECT_ORDER_DEFAULT = CONST_FROM_TOP_TO_BOTTOM
CONST_SELECT_OPTIONS_DEFAULT = (CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_RANDOM)
CONST_SELECT_OPTIONS_ARRAY = [CONST_FROM_TOP_TO_BOTTOM, CONST_FROM_BOTTOM_TO_TOP, CONST_RANDOM]

CONT_STRING_1_SEATS_REMAINING = [u'@1 seat(s) remaining',u'剩餘 1@',u'@1 席残り']

CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER = "NonBrowser"
CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS = "canvas"

CONST_WEBDRIVER_TYPE_SELENIUM = "selenium"
#CONST_WEBDRIVER_TYPE_STEALTH = "stealth"
CONST_WEBDRIVER_TYPE_UC = "undetected_chromedriver"


def t_or_f(arg):
    ret = False
    ua = str(arg).upper()
    if 'TRUE'.startswith(ua):
        ret = True
    elif 'YES'.startswith(ua):
        ret = True
    return ret

def sx(s1):
    key=18
    return ''.join(chr(ord(a) ^ key) for a in s1)

def decryptMe(b):
    s=""
    if(len(b)>0):
        s=sx(base64.b64decode(b).decode("UTF-8"))
    return s

def encryptMe(s):
    data=""
    if(len(s)>0):
        data=base64.b64encode(sx(s).encode('UTF-8')).decode("UTF-8")
    return data

def get_app_root():
    # 讀取檔案裡的參數值
    basis = ""
    if hasattr(sys, 'frozen'):
        basis = sys.executable
    else:
        basis = sys.argv[0]
    app_root = os.path.dirname(basis)
    return app_root

def get_config_dict(args):
    app_root = get_app_root()
    config_filepath = os.path.join(app_root, CONST_MAXBOT_CONFIG_FILE)

    # allow assign config by command line.
    if not args.input is None:
        if len(args.input) > 0:
            config_filepath = args.input

    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)

            # start to overwrite config settings.
            if not args.headless is None:
                headless_flag = t_or_f(args.headless)
                if headless_flag:
                    config_dict["advanced"]["headless"] = True

            if not args.homepage is None:
                if len(args.homepage) > 0:
                    config_dict["homepage"] = args.homepage
            if not args.ticket_number is None:
                if args.homepage > 0:
                    config_dict["ticket_number"] = args.ticket_number
            if not args.browser is None:
                if len(args.browser) > 0:
                    config_dict["browser"] = args.browser

            if not args.tixcraft_sid is None:
                if len(args.tixcraft_sid) > 0:
                    config_dict["advanced"]["tixcraft_sid"] = encryptMe(args.tixcraft_sid)
            if not args.kktix_account is None:
                if len(args.kktix_account) > 0:
                    config_dict["advanced"]["kktix_account"] = args.kktix_account
            if not args.kktix_password is None:
                if len(args.kktix_password) > 0:
                    config_dict["advanced"]["kktix_password"] = args.kktix_password
            if not args.ibonqware is None:
                if len(args.ibonqware) > 0:
                    config_dict["advanced"]["ibonqware"] = encryptMe(args.ibonqware)


            # special case for headless to enable away from keyboard mode.
            is_headless_enable = False
            if config_dict["advanced"]["headless"]:
                # for tixcraft headless.
                if len(config_dict["advanced"]["tixcraft_sid"]) > 1:
                    is_headless_enable = True
                else:
                    print("If you are runnig headless mode on tixcraft, you need input your cookie SID.")

            if is_headless_enable:
                config_dict["ocr_captcha"]["enable"] = True
                config_dict["ocr_captcha"]["force_submit"] = True
    return config_dict

def write_last_url_to_file(url):
    with open(CONST_MAXBOT_LAST_URL_FILE, "w") as text_file:
        text_file.write("%s" % url)

def read_last_url_from_file():
    ret = ""
    with open(CONST_MAXBOT_LAST_URL_FILE, "r") as text_file:
        ret = text_file.readline()
    return ret

def format_keyword_string(keyword):
    if not keyword is None:
        if len(keyword) > 0:
            keyword = keyword.replace('／','/')
            keyword = keyword.replace('　','')
            keyword = keyword.replace(',','')
            keyword = keyword.replace('，','')
            keyword = keyword.replace('$','')
            keyword = keyword.replace(' ','').lower()
    return keyword

def full2half(keyword):
    n = ""
    if not keyword is None:
        if len(keyword) > 0:
            for char in keyword:
                num = ord(char)
                if num == 0x3000:
                    num = 32
                elif 0xFF01 <= num <= 0xFF5E:
                    num -= 0xfee0
                n += chr(num)
    return n

def get_chinese_numeric():
    my_dict = {}
    my_dict['0']=['zero','零']
    my_dict['1']=['one','一','壹','①','❶','⑴']
    my_dict['2']=['two','二','貳','②','❷','⑵']
    my_dict['3']=['three','三','叁','③','❸','⑶']
    my_dict['4']=['four','四','肆','④','❹','⑷']
    my_dict['5']=['five','五','伍','⑤','❺','⑸']
    my_dict['6']=['six','六','陸','⑥','❻','⑹']
    my_dict['7']=['seven','七','柒','⑦','❼','⑺']
    my_dict['8']=['eight','八','捌','⑧','❽','⑻']
    my_dict['9']=['nine','九','玖','⑨','❾','⑼']

    return my_dict

# 同義字
def synonyms(keyword):
    ret = []
    my_dict = get_chinese_numeric()
    if keyword in my_dict:
        ret = my_dict[keyword]
    else:
        ret.append(keyword)
    return ret

def normalize_chinese_numeric(keyword):
    ret = None
    my_dict = get_chinese_numeric()
    for i in my_dict:
        for item in my_dict[i]:
            if keyword.lower() == item:
                ret = int(i)
                break
        if not ret is None:
            break
    return ret

def find_continuous_number(text):
    chars = "0123456789"
    return find_continuous_pattern(chars, text)

def find_continuous_text(text):
    chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return find_continuous_pattern(chars, text)

def find_continuous_pattern(allowed_char, text):
    ret = ""
    is_allowed_char_start = False
    for char in text:
        #print("char:", char)
        if char in allowed_char:
            if len(ret)==0 and not is_allowed_char_start:
                is_allowed_char_start = True
            if is_allowed_char_start:
                ret += char
        else:
            # make not continuous
            is_allowed_char_start = False
    return ret

def is_all_alpha_or_numeric(text):
    ret = False
    alpha_count = 0
    numeric_count = 0
    for char in text:
        try:
            if char.encode('UTF-8').isalpha():
                alpha_count += 1
        except Exception as exc:
            pass

        #if char.isnumeric():
        if char.isdigit():
            numeric_count += 1

    if (alpha_count + numeric_count) == len(text):
        ret = True

    #print("text/is_all_alpha_or_numeric:",text,ret)
    return ret

def get_favoriate_extension_path(webdriver_path):
    print("webdriver_path:", webdriver_path)
    no_google_analytics_path = os.path.join(webdriver_path,"no_google_analytics_1.1.0.0.crx")
    no_ad_path = os.path.join(webdriver_path,"Adblock_3.16.1.0.crx")
    buster_path = os.path.join(webdriver_path,"Buster_2.0.1.0.crx")
    return no_google_analytics_path, no_ad_path, buster_path

def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    if platform.system().lower()=="windows":
        chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path

def get_chrome_options(webdriver_path, adblock_plus_enable, browser="chrome", headless = False):
    chrome_options = webdriver.ChromeOptions()
    if browser=="edge":
        chrome_options = webdriver.EdgeOptions()
    if browser=="safari":
        chrome_options = webdriver.SafariOptions()

    # some windows cause: timed out receiving message from renderer
    if adblock_plus_enable:
        # PS: this is ocx version.
        no_google_analytics_path, no_ad_path, buster_path = get_favoriate_extension_path(webdriver_path)

        if os.path.exists(no_google_analytics_path):
            chrome_options.add_extension(no_google_analytics_path)
        if os.path.exists(no_ad_path):
            chrome_options.add_extension(no_ad_path)
        if os.path.exists(buster_path):
            chrome_options.add_extension(buster_path)
    if headless:
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--lang=zh-TW')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument("--no-sandbox");

    # for navigator.webdriver
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # Deprecated chrome option is ignored: useAutomationExtension
    #chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "translate":{"enabled": False}})

    #caps = DesiredCapabilities().CHROME
    caps = chrome_options.to_capabilities()

    #caps["pageLoadStrategy"] = u"normal"  #  complete
    caps["pageLoadStrategy"] = u"eager"  #  interactive
    #caps["pageLoadStrategy"] = u"none"

    #caps["unhandledPromptBehavior"] = u"dismiss and notify"  #  default
    #caps["unhandledPromptBehavior"] = u"ignore"
    #caps["unhandledPromptBehavior"] = u"dismiss"
    caps["unhandledPromptBehavior"] = u"accept"

    return chrome_options, caps

def load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable, headless):
    driver = None

    chromedriver_path = get_chromedriver_path(webdriver_path)
    if not os.path.exists(chromedriver_path):
        print("Please download chromedriver and extract zip to webdriver folder from this url:")
        print("請下在面的網址下載與你chrome瀏覽器相同版本的chromedriver,解壓縮後放到webdriver目錄裡：")
        print(URL_CHROME_DRIVER)
    else:
        chrome_service = Service(chromedriver_path)
        chrome_options, caps = get_chrome_options(webdriver_path, adblock_plus_enable, headless=headless)
        try:
            # method 6: Selenium Stealth
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options, desired_capabilities=caps)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)

    if driver_type=="stealth":
        from selenium_stealth import stealth
        # Selenium Stealth settings
        stealth(driver,
              languages=["zh-TW", "zh"],
              vendor="Google Inc.",
              platform="Win32",
              webgl_vendor="Intel Inc.",
              renderer="Intel Iris OpenGL Engine",
              fix_hairline=True,
          )
    #print("driver capabilities", driver.capabilities)

    return driver

def load_chromdriver_uc(webdriver_path, adblock_plus_enable, headless):
    import undetected_chromedriver as uc

    chromedriver_path = get_chromedriver_path(webdriver_path)

    options = uc.ChromeOptions()
    options.page_load_strategy="eager"

    #print("strategy", options.page_load_strategy)

    if adblock_plus_enable:
        no_google_analytics_path, no_ad_path, buster_path = get_favoriate_extension_path(webdriver_path)
        no_google_analytics_folder_path = no_google_analytics_path.replace('.crx','')
        no_ad_folder_path = no_ad_path.replace('.crx','')
        buster_path = buster_path.replace('.crx','')
        load_extension_path = ""
        if os.path.exists(no_google_analytics_folder_path):
            load_extension_path += "," + no_google_analytics_folder_path
        if os.path.exists(no_ad_folder_path):
            load_extension_path += "," + no_ad_folder_path
        if os.path.exists(buster_path):
            load_extension_path += "," + buster_path
        if len(load_extension_path) > 0:
            options.add_argument('--load-extension=' + load_extension_path[1:])

    if headless:
        #options.add_argument('--headless')
        options.add_argument('--headless=new')
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-translate')
    options.add_argument('--lang=zh-TW')
    options.add_argument('--disable-web-security')
    options.add_argument("--no-sandbox");

    options.add_argument("--password-store=basic")
    options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "translate":{"enabled": False}})

    caps = options.to_capabilities()
    caps["unhandledPromptBehavior"] = u"accept"

    driver = None
    try:
        driver = uc.Chrome(executable_path=chromedriver_path, options=options, desired_capabilities=caps, suppress_welcome=False)
    except Exception as exc:
        error_message = str(exc)
        left_part = None
        if "Stacktrace:" in error_message:
            left_part = error_message.split("Stacktrace:")[0]
            print(left_part)

        if "This version of ChromeDriver only supports Chrome version" in error_message:
            print(CONST_CHROME_VERSION_NOT_MATCH_EN)
            print(CONST_CHROME_VERSION_NOT_MATCH_TW)

    else:
        #print("Oops! web driver not on path:",chromedriver_path )
        print('undetected_chromedriver automatically download chromedriver.')
        try:
            driver = uc.Chrome(options=options, desired_capabilities=caps, suppress_welcome=False)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)
            pass

    if driver is None:
        print("create web drive object by undetected_chromedriver fail!")

        if os.path.exists(chromedriver_path):
            print("Unable to use undetected_chromedriver, ")
            print("try to use local chromedriver to launch chrome browser.")
            driver_type = "selenium"
            driver = load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable, headless)
        else:
            print("建議您自行下載 ChromeDriver 到 webdriver 的資料夾下")
            print("you need manually download ChromeDriver to webdriver folder.")

    return driver

def close_browser_tabs(driver):
    if not driver is None:
        try:
            window_handles_count = len(driver.window_handles)
            if window_handles_count > 1:
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except Exception as excSwithFail:
            pass

def get_driver_by_config(config_dict):
    global driver

    # read config.
    homepage = config_dict["homepage"]
    browser = config_dict["browser"]

    driver_type = config_dict["webdriver_type"]

    # output config:
    print("maxbot app version", CONST_APP_VERSION)
    print("python version", platform.python_version())
    print("platform", platform.platform())
    print("homepage", homepage)
    print("browser", browser)
    print("ticket_number", str(config_dict["ticket_number"]))
    print("pass_1_seat_remaining", config_dict["pass_1_seat_remaining"])

    print("==[kktix]==")
    print(config_dict["kktix"])
    print("==[tixcraft]==")
    print(config_dict["tixcraft"])
    print("==[advanced]==")
    print(config_dict["advanced"])
    print("webdriver_type", driver_type)

    # entry point
    if homepage is None:
        homepage = ""
    if len(homepage) == 0:
        homepage = CONST_HOMEPAGE_DEFAULT

    Root_Dir = get_app_root()
    webdriver_path = os.path.join(Root_Dir, "webdriver")
    print("platform.system().lower():", platform.system().lower())

    adblock_plus_enable = config_dict["advanced"]["adblock_plus_enable"]
    headless = config_dict["advanced"]["headless"]

    if browser == "chrome":
        # method 6: Selenium Stealth
        if driver_type != CONST_WEBDRIVER_TYPE_UC:
            driver = load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable, headless)
        else:
            # method 5: uc
            # multiprocessing not work bug.
            if platform.system().lower()=="windows":
                if hasattr(sys, 'frozen'):
                    from multiprocessing import freeze_support
                    freeze_support()
            driver = load_chromdriver_uc(webdriver_path, adblock_plus_enable, headless)

    if browser == "firefox":
        # default os is linux/mac
        # download url: https://github.com/mozilla/geckodriver/releases
        chromedriver_path = os.path.join(webdriver_path,"geckodriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"geckodriver.exe")

        if "macos" in platform.platform().lower():
            if "arm64" in platform.platform().lower():
                chromedriver_path = os.path.join(webdriver_path,"geckodriver_arm")

        webdriver_service = Service(chromedriver_path)
        driver = None
        try:
            from selenium.webdriver.firefox.options import Options
            options = Options()
            if headless:
                options.add_argument('--headless')
                #options.add_argument('--headless=new')
            if platform.system().lower()=="windows":
                options.binary_location = r'C:\\Program Files\\Mozilla Firefox\\firefox.exe'

            driver = webdriver.Firefox(service=webdriver_service, options=options)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)
            else:
                print(exc)

    if browser == "edge":
        # default os is linux/mac
        # download url: https://developer.microsoft.com/zh-tw/microsoft-edge/tools/webdriver/
        chromedriver_path = os.path.join(webdriver_path,"msedgedriver")
        if platform.system().lower()=="windows":
            chromedriver_path = os.path.join(webdriver_path,"msedgedriver.exe")

        webdriver_service = Service(chromedriver_path)
        chrome_options, caps = get_chrome_options(webdriver_path, adblock_plus_enable, browser="edge", headless=headless)

        driver = None
        try:
            driver = webdriver.Edge(service=webdriver_service, options=chrome_options)
        except Exception as exc:
            error_message = str(exc)
            #print(error_message)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if browser == "safari":
        driver = None
        try:
            driver = webdriver.Safari()
        except Exception as exc:
            error_message = str(exc)
            #print(error_message)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

    if driver is None:
        print("create web driver object fail @_@;")
    else:
        try:
            if 'kktix.c' in homepage:
                if len(config_dict["advanced"]["kktix_account"])>0:
                    if not 'https://kktix.com/users/sign_in?' in homepage:
                        homepage = CONST_KKTIX_SIGN_IN_URL % (homepage)

            if 'famiticket.com' in homepage:
                pass

            if 'ibon.com' in homepage:
                pass

            if 'kham.com' in homepage:
                if len(config_dict["advanced"]["kham_account"])>0:
                    homepage = CONST_KHAM_SIGN_IN_URL

            if 'urbtix.hk' in homepage:
                if len(config_dict["advanced"]["urbtix_account"])>0:
                    homepage = CONST_URBTIX_SIGN_IN_URL

            if 'cityline.com' in homepage:
                if len(config_dict["advanced"]["cityline_account"])>0:
                    homepage = CONST_CITYLINE_SIGN_IN_URL

            if 'hkticketing.com' in homepage:
                if len(config_dict["advanced"]["hkticketing_account"])>0:
                    homepage = CONST_HKTICKETING_SIGN_IN_URL

            if 'galaxymacau.com' in homepage:
                pass

            print("goto url:", homepage)
            driver.get(homepage)
            time.sleep(3.0)

            tixcraft_family = False
            if 'tixcraft.com' in homepage:
                tixcraft_family = True

            if 'indievox.com' in homepage:
                tixcraft_family = True

            if 'ticketmaster.' in homepage:
                tixcraft_family = True

            if tixcraft_family:
                if len(config_dict["advanced"]["tixcraft_sid"]) > 1:
                    tixcraft_sid = decryptMe(config_dict["advanced"]["tixcraft_sid"])
                    driver.delete_cookie("SID")
                    driver.add_cookie({"name":"SID", "value": tixcraft_sid, "path" : "/", "secure":True})

            if 'ibon.com' in homepage:
                if len(config_dict["advanced"]["ibonqware"]) > 1:
                    ibonqware = decryptMe(config_dict["advanced"]["ibonqware"])
                    driver.delete_cookie("ibonqware")
                    driver.add_cookie({"name":"ibonqware", "value": ibonqware, "domain" : "ibon.com.tw", "secure":True})

        except WebDriverException as exce2:
            print('oh no not again, WebDriverException')
            print('WebDriverException:', exce2)
        except Exception as exce1:
            print('get URL Exception:', exce1)
            pass

    return driver

# common functions.
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# convert web string to reg pattern
def convert_string_to_pattern(my_str, dynamic_length=True):
    my_hint_anwser_length = len(my_str)
    my_formated = ""
    if my_hint_anwser_length > 0:
        my_anwser_symbols = u"()[]<>{}-"
        for idx in range(my_hint_anwser_length):
            char = my_str[idx:idx+1]

            if char in my_anwser_symbols:
                my_formated += (u'\\' + char)
                continue

            pattern = re.compile(u"[A-Z]")
            match_result = pattern.match(char)
            #print("match_result A:", match_result)
            if not match_result is None:
                my_formated += u"[A-Z]"

            pattern = re.compile(u"[a-z]")
            match_result = pattern.match(char)
            #print("match_result a:", match_result)
            if not match_result is None:
                my_formated += u"[a-z]"

            pattern = re.compile(u"[\d]")
            match_result = pattern.match(char)
            #print("match_result d:", match_result)
            if not match_result is None:
                my_formated += u"[\d]"

        # for dynamic length
        if dynamic_length:
            for i in range(10):
                my_formated = my_formated.replace(u"[A-Z][A-Z]",u"[A-Z]")
                my_formated = my_formated.replace(u"[a-z][a-z]",u"[a-z]")
                my_formated = my_formated.replace(u"[\d][\d]",u"[\d]")

            my_formated = my_formated.replace(u"[A-Z]",u"[A-Z]+")
            my_formated = my_formated.replace(u"[a-z]",u"[a-z]+")
            my_formated = my_formated.replace(u"[\d]",u"[\d]+")
    return my_formated

def guess_answer_list_from_multi_options(tmp_text):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    options_list = None
    matched_pattern = ""
    if options_list is None:
        if u'【' in tmp_text and u'】' in tmp_text:
            pattern = '【.{1,4}】'
            options_list = re.findall(pattern, tmp_text)
            if len(options_list) <= 2:
                options_list = None
            else:
                matched_pattern = pattern

    if options_list is None:
        if u'(' in tmp_text and u')' in tmp_text:
            pattern = '\(.{1,4}\)'
            options_list = re.findall(pattern, tmp_text)
            if len(options_list) <= 2:
                options_list = None
            else:
                matched_pattern = pattern

    if options_list is None:
        if u'[' in tmp_text and u']' in tmp_text:
            pattern = '\[.{1,4}\]'
            options_list = re.findall(pattern, tmp_text)
            if len(options_list) <= 2:
                options_list = None
            else:
                matched_pattern = pattern

    if options_list is None:
        if "\n" in tmp_text and u')' in tmp_text:
            pattern = "\\n.{1,4}\)"
            options_list = re.findall(pattern, tmp_text)
            if len(options_list) <= 2:
                options_list = None
            else:
                matched_pattern = pattern

    if options_list is None:
        if "\n" in tmp_text and u']' in tmp_text:
            pattern = "\\n.{1,4}\]"
            options_list = re.findall(pattern, tmp_text)
            if len(options_list) <= 2:
                options_list = None
            else:
                matched_pattern = pattern

    if options_list is None:
        if "\n" in tmp_text and u'】' in tmp_text:
            pattern = "\\n.{1,4}】"
            options_list = re.findall(pattern, tmp_text)
            if len(options_list) <= 2:
                options_list = None
            else:
                matched_pattern = pattern

    if options_list is None:
        if "\n" in tmp_text and u':' in tmp_text:
            pattern = "\\n.{1,4}:"
            options_list = re.findall(pattern, tmp_text)
            if len(options_list) <= 2:
                options_list = None
            else:
                matched_pattern = pattern

    if show_debug_message:
        print("matched pattern:", matched_pattern)

    # default remove quota
    is_trim_quota = not check_answer_keep_symbol(tmp_text)
    if show_debug_message:
        print("is_trim_quota:", is_trim_quota)

    return_list = None
    if not options_list is None:
        options_list_length = len(options_list)
        if show_debug_message:
            print("options_list_length:", options_list_length)
            print("options_list:", options_list)
        if options_list_length > 2:
            is_all_options_same_length = True
            options_length_count = {}
            for i in range(options_list_length-1):
                current_option_length = len(options_list[i])
                next_option_length = len(options_list[i+1])
                if current_option_length != next_option_length:
                    is_all_options_same_length = False
                if current_option_length in options_length_count:
                    options_length_count[current_option_length] += 1
                else:
                    options_length_count[current_option_length] = 1

            if show_debug_message:
                print("is_all_options_same_length:", is_all_options_same_length)

            if is_all_options_same_length:
                return_list = []
                for each_option in options_list:
                    if is_trim_quota:
                        return_list.append(each_option[1:-1])
                    else:
                        return_list.append(each_option)
            else:
                #print("options_length_count:", options_length_count)
                if len(options_length_count) > 0:
                    target_option_length = 0
                    most_length_count = 0
                    for k in options_length_count.keys():
                        if options_length_count[k] > most_length_count:
                            most_length_count = options_length_count[k]
                            target_option_length = k
                    #print("most_length_count:", most_length_count)
                    #print("target_option_length:", target_option_length)
                    if target_option_length > 0:
                        return_list = []
                        for each_option in options_list:
                            current_option_length = len(each_option)
                            if current_option_length == target_option_length:
                                if is_trim_quota:
                                    return_list.append(each_option[1:-1])
                                else:
                                    return_list.append(each_option)

    # something is wrong, give up those options.
    if not return_list is None:
        if len(return_list) <= 2:
            return_list = None

    # remove chinese work options.
    if not return_list is None:
        new_list = []
        for item in return_list:
            if is_all_alpha_or_numeric(item):
                new_list.append(item)
        if len(new_list) >=3:
            return_list = new_list

    return return_list

#PS: this may get a wrong answer list. XD
def guess_answer_list_from_symbols(captcha_text_div_text):
    return_list = None
    # need replace to space to get first options.
    tmp_text = captcha_text_div_text
    tmp_text = tmp_text.replace(u'?',u' ')
    tmp_text = tmp_text.replace(u'？',u' ')
    tmp_text = tmp_text.replace(u'。',u' ')

    delimitor_symbols_left = [u"(",u"[",u"{", " ", " ", " ", " "]
    delimitor_symbols_right = [u")",u"]",u"}", ":", ".", ")", "-"]
    idx = -1
    for idx in range(len(delimitor_symbols_left)):
        symbol_left = delimitor_symbols_left[idx]
        symbol_right = delimitor_symbols_right[idx]
        if symbol_left in tmp_text and symbol_right in tmp_text and u'半形' in tmp_text:
            hint_list = re.findall(u'\\'+ symbol_left + u'[\\w]+\\'+ symbol_right , tmp_text)
            #print("hint_list:", hint_list)
            if not hint_list is None:
                if len(hint_list) > 1:
                    return_list = []
                    my_answer_delimitor = symbol_right
                    for options in hint_list:
                        if len(options) > 2:
                            my_anwser = options[1:-1]
                            #print("my_anwser:",my_anwser)
                            if len(my_anwser) > 0:
                                return_list.append(my_anwser)

        if not return_list is None:
            break
    return return_list

def get_offical_hint_string_from_symbol(symbol, tmp_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    offical_hint_string = ""
    if symbol in tmp_text:
        # start to guess offical hint
        if offical_hint_string == "":
            if u'【' in tmp_text and u'】' in tmp_text:
                hint_list = re.findall(u'【.*?】', tmp_text)
                if not hint_list is None:
                    if show_debug_message:
                        print("【.*?】hint_list:", hint_list)
                    for hint in hint_list:
                        if symbol in hint:
                            offical_hint_string = hint[1:-1]
                            break
        if offical_hint_string == "":
            if u'(' in tmp_text and u')' in tmp_text:
                hint_list = re.findall(u'\(.*?\)', tmp_text)
                if not hint_list is None:
                    if show_debug_message:
                        print("\(.*?\)hint_list:", hint_list)
                    for hint in hint_list:
                        if symbol in hint:
                            offical_hint_string = hint[1:-1]
                            break
        if offical_hint_string == "":
            if u'[' in tmp_text and u']' in tmp_text:
                hint_list = re.findall(u'[.*?]', tmp_text)
                if not hint_list is None:
                    if show_debug_message:
                        print("[.*?]hint_list:", hint_list)
                    for hint in hint_list:
                        if symbol in hint:
                            offical_hint_string = hint[1:-1]
                            break
        if offical_hint_string == "":
            offical_hint_string = tmp_text
    return offical_hint_string

def guess_answer_list_from_hint(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, captcha_text_div_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    return_list = None

    tmp_text = format_question_string(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, captcha_text_div_text)

    my_question = ""
    my_options = ""
    offical_hint_string = ""
    offical_hint_string_anwser = ""
    my_anwser_formated = ""
    my_answer_delimitor = ""

    if my_question == "":
        if u"?" in tmp_text:
            question_index = tmp_text.find(u"?")
            my_question = tmp_text[:question_index+1]
    if my_question == "":
        if u"。" in tmp_text:
            question_index = tmp_text.find(u"。")
            my_question = tmp_text[:question_index+1]
    if my_question == "":
        my_question = tmp_text
    #print(u"my_question:", my_question)

    # ps: hint_list is not options list

    if offical_hint_string == "":
        # for: 若你覺得答案為 a，請輸入 a
        if '答案' in tmp_text and CONST_INPUT_SYMBOL in tmp_text:
            offical_hint_string = get_offical_hint_string_from_symbol(CONST_INPUT_SYMBOL, tmp_text)
        if len(offical_hint_string) > 0:
            right_part = offical_hint_string.split(CONST_INPUT_SYMBOL)[1]
            #print("right_part:", right_part)
            if len(offical_hint_string) == len(tmp_text):
                offical_hint_string = right_part

            new_hint = find_continuous_text(right_part)
            if len(new_hint) > 0:
                # TODO: 答案為B需填入Bb)
                #if u'答案' in offical_hint_string and CONST_INPUT_SYMBOL in offical_hint_string:
                offical_hint_string_anwser = new_hint


    if offical_hint_string == "":
        offical_hint_string = get_offical_hint_string_from_symbol(CONST_EXAMPLE_SYMBOL, tmp_text)
        if len(offical_hint_string) > 0:
            right_part = offical_hint_string.split(CONST_EXAMPLE_SYMBOL)[1]
            if len(offical_hint_string) == len(tmp_text):
                offical_hint_string = right_part

            # PS: find first text will only get B char in this case: 答案為B需填入Bb)
            new_hint = find_continuous_text(right_part)
            if len(new_hint) > 0:
                offical_hint_string_anwser = new_hint

    # resize offical_hint_string_anwser for options contains in hint string.
    #print("offical_hint_string_anwser:", offical_hint_string_anwser)
    if len(offical_hint_string_anwser) > 0:
        offical_hint_string = offical_hint_string.split(offical_hint_string_anwser)[0]

    if show_debug_message:
        print("offical_hint_string:", offical_hint_string)

    # try rule4:
    # get hint from rule 3: without '(' & '), but use "*"
    if len(offical_hint_string) == 0:
        target_symbol = u"*"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index + len(target_symbol))
            offical_hint_string = tmp_text[star_index: space_index]

    # is need to merge next block
    if len(offical_hint_string) > 0:
        target_symbol = offical_hint_string + " "
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            next_block_index = star_index + len(target_symbol)
            space_index = tmp_text.find(u" ", next_block_index)
            next_block = tmp_text[next_block_index: space_index]
            if CONST_EXAMPLE_SYMBOL in next_block:
                offical_hint_string += u' ' + next_block

    # try rule5:
    # get hint from rule 3: n個半形英文大寫
    if len(offical_hint_string) == 0:
        target_symbol = u"個半形英文大寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'A' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個英文大寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'A' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個半形英文小寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'a' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個英文小寫"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                offical_hint_string_anwser = u'a' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個英數半形字"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                my_anwser_formated = u'[A-Za-z\d]' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

        target_symbol = u"個半形"
        if target_symbol in tmp_text :
            star_index = tmp_text.find(target_symbol)
            space_index = tmp_text.find(u" ", star_index)
            answer_char_count = tmp_text[star_index-1:star_index]
            if answer_char_count.isnumeric():
                star_index -= 1
                my_anwser_formated = u'[A-Za-z\d]' * int(answer_char_count)
            offical_hint_string = tmp_text[star_index: space_index]

    if len(offical_hint_string) > 0:
        if show_debug_message:
            print("offical_hint_string_anwser:", offical_hint_string_anwser)
        my_anwser_formated = convert_string_to_pattern(offical_hint_string_anwser)

    my_options = tmp_text
    if len(my_question) < len(tmp_text):
        my_options = my_options.replace(my_question,u"")
    my_options = my_options.replace(offical_hint_string,u"")

    # try rule7:
    # check is chinese/english in question, if match, apply my_options rule.
    if len(offical_hint_string) > 0:
        tmp_text_org = captcha_text_div_text
        if CONST_EXAMPLE_SYMBOL in tmp_text:
            tmp_text_org = tmp_text_org.replace(u'Ex:','ex:')
            target_symbol = u"ex:"
            if target_symbol in tmp_text_org :
                star_index = tmp_text_org.find(target_symbol)
                my_options = tmp_text_org[star_index-1:]

    if show_debug_message:
        print("tmp_text:", tmp_text)
        print("my_options:", my_options)

    if len(my_anwser_formated) > 0:
        allow_delimitor_symbols = ")].: }"
        pattern = re.compile(my_anwser_formated)
        search_result = pattern.search(my_options)
        if not search_result is None:
            (span_start, span_end) = search_result.span()
            maybe_delimitor=""
            if len(my_options) > (span_end+1)+1:
                maybe_delimitor = my_options[span_end+0:span_end+1]
            if maybe_delimitor in allow_delimitor_symbols:
                my_answer_delimitor = maybe_delimitor

    if show_debug_message:
        print(u"my_answer_delimitor:", my_answer_delimitor)

    # default remove quota
    is_trim_quota = not check_answer_keep_symbol(tmp_text)
    if show_debug_message:
        print("is_trim_quota:", is_trim_quota)

    if len(my_anwser_formated) > 0:
        new_pattern = my_anwser_formated
        if len(my_answer_delimitor) > 0:
            new_pattern = my_anwser_formated + u'\\' + my_answer_delimitor

        return_list = re.findall(new_pattern, my_options)
        if show_debug_message:
            print("my_anwser_formated:", my_anwser_formated)
            print("new_pattern:", new_pattern)
            print("return_list:" , return_list)

        if not return_list is None:
            if len(return_list) == 1:
                # re-sample for this case.
                return_list = re.findall(my_anwser_formated, my_options)

            if len(return_list) == 1:
                # if use pattern to find matched only one, means it is for example text.
                return_list = None

        if not return_list is None:
            # clean delimitor
            if is_trim_quota:
                return_list_length = len(return_list)
                if return_list_length >= 1:
                    if len(my_answer_delimitor) > 0:
                        for idx in range(return_list_length):
                            return_list[idx]=return_list[idx].replace(my_answer_delimitor,'')
                if show_debug_message:
                    print("cleaned return_list:" , return_list)

    return return_list, offical_hint_string_anwser

def format_question_string(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, captcha_text_div_text):
    tmp_text = captcha_text_div_text
    tmp_text = tmp_text.replace(u'  ',u' ')
    tmp_text = tmp_text.replace(u'：',u':')
    # for hint
    tmp_text = tmp_text.replace(u'*',u'*')

    # stop word.
    tmp_text = tmp_text.replace(u'輸入法',u'')
    tmp_text = tmp_text.replace(u'請問',u'')
    tmp_text = tmp_text.replace(u'請將',u'')
    tmp_text = tmp_text.replace(u'請在',u'')
    tmp_text = tmp_text.replace(u'請以',u'')
    tmp_text = tmp_text.replace(u'請回答',u'')
    tmp_text = tmp_text.replace(u'請',u'')

    # replace ex.
    tmp_text = tmp_text.replace(u'例如', CONST_EXAMPLE_SYMBOL)
    tmp_text = tmp_text.replace(u'如:', CONST_EXAMPLE_SYMBOL)
    tmp_text = tmp_text.replace(u'如為', CONST_EXAMPLE_SYMBOL+'為')

    tmp_text = tmp_text.replace(u'舉例', CONST_EXAMPLE_SYMBOL)
    if not CONST_EXAMPLE_SYMBOL in tmp_text:
        tmp_text = tmp_text.replace(u'例', CONST_EXAMPLE_SYMBOL)
    # important, maybe 例 & ex occurs at same time.
    tmp_text = tmp_text.replace(u'ex:', CONST_EXAMPLE_SYMBOL)
    tmp_text = tmp_text.replace(u'Ex:', CONST_EXAMPLE_SYMBOL)

    #若你覺得
    #PS:這個，可能會造成更多問題，呵呵。
    SYMBOL_IF_LIST = ['假設','如果','若']
    for symbol_if in SYMBOL_IF_LIST:
        if symbol_if in tmp_text and '答案' in tmp_text:
            tmp_text = tmp_text.replace('覺得', '')
            tmp_text = tmp_text.replace('認為', '')
            tmp_text = tmp_text.replace(symbol_if + '你答案', CONST_EXAMPLE_SYMBOL + '答案')
            tmp_text = tmp_text.replace(symbol_if + '答案', CONST_EXAMPLE_SYMBOL + '答案')

    tmp_text = tmp_text.replace(u'填入', CONST_INPUT_SYMBOL)

    #tmp_text = tmp_text.replace(u'[',u'(')
    #tmp_text = tmp_text.replace(u']',u')')
    tmp_text = tmp_text.replace(u'？',u'?')

    tmp_text = tmp_text.replace(u'（',u'(')
    tmp_text = tmp_text.replace(u'）',u')')

    return tmp_text

def permutations(iterable, r=None):
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = list(range(n))
    cycles = list(range(n, n-r, -1))
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return

def get_answer_list_by_question(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, captcha_text_div_text):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    return_list = None

    tmp_text = format_question_string(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, captcha_text_div_text)

    # guess answer list from multi-options: 【】() []
    if return_list is None:
        return_list = guess_answer_list_from_multi_options(tmp_text)
    if show_debug_message:
        print("captcha_text_div_text:", captcha_text_div_text)
        if not return_list is None:
            print("found, guess_answer_list_from_multi_options:", return_list)

    offical_hint_string_anwser = ""
    if return_list is None:
        return_list, offical_hint_string_anwser = guess_answer_list_from_hint(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, captcha_text_div_text)
    else:
        is_match_factorial = False
        mutiple = 0

        return_list_2, offical_hint_string_anwser = guess_answer_list_from_hint(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, captcha_text_div_text)
        if return_list_2 is None:
            if len(offical_hint_string_anwser) >=3:
                if len(return_list) >=3:
                    mutiple = int(len(offical_hint_string_anwser) / len(return_list[0]))
                    if mutiple >=3 :
                        is_match_factorial = True

        if show_debug_message:
            print("mutiple:", mutiple)
            print("is_match_factorial:", is_match_factorial)
        if is_match_factorial:
            is_match_factorial = False
            order_string_list = ['排列','排序','依序','順序','遞增','遞減','升冪','降冪','新到舊','舊到新','小到大','大到小','高到低','低到高']
            for order_string in order_string_list:
                if order_string in tmp_text:
                    is_match_factorial = True

        if is_match_factorial:
            new_array = permutations(return_list, mutiple)
            #print("new_array:", new_array)
            
            return_list = []
            for item_tuple in new_array:
                return_list.append(''.join(item_tuple))

    if show_debug_message:
        if not return_list is None:
            print("found, guess_answer_list_from_hint:", return_list)

    if return_list is None:
        return_list = guess_answer_list_from_symbols(captcha_text_div_text)
    if show_debug_message:
        if not return_list is None:
            print("found, guess_answer_list_from_symbols:", return_list)

    return return_list

def force_press_button(driver, select_by, select_query, force_by_js=True):
    ret = False
    next_step_button = None
    try:
        next_step_button = driver.find_element(select_by ,select_query)
        if not next_step_button is None:
            if next_step_button.is_enabled():
                next_step_button.click()
                ret = True
    except Exception as exc:
        #print("find %s clickable Exception:" % (select_query))
        #print(exc)
        pass

        if force_by_js:
            if not next_step_button is None:
                is_visible = False
                try:
                    if next_step_button.is_enabled():
                        is_visible = True
                except Exception as exc:
                    pass

                if is_visible:
                    try:
                        driver.execute_script("arguments[0].click();", next_step_button)
                        ret = True
                    except Exception as exc:
                        pass
    return ret

# close some div on home url.
def tixcraft_home_close_window(driver):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    accept_all_cookies_btn = None
    try:
        accept_all_cookies_btn = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
    except Exception as exc:
        if show_debug_message:
            print("find accept_all_cookies_btn fail")
        pass

    if accept_all_cookies_btn is not None:
        is_visible = False
        try:
            if accept_all_cookies_btn.is_enabled() and accept_all_cookies_btn.is_displayed():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            if show_debug_message:
                print("accept_all_cookies_btn visible. start to press.")
            try:
                accept_all_cookies_btn.click()
            except Exception as exc:
                print("try to click accept_all_cookies_btn fail, force click by js.")
                try:
                    driver.execute_script("arguments[0].click();", accept_all_cookies_btn)
                except Exception as exc:
                    pass
        else:
            if show_debug_message:
                print("accept_all_cookies_btn invisible.")

    close_all_alert_btns = None
    try:
        close_all_alert_btns = driver.find_elements(By.CSS_SELECTOR, "[class='close-alert']")
    except Exception as exc:
        print("find close_all_alert_btns fail")

    if close_all_alert_btns is not None:
        #print('alert count:', len(close_all_alert_btns))
        for alert_btn in close_all_alert_btns:
            # fix bug: Message: stale element reference: element is not attached to the page document
            is_visible = False
            try:
                if alert_btn.is_enabled() and alert_btn.is_displayed():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    alert_btn.click()
                except Exception as exc:
                    print("try to click alert_btn fail, force click by js.")
                    try:
                        driver.execute_script("arguments[0].click();", alert_btn)
                    except Exception as exc:
                        pass

# from detail to game
def tixcraft_redirect(driver, url):
    ret = False

    game_name = ""

    # get game_name from url
    url_split = url.split("/")
    if len(url_split) >= 6:
        game_name = url_split[5]

    if "/activity/detail/%s" % (game_name,) in url:
        # to support teamear
        entry_url = url.replace("/activity/detail/","/activity/game/")
        print("redirec to new url:", entry_url)
        try:
            driver.get(entry_url)
        except Exception as exec1:
            pass
        ret = True

    return ret

def tixcraft_date_auto_select(driver, url, config_dict, domain_name):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    # TODO: implement this feature.
    date_keyword_and = ""
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    # PS: for big events, check sold out text maybe not helpful, due to database is too busy.
    sold_out_text_list = ["選購一空","已售完","No tickets available","Sold out","空席なし","完売した"]
    find_ticket_text_list = ['立即訂購','Find tickets','お申込みへ進む']

    game_name = ""

    if "/activity/game/" in url:
        url_split = url.split("/")
        if len(url_split) >= 6:
            game_name = url_split[5]

    if show_debug_message:
        print('get date game_name:', game_name)
        print("date_auto_select_mode:", auto_select_mode)
        print("date_keyword:", date_keyword)

    check_game_detail = False
    # choose date
    if "/activity/game/%s" % (game_name,) in url:
        if show_debug_message:
            if len(date_keyword) == 0:
                print("date keyword is empty.")
            else:
                print("date keyword:", date_keyword)
        check_game_detail = True

    area_list = None
    if check_game_detail:
        try:
            area_list = driver.find_elements(By.CSS_SELECTOR, '#gameList > table > tbody > tr')
        except Exception as exc:
            print("find #gameList fail")

    is_coming_soon = False
    coming_soon_condictions_list_tw = ['開賣','剩餘','天','小時','分鐘','秒','0',':','/']

    matched_blocks = None
    formated_area_list = None

    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                try:
                    if not row.is_enabled():
                        row_is_enabled=False
                    
                    row_text = ""
                    # check buy button.
                    if row_is_enabled:
                        row_text = row.text
                        if row_text is None:
                            row_text = ""

                        row_is_enabled=False
                        for text_item in find_ticket_text_list:
                            if text_item in row_text:
                                row_is_enabled = True
                                break

                    # check sold out text.
                    if row_is_enabled:
                        if pass_date_is_sold_out_enable:
                            for sold_out_item in sold_out_text_list:
                                row_text_right_part = row_text[(len(sold_out_item)+5)*-1:]
                                if show_debug_message:
                                    #print("check right part text:", row_text_right_part)
                                    pass
                                if sold_out_item in row_text_right_part:
                                    row_is_enabled = False
                                    if show_debug_message:
                                        print("match sold out text: %s, skip this row." % (sold_out_item))
                                    break

                    # check is coming soon.
                    if row_is_enabled:
                        is_match_all_coming_soon_condiction = True
                        for condiction_string in coming_soon_condictions_list_tw:
                            if not condiction_string in row_text:
                                is_match_all_coming_soon_condiction = False
                                break
                        if is_match_all_coming_soon_condiction:
                            if show_debug_message:
                                print("match coming soon condiction at row:", row_text)
                            is_coming_soon = True
                            break

                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

            if show_debug_message:
                print("formated_area_list count:", len(formated_area_list))

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                date_keyword = format_keyword_string(date_keyword)
                if show_debug_message:
                    print("start to match formated keyword:", date_keyword)
                matched_blocks = []

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if date_keyword in row_text:
                                if len(date_keyword_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and # is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if date_keyword_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    is_date_clicked = False
    if target_area is not None:
        is_date_clicked = force_press_button(target_area, By.CSS_SELECTOR,'button')
        if not is_date_clicked:
            # for: ticketmaster.sg
            is_date_clicked = force_press_button(target_area, By.CSS_SELECTOR,'a')

    # [PS]: current reload condition only when
    if auto_reload_coming_soon_page_enable:
        if is_coming_soon:
            if show_debug_message:
                print("match is_coming_soon, start to reload page.")

            # case 2: match one row is coming soon.
            try:
                driver.refresh()
            except Exception as exc:
                pass
        else:
            if not is_date_clicked:
                if not formated_area_list is None:
                    if len(formated_area_list) == 0:
                        print('start to refresh page.')
                        try:
                            driver.refresh()
                            time.sleep(0.3)
                        except Exception as exc:
                            pass

    return is_date_clicked

def ticketmaster_date_auto_select(driver, url, config_dict, domain_name):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    # TODO: implement this feature.
    date_keyword_and = ""
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    # PS: for big events, check sold out text maybe not helpful, due to database is too busy.
    sold_out_text_list = ["選購一空","已售完","No tickets available","Sold out","空席なし","完売した"]
    find_ticket_text_list = ['See Tickets']

    area_list = None
    try:
        area_list = driver.find_elements(By.CSS_SELECTOR, '#list-view > div > div.event-listing > div.accordion-wrapper > div')
    except Exception as exc:
        print("find #gameList fail")

    matched_blocks = None
    formated_area_list = None

    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                try:
                    if not row.is_enabled():
                        row_is_enabled=False
                    
                    row_text = ""
                    # check buy button.
                    if row_is_enabled:
                        row_text = row.text
                        if row_text is None:
                            row_text = ""

                        row_is_enabled=False
                        # must contains 'See Tickets'
                        for text_item in find_ticket_text_list:
                            if text_item in row_text:
                                row_is_enabled = True
                                break

                    # check sold out text.
                    if row_is_enabled:
                        if pass_date_is_sold_out_enable:
                            for sold_out_item in sold_out_text_list:
                                if sold_out_item in row_text:
                                    row_is_enabled = False
                                    if show_debug_message:
                                        print("match sold out text: %s, skip this row." % (sold_out_item))
                                    break

                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

            if show_debug_message:
                print("formated_area_list count:", len(formated_area_list))

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                date_keyword = format_keyword_string(date_keyword)
                if show_debug_message:
                    print("start to match formated keyword:", date_keyword)
                matched_blocks = []

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if date_keyword in row_text:
                                if len(date_keyword_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and # is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if date_keyword_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    is_date_clicked = False
    if target_area is not None:
        is_date_clicked = force_press_button(target_area, By.CSS_SELECTOR,'a')
        if is_date_clicked:
            try:
                window_handles_count = len(driver.window_handles)
                if window_handles_count > 1:
                    driver.switch_to.window(driver.window_handles[0])
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(0.2)
            except Exception as excSwithFail:
                pass


    # [PS]: current reload condition only when
    if auto_reload_coming_soon_page_enable:
        if not is_date_clicked:
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    print('start to refresh page.')
                    try:
                        driver.refresh()
                        time.sleep(0.3)
                    except Exception as exc:
                        pass

    return is_date_clicked

# PURPOSE: get target area list.
# RETURN:
#   is_need_refresh
#   matched_blocks
# PS: matched_blocks will be None, if length equals zero.
def get_tixcraft_target_area(el, config_dict, area_keyword_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    area_auto_select_mode = config_dict["area_auto_select"]["mode"]
    pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]

    is_need_refresh = False
    matched_blocks = None

    area_list = None
    area_list_count = 0
    if el is not None:
        try:
            area_list = el.find_elements(By.TAG_NAME, 'a')
        except Exception as exc:
            #print("find area list a tag fail")
            pass

        if area_list is not None:
            area_list_count = len(area_list)
            if area_list_count == 0:
                print("area list is empty, do refresh!")
                is_need_refresh = True
        else:
            print("area list is None, do refresh!")
            is_need_refresh = True

    if area_list_count > 0:
        matched_blocks = []
        for row in area_list:
            row_is_enabled=False
            try:
                row_is_enabled = row.is_enabled()
            except Exception as exc:
                pass

            row_text = ""
            if row_is_enabled:
                try:
                    row_text = row.text
                except Exception as exc:
                    print("get text fail")
                    break

            if row_text is None:
                row_text = ""

            if len(row_text) > 0:
                area_keyword_exclude = config_dict["area_auto_select"]["area_keyword_exclude"]
                if len(area_keyword_exclude) > 0:
                    area_keyword_exclude_array = json.loads("["+ area_keyword_exclude +"]")
                    for exclude_item in area_keyword_exclude_array:
                        if exclude_item in row_text:
                            row_text = ""

            if len(row_text) > 0:
                # clean stop word.
                row_text = format_keyword_string(row_text)

                is_append_this_row = False

                if len(area_keyword_list) > 0:
                    # must match keyword.
                    is_append_this_row = True
                    area_keyword_array = area_keyword_list.split(' ')
                    for area_keyword in area_keyword_array:
                        area_keyword = format_keyword_string(area_keyword)
                        if not area_keyword in row_text:
                            is_append_this_row = False
                            break
                else:
                    # without keyword.
                    is_append_this_row = True

                if is_append_this_row:
                    if show_debug_message:
                        print("pass_1_seat_remaining_enable:", pass_1_seat_remaining_enable)
                    if pass_1_seat_remaining_enable:
                        area_item_font_el = None
                        try:
                            #print('try to find font tag at row:', row_text)
                            area_item_font_el = row.find_element(By.TAG_NAME, 'font')
                            if not area_item_font_el is None:
                                font_el_text = area_item_font_el.text
                                if font_el_text is None:
                                    font_el_text = ""
                                font_el_text = "@%s@" % (font_el_text)
                                if show_debug_message:
                                    print('font tag text:', font_el_text)
                                    pass
                                for check_item in CONT_STRING_1_SEATS_REMAINING:
                                    if check_item in font_el_text:
                                        if show_debug_message:
                                            print("match pass 1 seats remaining 1 full text:", row_text)
                                            print("match pass 1 seats remaining 2 font text:", font_el_text)
                                        is_append_this_row = False
                            else:
                                #print("row withou font tag.")
                                pass
                        except Exception as exc:
                            #print("find font text in a tag fail:", exc)
                            pass

                if show_debug_message:
                    print("is_append_this_row:", is_append_this_row)

                if is_append_this_row:
                    matched_blocks.append(row)

                    if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        print("only need first item, break area list loop.")
                        break
                    if show_debug_message:
                        print("row_text:" + row_text)
                        print("match:" + area_keyword)

        if len(matched_blocks) == 0:
            matched_blocks = None
            is_need_refresh = True

    return is_need_refresh, matched_blocks

# PS: auto refresh condition 1: no keyword + no hyperlink.
# PS: auto refresh condition 2: with keyword + no hyperlink.
def tixcraft_area_auto_select(driver, url, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
    area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]
    # disable pass 1 seat remaining when target ticket number is 1.
    ticket_number = config_dict["ticket_number"]
    if ticket_number == 1:
        pass_1_seat_remaining_enable = False

    if show_debug_message:
        print("area_keyword:", area_keyword)

    if '/ticket/area/' in url:
        #driver.switch_to.default_content()

        el = None
        try:
            el = driver.find_element(By.CSS_SELECTOR, '.zone')
        except Exception as exc:
            print("find .zone fail, do nothing.")

        if el is not None:
            is_need_refresh = False
            areas = None

            if len(area_keyword) > 0:
                    area_keyword_array = json.loads("["+ area_keyword +"]")
                    for area_keyword_item in area_keyword_array:
                        is_need_refresh, areas = get_tixcraft_target_area(el, config_dict, area_keyword_item)
                        if not is_need_refresh:
                            break
                        else:
                            print("is_need_refresh for keyword:", area_keyword_item)
            else:
                # empty keyword, match all.
                is_need_refresh, areas = get_tixcraft_target_area(el, config_dict, "")

            area_target = None
            if areas is not None:
                #print("area_auto_select_mode", area_auto_select_mode)
                #print("len(areas)", len(areas))
                if len(areas) > 0:
                    target_row_index = 0

                    if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                        pass

                    if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                        target_row_index = len(areas)-1

                    if area_auto_select_mode == CONST_RANDOM:
                        target_row_index = random.randint(0,len(areas)-1)

                    #print("target_row_index", target_row_index)
                    area_target = areas[target_row_index]

            if area_target is not None:
                try:
                    #print("area text:", area_target.text)
                    area_target.click()
                except Exception as exc:
                    print("click area a link fail, start to retry...")
                    try:
                        driver.execute_script("arguments[0].click();", area_target)
                    except Exception as exc:
                        print("click area a link fail, after reftry still fail.")
                        print(exc)
                        pass

            # auto refresh for area list page.
            if is_need_refresh:
                try:
                    driver.refresh()
                except Exception as exc:
                    pass

'''
        el_selectSeat_iframe = None
        try:
            el_selectSeat_iframe = driver.find_element_by_xpath("//iframe[contains(@src,'/ticket/selectSeat/')]")
        except Exception as exc:
            #print("find seat iframe fail")
            pass

        if el_selectSeat_iframe is not None:
            driver.switch_to.frame(el_selectSeat_iframe)

            # click one seat
            el_seat = None
            try:
                el_seat = driver.find_element(By.CSS_SELECTOR, '.empty')
                if el_seat is not None:
                    try:
                        el_seat.click()
                    except Exception as exc:
                        #print("click area button fail")
                        pass
            except Exception as exc:
                print("find empty seat fail")


            # click submit button
            el_confirm_seat = None
            try:
                el_confirm_seat = driver.find_element(By.ID, 'submitSeat')
                if el_confirm_seat is not None:
                    try:
                        el_confirm_seat.click()
                    except Exception as exc:
                        #print("click area button fail")
                        pass
            except Exception as exc:
                print("find submitSeat fail")
'''

def tixcraft_ticket_agree(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    agree_checkbox = None
    try:
        my_css_selector = '#TicketForm_agree'
        agree_checkbox = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find TicketForm_agree fail")
        if show_debug_message:
            print(exc)
        pass

    is_finish_checkbox_click = force_check_checkbox(driver, agree_checkbox)

    return is_finish_checkbox_click

def tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number):
    is_ticket_number_assigned = False
    if select_obj is not None:
        try:
            # target ticket number
            select_obj.select_by_visible_text(ticket_number)
            #select.select_by_value(ticket_number)
            #select.select_by_index(int(ticket_number))
            is_ticket_number_assigned = True
        except Exception as exc:
            print("select_by_visible_text ticket_number fail")
            print(exc)

            try:
                # target ticket number
                select_obj.select_by_visible_text(ticket_number)
                #select.select_by_value(ticket_number)
                #select.select_by_index(int(ticket_number))
                is_ticket_number_assigned = True
            except Exception as exc:
                print("select_by_visible_text ticket_number fail...2")
                print(exc)

                # try buy one ticket
                try:
                    select_obj.select_by_visible_text("1")
                    #select.select_by_value("1")
                    #select.select_by_index(int(ticket_number))
                    is_ticket_number_assigned = True
                except Exception as exc:
                    print("select_by_visible_text 1 fail")
                    pass

    # Plan B.
    # if not is_ticket_number_assigned:
    if False:
        if select is not None:
            try:
                # target ticket number
                #select.select_by_visible_text(ticket_number)
                print("assign ticker number by jQuery:",ticket_number)
                driver.execute_script("$(\"input[type='select']\").val(\""+ ticket_number +"\");")
                is_ticket_number_assigned = True
            except Exception as exc:
                print("jQuery select_by_visible_text ticket_number fail (after click.)")
                print(exc)

    return is_ticket_number_assigned

def guess_tixcraft_question(driver):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    inferred_answer_string = None
    answer_list = []

    form_select = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, '.zone-verify')
    except Exception as exc:
        print("find verify textbox fail")
        pass

    question_text = None
    if form_select is not None:
        try:
            question_text = form_select.text
        except Exception as exc:
            print("get text fail")

    formated_html_text = ""
    if question_text is not None:
        if len(question_text) > 0:
            # format question text.
            formated_html_text = question_text
            formated_html_text = formated_html_text.replace(u'「',u'【')
            formated_html_text = formated_html_text.replace(u'〔',u'【')
            formated_html_text = formated_html_text.replace(u'［',u'【')
            formated_html_text = formated_html_text.replace(u'〖',u'【')
            formated_html_text = formated_html_text.replace(u'[',u'【')

            formated_html_text = formated_html_text.replace(u'」',u'】')
            formated_html_text = formated_html_text.replace(u'〕',u'】')
            formated_html_text = formated_html_text.replace(u'］',u'】')
            formated_html_text = formated_html_text.replace(u'〗',u'】')
            formated_html_text = formated_html_text.replace(u']',u'】')

            if u'【' in formated_html_text and u'】' in formated_html_text:
                # PS: 這個太容易沖突，因為問題類型太多，不能直接使用。
                #inferred_answer_string = find_between(formated_html_text, u"【", u"】")
                pass

    if show_debug_message:
        print("formated_html_text:", formated_html_text)

    is_options_in_question = False

    # 請輸入"YES"，代表您已詳閱且瞭解並同意。
    if inferred_answer_string is None:
        if u'輸入"YES"' in formated_html_text:
            if u'已詳閱' in formated_html_text or '請詳閱' in formated_html_text:
                if u'同意' in formated_html_text:
                    inferred_answer_string = 'YES'

    # 購票前請詳閱注意事項，並於驗證碼欄位輸入【同意】繼續購票流程。
    if inferred_answer_string is None:
        if '驗證碼' in formated_html_text or '驗證欄位' in formated_html_text:
            if '已詳閱' in formated_html_text or '請詳閱' in formated_html_text:
                if '輸入【同意】' in formated_html_text:
                    inferred_answer_string = '同意'

    if inferred_answer_string is None:
        if not question_text is None:
            inferred_answer_string, answer_list = get_answer_list_from_question_string(None, question_text)

    return inferred_answer_string, answer_list

def tixcraft_verify(driver, config_dict, answer_index):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    inferred_answer_string = None
    answer_list = []

    is_retry_user_single_answer = False

    presale_code = config_dict["tixcraft"]["presale_code"]
    presale_code_delimiter = config_dict["tixcraft"]["presale_code_delimiter"]

    if len(presale_code) > 0:
        if len(presale_code_delimiter) > 0:
            if presale_code_delimiter in presale_code:
                answer_list = presale_code.split(presale_code_delimiter)
                if len(answer_list) > 0:
                    if answer_index < len(answer_list)-1:
                        inferred_answer_string = answer_list[answer_index+1]
        else:
            is_retry_user_single_answer = True
            if answer_index < 2:
                inferred_answer_string = presale_code

    if inferred_answer_string is None:
        if config_dict["advanced"]["auto_guess_options"]:
            inferred_answer_string, answer_list = guess_tixcraft_question(driver)
            if inferred_answer_string is None:
                if not answer_list is None:
                    if len(answer_list) > 0:
                        if answer_index < len(answer_list)-1:
                            inferred_answer_string = answer_list[answer_index+1]

    if show_debug_message:
        print("answer_index:", answer_index)
        print("inferred_answer_string:", inferred_answer_string)
        print("answer_index:", answer_index)
        print("is_retry_user_single_answer:", is_retry_user_single_answer)

    form_input = None
    try:
        form_input = driver.find_element(By.CSS_SELECTOR, "input[name='checkCode']")
    except Exception as exc:
        print("find verify code fail")
        pass

    inputed_value = None
    if form_input is not None:
        try:
            inputed_value = form_input.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass

    if inputed_value is None:
        inputed_value = ""

    if not inferred_answer_string is None:
        is_password_sent = False
        if len(inputed_value)==0:
            try:
                # PS: sometime may send key twice...
                form_input.clear()
                form_input.send_keys(inferred_answer_string)
                form_input.send_keys(Keys.ENTER)
                is_password_sent = True

                # guess answer mode.
                answer_index += 1

                if show_debug_message:
                    print("sent password by bot:", inferred_answer_string)
            except Exception as exc:
                pass
        else:
            if inputed_value == inferred_answer_string:
                if show_debug_message:
                    print("sent password by previous time.")
                is_password_sent = True
                try:
                    form_input.send_keys(Keys.ENTER)
                except Exception as exc:
                    pass

            if is_retry_user_single_answer:
                # increase counter for waiting for stop retry.
                answer_index += 1
            else:
                # guess answer mode.
                if answer_index > -1:
                    # here not is first option.
                    inferred_answer_previous = None
                    if answer_index < len(answer_list)-1:
                        inferred_answer_previous = answer_list[answer_index]
                    if inputed_value == inferred_answer_previous:
                        try:
                            form_input.clear()
                            form_input.send_keys(inferred_answer_string)
                            form_input.send_keys(Keys.ENTER)
                            is_password_sent = True
                            if show_debug_message:
                                print("sent password by bot:", inferred_answer_string, "at index:", answer_index+2)

                            answer_index += 1
                        except Exception as exc:
                            pass

        if is_password_sent:
            for i in range(3):
                time.sleep(0.1)

                alert_ret = check_pop_alert(driver)
                if alert_ret:
                    if show_debug_message:
                        print("press accept button at time #", i+1)
                    break
    else:
        if len(inputed_value)==0:
            try:
                form_input.click()
            except Exception as exc:
                pass

    return answer_index

def tixcraft_change_captcha(driver,url):
    try:
        driver.execute_script(f"document.querySelector('.verify-img').children[0].setAttribute('src','{url}');")
    except Exception as exc:
        print("edit captcha element fail")

def tixcraft_toast(driver, message):
    toast_element = None
    try:
        my_css_selector = ".remark-word"
        toast_element = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not toast_element is None:
            driver.execute_script("arguments[0].innerHTML='%s';" % message, toast_element)
    except Exception as exc:
        print("find toast element fail")

def tixcraft_keyin_captcha_code(driver, answer = "", auto_submit = False):
    is_verifyCode_editing = False
    is_form_sumbited = False

    # manually keyin verify code.
    # start to input verify code.
    form_verifyCode = None
    try:
        form_verifyCode = driver.find_element(By.ID, 'TicketForm_verifyCode')
    except Exception as exc:
        print("find form_verifyCode fail")

    if form_verifyCode is not None:
        is_visible = False
        try:
            if form_verifyCode.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        inputed_value = None
        try:
            inputed_value = form_verifyCode.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass
        
        if inputed_value is None:
            inputed_value = ""
        
        if answer==inputed_value:
            # no need to send key.
            is_visible = False

        if is_visible:
            try:
                form_verifyCode.click()
                is_verifyCode_editing = True
            except Exception as exc:
                print("click form_verifyCode fail, tring to use javascript.")
                # plan B
                try:
                    driver.execute_script("document.getElementById(\"TicketForm_verifyCode\").focus();")
                    is_verifyCode_editing = True
                except Exception as exc:
                    #print("click form_verifyCode fail.")
                    pass

            if len(answer) > 0:
                #print("start to fill answer.")
                try:
                    form_verifyCode.clear()
                    form_verifyCode.send_keys(answer)
    
                    if auto_submit:
                        form_verifyCode.send_keys(Keys.ENTER)
                        is_verifyCode_editing = False
                        is_form_sumbited = True
                    else:
                        driver.execute_script("document.getElementById(\"TicketForm_verifyCode\").select();")
                        tixcraft_toast(driver, "※ 按 Enter 如果答案是: " + answer)
                except Exception as exc:
                    print("send_keys ocr answer fail.")

    return is_verifyCode_editing, is_form_sumbited

def tixcraft_reload_captcha(driver, domain_name):
    # manually keyin verify code.
    # start to input verify code.
    ret = False
    form_captcha = None
    try:
        image_id = 'TicketForm_verifyCode-image'
        if 'indievox.com' in domain_name:
            image_id = 'TicketForm_verifyCode-image'
        form_captcha = driver.find_element(By.ID, image_id)
        if not form_captcha is None:
            form_captcha.click()
            ret = True
    except Exception as exc:
        print("find form_captcha fail")

    return ret

def tixcraft_get_ocr_answer(driver, ocr, ocr_captcha_image_source, Captcha_Browser, domain_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ocr_answer = None
    if not ocr is None:
        img_base64 = None

        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.Request_Captcha())

        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'TicketForm_verifyCode-image'
            if 'indievox.com' in domain_name:
                #image_id = 'TicketForm_verifyCode-image'
                pass
            try:
                form_verifyCode_base64 = driver.execute_async_script("""
                    var canvas = document.createElement('canvas');
                    var context = canvas.getContext('2d');
                    var img = document.getElementById('%s');
                    if(img!=null) {
                    canvas.height = img.naturalHeight;
                    canvas.width = img.naturalWidth;
                    context.drawImage(img, 0, 0);
                    callback = arguments[arguments.length - 1];
                    callback(canvas.toDataURL()); }
                    """ % (image_id))
                if not form_verifyCode_base64 is None:
                    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])

                if img_base64 is None:
                    if not Captcha_Browser is None:
                        print("canvas get image fail, use plan_b: NonBrowser")
                        img_base64 = base64.b64decode(Captcha_Browser.Request_Captcha())
            except Exception as exc:
                if show_debug_message:
                    print("canvas exception:", str(exc))
                pass
        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                pass

    return ocr_answer
#PS: credit to LinShihJhang's share
def tixcraft_auto_ocr(driver, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, domain_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online
    print("start to ddddocr")

    is_need_redo_ocr = False
    is_form_sumbited = False

    if not ocr is None:
        if show_debug_message:
            print("away_from_keyboard_enable:", away_from_keyboard_enable)
            print("previous_answer:", previous_answer)
            print("ocr_captcha_image_source:", ocr_captcha_image_source)

        ocr_start_time = time.time()
        ocr_answer = tixcraft_get_ocr_answer(driver, ocr, ocr_captcha_image_source, Captcha_Browser, domain_name)
        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        print("ocr elapsed time:", "{:.3f}".format(ocr_elapsed_time))

        if ocr_answer is None:
            if away_from_keyboard_enable:
                # page is not ready, retry again.
                # PS: usually occur in async script get captcha image.
                is_need_redo_ocr = True
                time.sleep(0.1)
            else:
                tixcraft_keyin_captcha_code(driver)
        else:
            ocr_answer = ocr_answer.strip()
            print("ocr_answer:", ocr_answer)
            if len(ocr_answer)==4:
                who_care_var, is_form_sumbited = tixcraft_keyin_captcha_code(driver, answer = ocr_answer, auto_submit = away_from_keyboard_enable)
            else:
                if not away_from_keyboard_enable:
                    tixcraft_keyin_captcha_code(driver)
                    tixcraft_toast(driver, "※ OCR辨識失敗Q_Q，驗證碼請手動輸入...")
                else:
                    is_need_redo_ocr = True
                    if previous_answer != ocr_answer:
                        previous_answer = ocr_answer
                        print("click captcha again.")
                        if True:
                            # selenium solution.
                            tixcraft_reload_captcha(driver, domain_name)

                            if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
                                time.sleep(0.1)
                        else:
                            # Non_Browser solution.
                            if not Captcha_Browser is None:
                                new_captcha_url = Captcha_Browser.Request_Refresh_Captcha() #取得新的CAPTCHA
                                if new_captcha_url != "":
                                    tixcraft_change_captcha(driver, new_captcha_url) #更改CAPTCHA圖
    else:
        print("ddddocr component is not able to use, you may running in arm environment.")

    return is_need_redo_ocr, previous_answer, is_form_sumbited

def tixcraft_ticket_main_agree(driver, config_dict):
    if config_dict["auto_check_agree"]:
        for i in range(3):
            is_finish_checkbox_click = tixcraft_ticket_agree(driver, config_dict)
            if is_finish_checkbox_click:
                break

def tixcraft_ticket_main(driver, config_dict, ocr, Captcha_Browser, domain_name):
    tixcraft_ticket_main_agree(driver, config_dict)

    # allow agree not enable to assign ticket number.
    form_select = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, '.mobile-select')
    except Exception as exc:
        print("find select fail")
        pass

    # for ticketmaster
    if form_select is None:
        try:
            form_select = driver.find_element(By.CSS_SELECTOR, 'td > select.form-select')
        except Exception as exc:
            print("find form-select fail")
            pass

    select_obj = None
    if form_select is not None:
        is_visible = False
        try:
            if form_select.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        if is_visible:
            try:
                select_obj = Select(form_select)
            except Exception as exc:
                pass

    if not select_obj is None:
        is_ticket_number_assigned = False
        row_text = None
        try:
            row_text = select_obj.first_selected_option.text
        except Exception as exc:
            pass
        if not row_text is None:
            if len(row_text) > 0:
                if row_text != "0":
                    if row_text.isnumeric():
                        # ticket assign.
                        is_ticket_number_assigned = True

        # must wait select object ready to assign ticket number.
        if not is_ticket_number_assigned:
            # only this case: "ticket number not changed by bot" to play sound!
            # PS: I assume each time assign ticket number will succufully changed, so let sound play first.
            check_and_play_sound_for_captcha(config_dict)

            ticket_number = str(config_dict["ticket_number"])
            is_ticket_number_assigned = tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number)

            # must wait ticket number assign to focus captcha.
            if is_ticket_number_assigned:
                tixcraft_ticket_main_ocr(driver, config_dict, ocr, Captcha_Browser, domain_name)

def tixcraft_ticket_main_ocr(driver, config_dict, ocr, Captcha_Browser, domain_name):
    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False
    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]

    if not config_dict["ocr_captcha"]["enable"]:
        tixcraft_keyin_captcha_code(driver)
    else:
        previous_answer = None
        for redo_ocr in range(999):
            is_need_redo_ocr, previous_answer, is_form_sumbited = tixcraft_auto_ocr(driver, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, domain_name)
            if is_form_sumbited:
                # start next loop.
                break

            if not away_from_keyboard_enable:
                break

            if not is_need_redo_ocr:
                break

def kktix_confirm_order_button(driver):
    ret = False

    wait = WebDriverWait(driver, 1)
    next_step_button = None
    try:
        # method #3 wait
        next_step_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.form-actions a.btn-primary')))
        if not next_step_button is None:
            if next_step_button.is_enabled():
                next_step_button.click()
                ret = True
    except Exception as exc:
        print("wait form-actions div wait to be clickable Exception:")
        #print(exc)
        pass

        if not next_step_button is None:
            is_visible = False
            try:
                if next_step_button.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    driver.execute_script("arguments[0].click();", next_step_button)
                    ret = True
                except Exception as exc:
                    pass

    return ret


# PS: There are two "Next" button in kktix.
#   : 1: /events/xxx
#   : 2: /events/xxx/registrations/new
#   : This is ONLY for case-1, because case-2 lenght >5
def kktix_events_press_next_button(driver):
    is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'div.tickets a.btn-point')
    return is_button_clicked

#   : This is for case-2 next button.
def kktix_press_next_button(driver):
    ret = False

    wait = WebDriverWait(driver, 1)
    next_step_button = None
    try:
        # method #1
        #form_actions_div = None
        #form_actions_div = driver.find_element(By.ID, 'registrationsNewApp')
        #next_step_button = form_actions_div.find_element(By.CSS_SELECTOR, 'div.form-actions button.btn-primary')

        # method #2
        # next_step_button = driver.find_element(By.CSS_SELECTOR, '#registrationsNewApp div.form-actions button.btn-primary')

        # method #3 wait
        next_step_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#registrationsNewApp div.form-actions button.btn-primary')))
        if not next_step_button is None:
            if next_step_button.is_enabled():
                next_step_button.click()
                ret = True

    except Exception as exc:
        print("wait form-actions div wait to be clickable Exception:")
        print(exc)
        #pass

        if not next_step_button is None:
            is_visible = False
            try:
                if next_step_button.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    driver.execute_script("arguments[0].click();", next_step_button)
                    ret = True
                except Exception as exc:
                    pass
    return ret

def kktix_captcha_text_value(captcha_inner_div):
    ret = ""

    if captcha_inner_div is not None:
        try:
            captcha_password_text = captcha_inner_div.find_element(By.TAG_NAME, "input")
            if not captcha_password_text is None:
                ret = captcha_password_text.get_attribute('value')
            else:
                print("find captcha input field fail")
        except Exception as exc:
            print("find captcha_inner_div Exception:")
            #print(exc)
            pass

    return ret

def kktix_input_captcha_text(captcha_password_input_tag, inferred_answer_string, force_overwrite = False):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    is_cpatcha_sent = False
    inputed_captcha_text = ""

    if not captcha_password_input_tag is None:
        if force_overwrite:
            try:
                captcha_password_input_tag.send_keys(inferred_answer_string)
                print("send captcha keys:" + inferred_answer_string)
                is_cpatcha_sent = True
                inputed_captcha_text = inferred_answer_string
            except Exception as exc:
                pass
        else:
            # not force overwrite:
            inputed_captcha_text = None
            try:
                inputed_captcha_text = captcha_password_input_tag.get_attribute('value')
            except Exception as exc:
                pass
            if inputed_captcha_text is None:
                inputed_captcha_text = ""

            if len(inputed_captcha_text) == 0:
                try:
                    captcha_password_input_tag.send_keys(inferred_answer_string)
                    print("send captcha keys:" + inferred_answer_string)
                    is_cpatcha_sent = True
                except Exception as exc:
                    pass

    return is_cpatcha_sent

def kktix_travel_price_list(driver, config_dict, kktix_area_keyword):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]
    # disable pass 1 seat remaining when target ticket number is 1.
    ticket_number = config_dict["ticket_number"]
    if ticket_number == 1:
        pass_1_seat_remaining_enable = False

    areas = None
    is_ticket_number_assigned = False

    ticket_price_list = None
    try:
        ticket_price_list = driver.find_elements(By.CSS_SELECTOR, '.display-table-row')
    except Exception as exc:
        ticket_price_list = None
        print("find ticket-price span Exception:")
        print(exc)
        pass

    price_list_count = 0
    if ticket_price_list is not None:
        price_list_count = len(ticket_price_list)
        if show_debug_message:
            print("found price count:", price_list_count)
    else:
        print("find ticket-price span fail")

    is_travel_interrupted = False

    if price_list_count > 0:
        areas = []

        kktix_area_keyword_array = kktix_area_keyword.split(' ')
        kktix_area_keyword_1 = kktix_area_keyword_array[0]
        kktix_area_keyword_1_and = ""
        if len(kktix_area_keyword_array) > 1:
            kktix_area_keyword_1_and = kktix_area_keyword_array[1]

        # clean stop word.
        kktix_area_keyword_1 = format_keyword_string(kktix_area_keyword_1)
        kktix_area_keyword_1_and = format_keyword_string(kktix_area_keyword_1_and)

        if show_debug_message:
            print('kktix_area_keyword_1:', kktix_area_keyword_1)
            print('kktix_area_keyword_1_and:', kktix_area_keyword_1_and)

        row_index = 0
        for row in ticket_price_list:
            row_index += 1

            row_text = ""
            try:
                row_text = row.text
                if show_debug_message:
                    print("get text:", row_text, ",at row:", row_index)
            except Exception as exc:
                row_text = ""
                is_travel_interrupted = True
                print("get text fail.")

            if row_text is None:
                row_text = ""

            if '已售完' in row_text:
                row_text = ""

            if 'Sold Out' in row_text:
                row_text = ""

            if '完売' in row_text:
                row_text = ""

            if len(row_text) > 0:
                area_keyword_exclude = config_dict["area_auto_select"]["area_keyword_exclude"]
                if len(area_keyword_exclude) > 0:
                    area_keyword_exclude_array = json.loads("["+ area_keyword_exclude +"]")
                    for exclude_item in area_keyword_exclude_array:
                        if exclude_item in row_text:
                            row_text = ""
            
            if len(row_text) > 0:
                # clean stop word.
                row_text = format_keyword_string(row_text)

                # check ticket input textbox.
                ticket_price_input = None
                try:
                    ticket_price_input = row.find_element(By.CSS_SELECTOR, "input[type='text']")
                except Exception as exc:
                    pass

                if ticket_price_input is not None:
                    current_ticket_number = ""
                    is_visible = False

                    try:
                        current_ticket_number = str(ticket_price_input.get_attribute('value')).strip()
                        is_visible = ticket_price_input.is_enabled()
                    except Exception as exc:
                        pass

                    if len(current_ticket_number) > 0:
                        if current_ticket_number != "0":
                            is_ticket_number_assigned = True

                    if is_ticket_number_assigned:
                        # no need to travel
                        break

                    is_danger_notice = False
                    if ticket_number > 1:
                        # start to check danger notice.
                        span_danger_popup = None
                        try:
                            span_danger_popup = row.find_element(By.CSS_SELECTOR, "span.danger")
                            if span_danger_popup.is_displayed():
                                is_danger_notice = True
                        except Exception as exc:
                            pass

                        if is_danger_notice:
                            # skip this row, because assign will fail, or fill ticket number as 1.
                            if pass_1_seat_remaining_enable:
                                continue

                    if is_visible:
                        is_match_area = False
                        match_area_code = 0

                        if len(kktix_area_keyword_1) == 0:
                            # keyword #1, empty, direct add to list.
                            is_match_area = True
                            match_area_code = 1
                        else:
                            # MUST match keyword #1.
                            if kktix_area_keyword_1 in row_text:
                                #print('match keyword#1')

                                # because of logic between keywords is AND!
                                if len(kktix_area_keyword_1_and) == 0:
                                    #print('keyword#2 is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if kktix_area_keyword_1_and in row_text:
                                        #print('match keyword#2')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        #print('not match keyword#2')
                                        pass
                            else:
                                #print('not match keyword#1')
                                pass

                        if show_debug_message:
                            print("is_match_area:", is_match_area)
                            print("match_area_code:", match_area_code)

                        if is_match_area:
                            areas.append(ticket_price_input)

            if is_travel_interrupted:
                # not sure to break or continue..., maybe break better.
                break
    else:
        if show_debug_message:
            print("no any price list found.")
        pass

    # unknow issue...
    if is_travel_interrupted:
        pass

    return is_ticket_number_assigned, areas

def kktix_assign_ticket_number(driver, config_dict, kktix_area_keyword):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ticket_number_str = str(config_dict["ticket_number"])
    pass_1_seat_remaining_enable = config_dict["pass_1_seat_remaining"]
    # disable pass 1 seat remaining when target ticket number is 1.
    ticket_number = config_dict["ticket_number"]
    if ticket_number == 1:
        pass_1_seat_remaining_enable = False
    kktix_area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_ticket_number_assigned, areas = kktix_travel_price_list(driver, config_dict, kktix_area_keyword)

    is_need_refresh = False

    ticket_price_input = None
    if not is_ticket_number_assigned:
        if areas is not None:
            if len(areas) > 0:
                target_row_index = 0

                if kktix_area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    pass

                if kktix_area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                    target_row_index = len(areas)-1

                if kktix_area_auto_select_mode == CONST_RANDOM:
                    target_row_index = random.randint(0,len(areas)-1)

                if show_debug_message:
                    print("target_row_index", target_row_index)
                ticket_price_input = areas[target_row_index]
            else:
                is_need_refresh = True

    current_ticket_number = ""
    is_visible = False
    if ticket_price_input is not None:
        if show_debug_message:
            print("try to get input box value.")
        try:
            current_ticket_number = str(ticket_price_input.get_attribute('value')).strip()
            is_visible = ticket_price_input.is_enabled()
        except Exception as exc:
            pass

    if is_visible and len(current_ticket_number) > 0:
        if current_ticket_number == "0":
            try:
                print("asssign ticket number:%s" % ticket_number_str)
                ticket_price_input.clear()
                ticket_price_input.send_keys(ticket_number_str)

                is_ticket_number_assigned = True
            except Exception as exc:
                print("asssign ticket number to ticket-price field Exception:")
                print(exc)
                try:
                    ticket_price_input.clear()
                    ticket_price_input.send_keys("1")
                    is_ticket_number_assigned = True
                except Exception as exc2:
                    pass
        else:
            if show_debug_message:
                print("value already assigned.")
            # already assigned.
            is_ticket_number_assigned = True

    return is_ticket_number_assigned, is_need_refresh

def kktix_get_web_datetime(registrationsNewApp_div):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    web_datetime = None

    is_found_web_datetime = False

    el_web_datetime_list = None
    if not registrationsNewApp_div is None:
        try:
            el_web_datetime_list = registrationsNewApp_div.find_elements(By.TAG_NAME, 'td')
        except Exception as exc:
            if show_debug_message:
                print("find td.ng-binding Exception")
                print(exc)
            pass
        #print("is_found_web_datetime", is_found_web_datetime)

    if el_web_datetime_list is not None:
        el_web_datetime_list_count = len(el_web_datetime_list)
        if el_web_datetime_list_count > 0:
            el_web_datetime = None
            for el_web_datetime in el_web_datetime_list:
                el_web_datetime_text = None
                try:
                    el_web_datetime_text = el_web_datetime.text
                    if show_debug_message:
                        print("el_web_datetime_text:", el_web_datetime_text)
                except Exception as exc:
                    if show_debug_message:
                        print('parse web datetime fail:')
                        print(exc)
                    pass

                if el_web_datetime_text is not None:
                    if len(el_web_datetime_text) > 0:
                        now = datetime.now()
                        #print("now:", now)
                        for guess_year in range(now.year,now.year+3):
                            current_year = str(guess_year)
                            if current_year in el_web_datetime_text:
                                if u'/' in el_web_datetime_text:
                                    web_datetime = el_web_datetime_text
                                    is_found_web_datetime = True
                                    break
                        if is_found_web_datetime:
                            break
    else:
        print("find td.ng-binding fail")

    if show_debug_message:
        print('is_found_web_datetime:', is_found_web_datetime)
        print('web_datetime:', web_datetime)

    return web_datetime

def kktix_hide_blocks(driver):
    is_need_refresh = False
    elements = None
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "div[ng-controller='EventInfoCtrl']")
    except Exception as exc:
        print("find person_agree_terms checkbox Exception")
        pass

    if elements is not None:
        for element in elements:
            if element is not None:
                try:
                    driver.execute_script("arguments[0].innerHTML='';", element);
                except Exception as exc:
                    pass

def kktix_check_agree_checkbox(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_need_refresh = False
    is_finish_checkbox_click = False

    kktix_hide_blocks(driver)

    agree_checkbox = None
    try:
        agree_checkbox = driver.find_element(By.ID, 'person_agree_terms')
    except Exception as exc:
        print("find person_agree_terms checkbox Exception")
        if show_debug_message:
            print(exc)
        pass

    if agree_checkbox is not None:
        is_finish_checkbox_click = force_check_checkbox(driver, agree_checkbox)
    else:
        is_need_refresh = True

    if is_need_refresh:
        print("find person_agree_terms checkbox fail, do refresh page.")

    return is_need_refresh, is_finish_checkbox_click


def force_check_checkbox(driver, agree_checkbox):
    is_finish_checkbox_click = False
    if agree_checkbox is not None:
        is_visible = False
        try:
            if agree_checkbox.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            is_checkbox_checked = False
            try:
                if agree_checkbox.is_selected():
                    is_checkbox_checked = True
            except Exception as exc:
                pass

            if not is_checkbox_checked:
                #print('send check to checkbox')
                try:
                    agree_checkbox.click()
                    is_finish_checkbox_click = True
                except Exception as exc:
                    try:
                        driver.execute_script("arguments[0].click();", agree_checkbox)
                        is_finish_checkbox_click = True
                    except Exception as exc:
                        pass
            else:
                is_finish_checkbox_click = True
    return is_finish_checkbox_click


def kktix_check_register_status(driver, url):
    #ex: https://xxx.kktix.cc/events/xxx
    prefix_list = ['.com/events/','.cc/events/']
    postfix = '/registrations/new'

    is_match_event_code = False
    event_code = ""
    for prefix in prefix_list:
        event_code = find_between(url,prefix,postfix)
        if len(event_code) > 0:
            is_match_event_code = True
            #print('event_code:',event_code)
            break

    if is_match_event_code:
        js = '''
function load_kktix_register_code(){
let api_url = "https://kktix.com/g/events/%s/register_info";
fetch(api_url).then(function (response)
{
return response.json();
}
).then(function (data)
{
let reload=false;
console.log(data.inventory.registerStatus);
if(data.inventory.registerStatus=='OUT_OF_STOCK') {reload=true;}
if(data.inventory.registerStatus=='COMING_SOON') {reload=true;}
console.log(reload);
if(reload) {location.reload();}
}
).catch(function (err)
{
console.log(err);
});
}
if (!$.kkUser) {
    $.kkUser = {};
}
if (typeof $.kkUser.checked_status_register_code === 'undefined') {
    $.kkUser.checked_status_register_code = true;
    load_kktix_register_code();
}
        ''' % (event_code)
        try:
            driver.execute_script(js)
        except Exception as exc:
            pass

        # use javascritp version only.
        is_match_event_code = False

    html_result = None
    if is_match_event_code:
        url = "https://kktix.com/g/events/%s/register_info" % (event_code)
        #print('event_code:',event_code)
        #print("url:", url)

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        headers = {"Accept-Language": "zh-TW,zh;q=0.5", 'User-Agent': user_agent}

        try:
            html_result = requests.get(url , headers=headers, timeout=0.7, allow_redirects=False)
        except Exception as exc:
            html_result = None
            print("send reg_info request fail:")
            print(exc)

    registerStatus = None
    if not html_result is None:
        status_code = html_result.status_code
        #print("status_code:",status_code)

        if status_code == 200:
            html_text = html_result.text
            #print("html_text:", html_text)

            try:
                jsLoads = json.loads(html_text)
                if 'inventory' in jsLoads:
                    if 'registerStatus' in jsLoads['inventory']:
                        registerStatus = jsLoads['inventory']['registerStatus']
            except Exception as exc:
                print("load reg_info json fail:")
                print(exc)
                pass

    #print("registerStatus:", registerStatus)
    return registerStatus

def get_answer_string_from_web_date(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, registrationsNewApp_div, captcha_text_div_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    inferred_answer_string = None

    is_need_parse_web_datetime = False
    # '半形阿拉伯數字' & '半形數字'
    if u'半形' in captcha_text_div_text and u'字' in captcha_text_div_text:
        if u'演出日期' in captcha_text_div_text:
            is_need_parse_web_datetime = True
        if u'活動日期' in captcha_text_div_text:
            is_need_parse_web_datetime = True
        if u'表演日期' in captcha_text_div_text:
            is_need_parse_web_datetime = True
        if u'開始日期' in captcha_text_div_text:
            is_need_parse_web_datetime = True
        if u'演唱會日期' in captcha_text_div_text:
            is_need_parse_web_datetime = True
        if u'展覽日期' in captcha_text_div_text:
            is_need_parse_web_datetime = True
        if u'音樂會日期' in captcha_text_div_text:
            is_need_parse_web_datetime = True
    if u'the date of the show you purchased' in captcha_text_div_text:
        is_need_parse_web_datetime = True

    if show_debug_message:
        print("is_need_parse_web_datetime:", is_need_parse_web_datetime)

    if is_need_parse_web_datetime:
        web_datetime = kktix_get_web_datetime(registrationsNewApp_div)
        if not web_datetime is None:
            if show_debug_message:
                print("web_datetime:", web_datetime)

            captcha_text_formatted = format_question_string(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, captcha_text_div_text)
            if show_debug_message:
                print("captcha_text_formatted", captcha_text_formatted)

            my_datetime_foramted = None

            # MMDD
            if my_datetime_foramted is None:
                if u'4位半形' in captcha_text_formatted:
                    my_datetime_foramted = "%m%d"

            # for "如為2月30日，請輸入0230"
            if my_datetime_foramted is None:
                right_part = ""
                if CONST_EXAMPLE_SYMBOL in captcha_text_formatted:
                    right_part = captcha_text_formatted.split(CONST_EXAMPLE_SYMBOL)[1]

                if CONST_INPUT_SYMBOL in right_part:
                    right_part = right_part.split(CONST_INPUT_SYMBOL)[1]
                    number_text = find_continuous_number(right_part)

                    my_anwser_formated = convert_string_to_pattern(number_text, dynamic_length=False)
                    if my_anwser_formated == u"[\\d][\\d][\\d][\\d][\\d][\\d][\\d][\\d]":
                        my_datetime_foramted = "%Y%m%d"
                    if my_anwser_formated == u"[\\d][\\d][\\d][\\d]":
                        my_datetime_foramted = "%m%d"
                    #print("my_datetime_foramted:", my_datetime_foramted)

            if show_debug_message:
                print("my_datetime_foramted", my_datetime_foramted)

            if my_datetime_foramted is None:
                now = datetime.now()
                for guess_year in range(now.year-4,now.year+2):
                    current_year = str(guess_year)
                    if current_year in captcha_text_formatted:
                        my_hint_index = captcha_text_formatted.find(current_year)
                        my_hint_anwser = captcha_text_formatted[my_hint_index:]
                        #print("my_hint_anwser:", my_hint_anwser)
                        # get after.
                        my_delimitor_symbol = CONST_EXAMPLE_SYMBOL
                        if my_delimitor_symbol in my_hint_anwser:
                            my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                            my_hint_anwser = my_hint_anwser[my_delimitor_index+len(my_delimitor_symbol):]
                        #print("my_hint_anwser:", my_hint_anwser)
                        # get before.
                        my_delimitor_symbol = u'，'
                        if my_delimitor_symbol in my_hint_anwser:
                            my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                            my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                        my_delimitor_symbol = u'。'
                        if my_delimitor_symbol in my_hint_anwser:
                            my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                            my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                        # PS: space may not is delimitor...
                        my_delimitor_symbol = u' '
                        if my_delimitor_symbol in my_hint_anwser:
                            my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                            my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                        #remove last char.
                        remove_last_char_list = [')','(','.','。','）','（','[',']']
                        for check_char in remove_last_char_list:
                            if my_hint_anwser[-1:]==check_char:
                                my_hint_anwser = my_hint_anwser[:-1]

                        my_anwser_formated = convert_string_to_pattern(my_hint_anwser, dynamic_length=False)
                        if my_anwser_formated == u"[\\d][\\d][\\d][\\d][\\d][\\d][\\d][\\d]":
                            my_datetime_foramted = "%Y%m%d"
                        if my_anwser_formated == u"[\\d][\\d][\\d][\\d]/[\\d][\\d]/[\\d][\\d]":
                            my_datetime_foramted = "%Y/%m/%d"

                        if show_debug_message:
                            print("my_hint_anwser:", my_hint_anwser)
                            print("my_anwser_formated:", my_anwser_formated)
                            print("my_datetime_foramted:", my_datetime_foramted)
                        break

            if not my_datetime_foramted is None:
                my_delimitor_symbol = ' '
                if my_delimitor_symbol in web_datetime:
                    web_datetime = web_datetime[:web_datetime.find(my_delimitor_symbol)]
                date_time = datetime.strptime(web_datetime,u"%Y/%m/%d")
                if show_debug_message:
                    print("our web date_time:", date_time)
                ans = None
                try:
                    if not date_time is None:
                        ans = date_time.strftime(my_datetime_foramted)
                except Exception as exc:
                    pass
                inferred_answer_string = ans
                if show_debug_message:
                    print("web date_time anwser:", ans)

    return inferred_answer_string

def get_answer_string_from_web_time(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, registrationsNewApp_div, captcha_text_div_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    inferred_answer_string = None

    # parse '演出時間'
    is_need_parse_web_time = False
    if u'半形' in captcha_text_div_text:
        if u'演出時間' in captcha_text_div_text:
            is_need_parse_web_time = True
        if u'表演時間' in captcha_text_div_text:
            is_need_parse_web_time = True
        if u'開始時間' in captcha_text_div_text:
            is_need_parse_web_time = True
        if u'演唱會時間' in captcha_text_div_text:
            is_need_parse_web_time = True
        if u'展覽時間' in captcha_text_div_text:
            is_need_parse_web_time = True
        if u'音樂會時間' in captcha_text_div_text:
            is_need_parse_web_time = True
        if u'the time of the show you purchased' in captcha_text_div_text:
            is_need_parse_web_time = True

    #print("is_need_parse_web_time", is_need_parse_web_time)
    if is_need_parse_web_time:
        web_datetime = None
        if not registrationsNewApp_div is None:
            web_datetime = kktix_get_web_datetime(registrationsNewApp_div)
        if not web_datetime is None:
            tmp_text = format_question_string(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, captcha_text_div_text)

            my_datetime_foramted = None

            if my_datetime_foramted is None:
                my_hint_anwser = tmp_text

                my_delimitor_symbol = CONST_EXAMPLE_SYMBOL
                if my_delimitor_symbol in my_hint_anwser:
                    my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                    my_hint_anwser = my_hint_anwser[my_delimitor_index+len(my_delimitor_symbol):]
                #print("my_hint_anwser:", my_hint_anwser)
                # get before.
                my_delimitor_symbol = u'，'
                if my_delimitor_symbol in my_hint_anwser:
                    my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                    my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                my_delimitor_symbol = u'。'
                if my_delimitor_symbol in my_hint_anwser:
                    my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                    my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                # PS: space may not is delimitor...
                my_delimitor_symbol = u' '
                if my_delimitor_symbol in my_hint_anwser:
                    my_delimitor_index = my_hint_anwser.find(my_delimitor_symbol)
                    my_hint_anwser = my_hint_anwser[:my_delimitor_index]
                my_anwser_formated = convert_string_to_pattern(my_hint_anwser, dynamic_length=False)
                #print("my_hint_anwser:", my_hint_anwser)
                #print(u"my_anwser_formated:", my_anwser_formated)
                if my_anwser_formated == u"[\\d][\\d][\\d][\\d]":
                    my_datetime_foramted = "%H%M"
                    if u'12小時' in tmp_text:
                        my_datetime_foramted = "%I%M"

                if my_anwser_formated == u"[\\d][\\d]:[\\d][\\d]":
                    my_datetime_foramted = "%H:%M"
                    if u'12小時' in tmp_text:
                        my_datetime_foramted = "%I:%M"

            if not my_datetime_foramted is None:
                date_delimitor_symbol = u'('
                if date_delimitor_symbol in web_datetime:
                    date_delimitor_symbol_index = web_datetime.find(date_delimitor_symbol)
                    if date_delimitor_symbol_index > 8:
                        web_datetime = web_datetime[:date_delimitor_symbol_index-1]
                date_time = datetime.strptime(web_datetime,u"%Y/%m/%d %H:%M")
                #print("date_time:", date_time)
                ans = None
                try:
                    ans = date_time.strftime(my_datetime_foramted)
                except Exception as exc:
                    pass
                inferred_answer_string = ans
                #print(u"my_anwser:", ans)

    return inferred_answer_string

def check_answer_keep_symbol(captcha_text_div_text):
    is_need_keep_symbol = False

    # format text
    keep_symbol_tmp = captcha_text_div_text
    keep_symbol_tmp = keep_symbol_tmp.replace(u'也',u'須')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'必須',u'須')

    keep_symbol_tmp = keep_symbol_tmp.replace(u'全都',u'都')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'全部都',u'都')

    keep_symbol_tmp = keep_symbol_tmp.replace(u'一致',u'相同')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'一樣',u'相同')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'相等',u'相同')

    if u'符號須都相同' in keep_symbol_tmp:
        is_need_keep_symbol = True

    if u'符號都相同' in keep_symbol_tmp:
        is_need_keep_symbol = True

    if u'符號須相同' in keep_symbol_tmp:
        is_need_keep_symbol = True

    # for: 大小寫含括號需一模一樣
    keep_symbol_tmp = keep_symbol_tmp.replace(u'含', '')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'和', '')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'與', '')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'還有', '')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'及', '')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'以及', '')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'需', '')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'必須', '')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'而且', '')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'且', '')
    keep_symbol_tmp = keep_symbol_tmp.replace(u'一模', '')
    #print("keep_symbol_tmp:", keep_symbol_tmp)
    if '大小寫括號相同' in keep_symbol_tmp:
        is_need_keep_symbol = True

    return is_need_keep_symbol

def get_answer_list_from_question_string(registrationsNewApp_div, captcha_text_div_text):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    inferred_answer_string = None
    answer_list = None

    CONST_EXAMPLE_SYMBOL = "範例"
    CONST_INPUT_SYMBOL = "輸入"

    if captcha_text_div_text is None:
        captcha_text_div_text = ""

    # 請在下方空白處輸入引號內文字：
    if inferred_answer_string is None:
        is_use_quota_message = False
        if u"「" in captcha_text_div_text and u"」" in captcha_text_div_text:
            if u'下' in captcha_text_div_text and u'空' in captcha_text_div_text and CONST_INPUT_SYMBOL in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                is_use_quota_message = True
            if u'半形' in captcha_text_div_text and CONST_INPUT_SYMBOL in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                is_use_quota_message = True
        #print("is_use_quota_message:" , is_use_quota_message)
        if is_use_quota_message:
            inferred_answer_string = find_between(captcha_text_div_text, u"「", u"」")
            #print("find captcha text:" , inferred_answer_string)

    if inferred_answer_string is None:
        is_use_quota_message = False
        if u"【" in captcha_text_div_text and u"】" in captcha_text_div_text:
            if u'下' in captcha_text_div_text and u'空' in captcha_text_div_text and CONST_INPUT_SYMBOL in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                is_use_quota_message = True
            if u'半形' in captcha_text_div_text and CONST_INPUT_SYMBOL in captcha_text_div_text and u'引號' in captcha_text_div_text and u'字' in captcha_text_div_text:
                is_use_quota_message = True
        #print("is_use_quota_message:" , is_use_quota_message)
        if is_use_quota_message:
            inferred_answer_string = find_between(captcha_text_div_text, u"【", u"】")
            #print("find captcha text:" , inferred_answer_string)

    # parse '演出日期'
    if inferred_answer_string is None:
        inferred_answer_string = get_answer_string_from_web_date(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, registrationsNewApp_div, captcha_text_div_text)

    # parse '演出時間'
    if inferred_answer_string is None:
        inferred_answer_string = get_answer_string_from_web_time(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, registrationsNewApp_div, captcha_text_div_text)

    # name of event.
    if inferred_answer_string is None:
        if u"name of event" in captcha_text_div_text:
            if u'(' in captcha_text_div_text and u')' in captcha_text_div_text and u'ans:' in captcha_text_div_text.lower():
                target_symbol = u"("
                star_index = captcha_text_div_text.find(target_symbol)
                target_symbol = u":"
                star_index = captcha_text_div_text.find(target_symbol, star_index)
                target_symbol = u")"
                end_index = captcha_text_div_text.find(target_symbol, star_index)
                inferred_answer_string = captcha_text_div_text[star_index+1:end_index]
                #print("inferred_answer_string:", inferred_answer_string)

    # 二題式，組合問題。
    is_combine_two_question = False
    if u"第一題" in captcha_text_div_text and u"第二題" in captcha_text_div_text:
        is_combine_two_question = True
    if u"Q1." in captcha_text_div_text and u"Q2." in captcha_text_div_text:
        if u"二題" in captcha_text_div_text:
            is_combine_two_question = True
        if u"2題" in captcha_text_div_text:
            is_combine_two_question = True
    if u"Q1:" in captcha_text_div_text and u"Q2:" in captcha_text_div_text:
        if u"二題" in captcha_text_div_text:
            is_combine_two_question = True
        if u"2題" in captcha_text_div_text:
            is_combine_two_question = True
    if u"Q1 " in captcha_text_div_text and u"Q2 " in captcha_text_div_text:
        if u"二題" in captcha_text_div_text:
            is_combine_two_question = True
        if u"2題" in captcha_text_div_text:
            is_combine_two_question = True
    if is_combine_two_question:
        inferred_answer_string = None
    #print("is_combine_two_question:", is_combine_two_question)


    # still no answer.
    if inferred_answer_string is None:
        if not is_combine_two_question:
            answer_list = get_answer_list_by_question(CONST_EXAMPLE_SYMBOL, CONST_INPUT_SYMBOL, captcha_text_div_text)
            if show_debug_message:
                print("guess answer list:", answer_list)
        else:
            if show_debug_message:
                print("skip to guess answer because of combine question...")

    else:
        if show_debug_message:
            print("got an inferred_answer_string:", inferred_answer_string)


    return inferred_answer_string, answer_list

def kktix_reg_new_captcha(registrationsNewApp_div, captcha_inner_div):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    captcha_text_div = None
    try:
        captcha_text_div = captcha_inner_div.find_element(By.TAG_NAME, "p")
    except Exception as exc:
        pass
        print("find p tag(captcha_text_div) fail")
        print(exc)

    captcha_text_div_text = None
    if captcha_text_div is not None:
        try:
            captcha_text_div_text = captcha_text_div.text
        except Exception as exc:
            pass

    # try to auto answer options.
    answer_list = None
    inferred_answer_string = None

    if not captcha_text_div_text is None:
        if show_debug_message:
            print("captcha_text_div_text:", captcha_text_div_text)
        inferred_answer_string, answer_list = get_answer_list_from_question_string(registrationsNewApp_div, captcha_text_div_text)

    return inferred_answer_string, answer_list

def kktix_double_check_all_text_value(driver, ticket_number):
    is_do_press_next_button = False

    # double check ticket input textbox.
    ticket_price_input_list = None
    try:
        # PS: unable directly access text's value attribute via css selector or xpath on KKTix!
        my_css_selector = "input[type='text']"
        #print("my_css_selector:", my_css_selector)
        ticket_price_input_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass

    if ticket_price_input_list is not None:
        #print("bingo, found one of ticket number textbox.")
        row_index = 0
        for ticket_price_input in ticket_price_input_list:
            row_index += 1
            current_ticket_number = ""
            try:
                current_ticket_number = str(ticket_price_input.get_attribute('value')).strip()
            except Exception as exc:
                pass
            if current_ticket_number is None:
                current_ticket_number = ""
            if len(current_ticket_number) > 0:
                #print(row_index, "current_ticket_number:", current_ticket_number)
                if current_ticket_number == str(ticket_number):
                    #print("bingo, match target ticket number.")

                    # ONLY, this case to auto press next button.
                    is_do_press_next_button = True
                    break

    return is_do_press_next_button

def kktix_reg_captcha(driver, config_dict, answer_index, is_finish_checkbox_click, registrationsNewApp_div):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_captcha_appear = False
    is_captcha_appear_and_filled_password = False
    answer_list = None

    # TODO: in guess options mode, no need to travel div again.
    captcha_inner_div = None
    try:
        captcha_inner_div = driver.find_element(By.CSS_SELECTOR, '.custom-captcha-inner')
    except Exception as exc:
        pass

    captcha_password_input_tag = None
    if not captcha_inner_div is None:
        try:
            captcha_password_input_tag = captcha_inner_div.find_element(By.TAG_NAME, "input")
            if show_debug_message:
                print("found captcha input field")
        except Exception as exc:
            pass

    if not captcha_password_input_tag is None:
        inferred_answer_string = None
        if captcha_inner_div is not None:
            is_captcha_appear = True
            if show_debug_message:
                print("found captcha_inner_div layor.")

            if len(config_dict["kktix"]["user_guess_string"]) > 0:
                inferred_answer_string = config_dict["kktix"]["user_guess_string"]
            else:
                if config_dict["advanced"]["auto_guess_options"]:
                    inferred_answer_string, answer_list = kktix_reg_new_captcha(registrationsNewApp_div, captcha_inner_div)

            if inferred_answer_string is not None:
                # password is not None, try to send.
                is_cpatcha_sent = kktix_input_captcha_text(captcha_password_input_tag, inferred_answer_string)
                if is_cpatcha_sent:
                    is_captcha_appear_and_filled_password = True
            else:
                is_try_to_focus = False
                if answer_list is None:
                    is_try_to_focus = True
                else:
                    if len(answer_list)==0:
                        is_try_to_focus = True

                if is_try_to_focus:
                    # password is None, focus to input, and play sound.
                    inputed_captcha_text = None
                    try:
                        inputed_captcha_text = captcha_password_input_tag.get_attribute('value')
                    except Exception as exc:
                        pass
                    if inputed_captcha_text is None:
                        inputed_captcha_text = ""
                    if len(inputed_captcha_text) == 0:
                        try:
                            #print("focus() captcha to input.")
                            # only this case: "ticket number not changed by bot" to play sound!
                            check_and_play_sound_for_captcha(config_dict)
                            captcha_password_input_tag.click()
                            time.sleep(1)
                            # let user to input answer, bot sleep 1 second.
                        except Exception as exc:
                            pass

        if show_debug_message:
            print("is_captcha_appear:", is_captcha_appear)
            print("is_captcha_appear_and_filled_password:", is_captcha_appear_and_filled_password)

    # retry check agree checkbox again.
    if not is_finish_checkbox_click:
        if config_dict["auto_check_agree"]:
            is_need_refresh, is_finish_checkbox_click = kktix_check_agree_checkbox(driver, config_dict)

    is_do_press_next_button = False
    auto_press_next_step_button = config_dict["kktix"]["auto_press_next_step_button"]
    if auto_press_next_step_button:
        if is_finish_checkbox_click:
            is_do_press_next_button = kktix_double_check_all_text_value(driver, config_dict["ticket_number"])
        else:
            print("still unable to assign checkbox as selected.")

    if show_debug_message:
        print("is_do_press_next_button:", is_do_press_next_button)

    if is_do_press_next_button:
        if not is_captcha_appear:
            click_ret = kktix_press_next_button(driver)
        else:
            if is_captcha_appear_and_filled_password:
                # for easy guest mode, we can fill the password correct.
                #print("for easy guest mode, we can fill the password correct.")
                click_ret = kktix_press_next_button(driver)
            else:
                # not is easy guest mode.
                #print("# not is easy guest mode.")

                # merge with password dictionary, so need remove duplicate list
                # PS: now, there are no password dictionary.
                if not answer_list is None:
                    if len(answer_list) > 1:
                        unique = [x for i, x in enumerate(answer_list) if answer_list.index(x) == i]
                        answer_list = unique

                # start to try answers.
                if not answer_list is None:
                    # for popular event
                    if len(answer_list) > 0:
                        if answer_index < len(answer_list)-1:
                            if kktix_captcha_text_value(captcha_inner_div) == "":
                                answer_index += 1
                                answer_string = answer_list[answer_index]

                                if len(answer_string) > 0:
                                    print("send answer:" + answer_string)
                                    is_cpatcha_sent = kktix_input_captcha_text(captcha_password_input_tag, answer_string)
                                    if is_cpatcha_sent:
                                        kktix_press_next_button(driver)
                        else:
                            # exceed index, do nothing.
                            pass
                else:
                    # captcha appeared, but we don't have answer list.
                    pass

    return answer_index

def kktix_reg_new_main(driver, config_dict, answer_index, is_finish_checkbox_click):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

    # part 1: check div.
    registrationsNewApp_div = None
    try:
        registrationsNewApp_div = driver.find_element(By.CSS_SELECTOR, '#registrationsNewApp')
    except Exception as exc:
        pass
        #print("find input fail:", exc)

    # part 2: assign ticket number
    is_ticket_number_assigned = False
    if not registrationsNewApp_div is None:
        is_need_refresh = False

        if len(area_keyword) > 0:
            for retry_index in range(2):
                area_keyword_array = json.loads("["+ area_keyword +"]")
                for area_keyword_item in area_keyword_array:
                    is_ticket_number_assigned, is_need_refresh = kktix_assign_ticket_number(driver, config_dict, area_keyword_item)
                    if is_ticket_number_assigned:
                        break
                    else:
                        print("is_need_refresh for keyword:", area_keyword_item)

                if is_ticket_number_assigned:
                    break
        else:
            # empty keyword, match all.
            is_ticket_number_assigned, is_need_refresh = kktix_assign_ticket_number(driver, config_dict, "")

        # part 3: captcha
        if is_ticket_number_assigned:
            answer_index = kktix_reg_captcha(driver, config_dict, answer_index, is_finish_checkbox_click, registrationsNewApp_div)
        else:
            if is_need_refresh:
                try:
                    print("no match any price, start to refresh page...")
                    driver.refresh()
                except Exception as exc:
                    #print("refresh fail")
                    pass

    return answer_index

def kktix_reg_new(driver, url, answer_index, kktix_register_status_last, config_dict):
    registerStatus = kktix_register_status_last

    # auto refresh for area list page.
    is_need_refresh = False
    is_finish_checkbox_click = False

    if not is_need_refresh:
        if registerStatus is None:
            # current version, change refresh event from selenium to javascript.
            registerStatus = kktix_check_register_status(driver, url)
            # for request solution, refresh on selenium.
            if not registerStatus is None:
                print("registerStatus:", registerStatus)
                # OUT_OF_STOCK
                if registerStatus != 'IN_STOCK':
                    is_need_refresh = True

    if config_dict["auto_check_agree"]:
        if not is_need_refresh:
            is_need_refresh, is_finish_checkbox_click = kktix_check_agree_checkbox(driver, config_dict)
        if not is_finish_checkbox_click:
            # retry again.
            is_need_refresh, is_finish_checkbox_click = kktix_check_agree_checkbox(driver, config_dict)

    if is_need_refresh:
        try:
            print("try to refresh page...")
            driver.refresh()
        except Exception as exc:
            #print("refresh fail")
            pass

        # reset answer_index
        answer_index = -1
        registerStatus = None
    else:
        # check is able to buy.
        if config_dict["kktix"]["auto_fill_ticket_number"]:
            answer_index = kktix_reg_new_main(driver, config_dict, answer_index, is_finish_checkbox_click)

    return answer_index, registerStatus


# PURPOSE: get target area list.
# PS: this is main block, use keyword to get rows.
# PS: it seems use date_auto_select_mode instead of area_auto_select_mode
def get_fami_target_area(driver, config_dict, area_keyword_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    date_keyword = format_keyword_string(date_keyword)

    area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    area_list = None
    try:
        my_css_selector = "table.session__list > tbody > tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #session date list fail")
        if show_debug_message:
            print(exc)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    if area_list is not None:
        area_list_length = len(area_list)
        if show_debug_message:
            print("lenth of area rows:", area_list_length)

        if area_list_length > 0:
            formated_area_list = []

            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                el_btn = None
                try:
                    my_css_selector = "button"
                    el_btn = row.find_element(By.TAG_NAME, my_css_selector)
                    if el_btn is not None:
                        if not el_btn.is_enabled():
                            #print("row's button disabled!")
                            row_is_enabled=False
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

    matched_blocks = None
    if not formated_area_list is None:
        if len(formated_area_list) > 0:
            matched_blocks = []

            if len(date_keyword)==0 and len(area_keyword_list)==0:
                # select all.
                matched_blocks = formated_area_list
            else:
                # match keyword.
                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    #print("row index:", row_index)

                    date_html_text = ""
                    area_html_text = ""

                    row_text = ""
                    try:
                        my_css_selector = "td:nth-child(1)"
                        td_date = row.find_element(By.CSS_SELECTOR, my_css_selector)
                        if td_date is not None:
                            #print("date:", td_date.text)
                            date_html_text = format_keyword_string(td_date.text)

                        my_css_selector = "td:nth-child(2)"
                        td_area = row.find_element(By.CSS_SELECTOR, my_css_selector)
                        if td_area is not None:
                            #print("area:", td_area.text)
                            area_html_text = format_keyword_string(td_area.text)

                        row_text = row.text
                    except Exception as exc:
                        print("get row text fail")
                        break

                    if row_text is None:
                        row_text = ""

                    if len(row_text) > 0:
                        area_keyword_exclude = config_dict["area_auto_select"]["area_keyword_exclude"]
                        if len(area_keyword_exclude) > 0:
                            area_keyword_exclude_array = json.loads("["+ area_keyword_exclude +"]")
                            for exclude_item in area_keyword_exclude_array:
                                if exclude_item in row_text:
                                    row_text = ""

                    if len(row_text) > 0:
                        # check date.
                        is_match_date = False
                        if len(date_keyword) > 0:
                            if date_keyword in date_html_text:
                                #print("is_match_date")
                                is_match_date = True
                        else:
                            is_match_date = True

                        # check area.
                        is_match_area = False

                        if len(area_keyword_list) > 0:
                            # must match keyword.
                            is_match_area = True
                            area_keyword_array = area_keyword_list.split(' ')
                            for area_keyword in area_keyword_array:
                                area_keyword = format_keyword_string(area_keyword)
                                if not area_keyword in row_text:
                                    is_match_area = False
                                    break
                        else:
                            # without keyword.
                            is_match_area = True

                        if is_match_date and is_match_area:
                            matched_blocks.append(row)

                            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                                print("only need first item, break area list loop.")
                                break


    return_row_count = 0
    if not matched_blocks is None:
        return_row_count = len(matched_blocks)
        if return_row_count==0:
            matched_blocks = None

    if show_debug_message:
        print("return_row_count:", return_row_count)

    return matched_blocks


def fami_activity(driver):
    #print("fami_activity bingo")

    #---------------------------
    # part 1: press "buy" button.
    #---------------------------
    fami_start_to_buy_button = None
    try:
        fami_start_to_buy_button = driver.find_element(By.ID, 'buyWaiting')
    except Exception as exc:
        pass

    is_visible = False
    if fami_start_to_buy_button is not None:
        try:
            if fami_start_to_buy_button.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    if is_visible:
        try:
            fami_start_to_buy_button.click()
        except Exception as exc:
            print("click buyWaiting button fail...")
            #print(exc)
            #pass
            try:
                driver.execute_script("arguments[0].click();", fami_start_to_buy_button)
            except Exception as exc:
                pass


def fami_home(driver, url, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_ticket_number_assigned = False

    ticket_number = str(config_dict["ticket_number"])

    #---------------------------
    # part 3: fill ticket number.
    #---------------------------
    ticket_el = None
    try:
        my_css_selector = "tr.ticket > td > select"
        ticket_el = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass
        print("click buyWaiting button fail")
        #print(exc)

    is_select_box_visible = False
    if ticket_el is not None:
        try:
            if ticket_el.is_enabled():
                is_select_box_visible = True
        except Exception as exc:
            pass

    is_ticket_number_assigned = False
    if is_select_box_visible:
        ticket_number_select = None
        try:
            ticket_number_select = Select(ticket_el)
        except Exception as exc:
            pass

        if ticket_number_select is not None:
            try:
                #print("get select ticket value:" + Select(ticket_number_select).first_selected_option.text)
                if ticket_number_select.first_selected_option.text=="0" or ticket_number_select.first_selected_option.text=="選擇張數":
                    # target ticket number
                    ticket_number_select.select_by_visible_text(ticket_number)
                    is_ticket_number_assigned = True
            except Exception as exc:
                print("select_by_visible_text ticket_number fail")
                print(exc)

                try:
                    # try target ticket number twice
                    ticket_number_select.select_by_visible_text(ticket_number)
                    is_ticket_number_assigned = True
                except Exception as exc:
                    print("select_by_visible_text ticket_number fail...2")
                    print(exc)

                    # try buy one ticket
                    try:
                        ticket_number_select.select_by_visible_text("1")
                        is_ticket_number_assigned = True
                    except Exception as exc:
                        print("select_by_visible_text 1 fail")
                        pass

    #---------------------------
    # part 4: press "next" button.
    #---------------------------
    if is_ticket_number_assigned:
        fami_assign_site_button = None
        try:
            my_css_selector = "div.col > a.btn"
            fami_assign_site_button = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if fami_assign_site_button is not None:
            is_visible = False
            try:
                if fami_assign_site_button.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    fami_assign_site_button.click()
                except Exception as exc:
                    print("click buyWaiting button fail")
                    #print(exc)
                    try:
                        driver.execute_script("arguments[0].click();", fami_assign_site_button)
                    except Exception as exc:
                        pass


    areas = None
    if not is_select_box_visible:
        #---------------------------
        # part 2: select keywords
        #---------------------------

        area_auto_select_mode = config_dict["area_auto_select"]["mode"]
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

        if len(area_keyword) > 0:
            area_keyword_array = json.loads("["+ area_keyword +"]")
            for area_keyword_item in area_keyword_array:
                areas = get_fami_target_area(driver, config_dict, area_keyword_item)
                if not areas is None:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.
            areas = get_fami_target_area(driver, config_dict, "")
            

        area_target = None
        if areas is not None:
            #print("area_auto_select_mode", area_auto_select_mode)
            #print("len(areas)", len(areas))
            if len(areas) > 0:
                target_row_index = 0

                if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    pass

                if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                    target_row_index = len(areas)-1

                if area_auto_select_mode == CONST_RANDOM:
                    target_row_index = random.randint(0,len(areas)-1)

                #print("target_row_index", target_row_index)
                area_target = areas[target_row_index]

        if area_target is not None:
            el_btn = None
            is_visible = False
            try:
                my_css_selector = "button"
                el_btn = area_target.find_element(By.TAG_NAME, my_css_selector)
                if el_btn is not None:
                    if el_btn.is_enabled():
                        is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    el_btn.click()
                except Exception as exc:
                    print("click buy button fail, start to retry...")
                    try:
                        driver.execute_script("arguments[0].click();", el_btn)
                    except Exception as exc:
                        pass


# purpose: date auto select
def urbtix_date_auto_select(driver, auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False
    matched_blocks = None

    # clean stop word.
    date_keyword = format_keyword_string(date_keyword)
    date_keyword_and = ""

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "div.conent-wrapper > div.list-wrapper > ul"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #date-time-position date list fail")
        print(exc)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None

    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []

            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                el_btn = None
                try:
                    my_css_selector = "div.buy-icon"
                    el_btn = row.find_element(By.CSS_SELECTOR, my_css_selector)
                    if el_btn is not None:
                        button_class_string = str(el_btn.get_attribute('class'))
                        if len(button_class_string) > 1:
                            if 'disabled' in button_class_string:
                                if show_debug_message:
                                    print("found disabled activity at row:", row_index)
                                row_is_enabled=False
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

            if show_debug_message:
                print("formated_area_list count:", len(formated_area_list))

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", date_keyword)
                matched_blocks = []

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    #row_is_enabled=False
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if date_keyword in row_text:
                                if len(date_keyword_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and # is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if date_keyword_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        el_btn = None
        try:
            #print("target_area text", target_area.text)
            my_css_selector = "div.buy-icon"
            el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass
        if el_btn is not None:
            is_button_enable = True
            try:
                if not el_btn.is_enabled():
                    is_button_enable = False
                else:
                    # button enable, but class disable.
                    button_class_string = str(el_btn.get_attribute('class'))
                    if len(button_class_string) > 1:
                        if 'disabled' in button_class_string:
                            is_button_enable = False
                if is_button_enable:
                    el_btn.click()
                    ret = True
                    print("buy icon pressed.")
            except Exception as exc:
                # use plan B
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_btn)
                    ret = True
                except Exception as exc:
                    pass
    else:
        # no target.
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        driver.refresh()
                        time.sleep(1.0)
                    except Exception as exc:
                        pass

    return ret

def urbtix_purchase_ticket(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
    is_date_assign_by_bot = urbtix_date_auto_select(driver, date_auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable)

    return is_date_assign_by_bot

# purpose: area auto select
def urbtix_area_auto_select(driver, config_dict, area_keyword_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    matched_blocks = None

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "div.area-info"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)
            print("area_keyword_list:", area_keyword_list)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True

                row_text = ""
                if row_is_enabled:
                    try:
                        row_text = row.text
                    except Exception as exc:
                        pass

                if row_text is None:
                    row_text = ""

                if len(row_text) > 0:
                    area_keyword_exclude = config_dict["area_auto_select"]["area_keyword_exclude"]
                    if len(area_keyword_exclude) > 0:
                        area_keyword_exclude_array = json.loads("["+ area_keyword_exclude +"]")
                        for exclude_item in area_keyword_exclude_array:
                            if exclude_item in row_text:
                                row_text = ""

                if row_text == "":
                    row_is_enabled=False

                button_class_string = None
                if row_is_enabled:
                    try:
                        button_class_string = str(row.get_attribute('class'))
                    except Exception as exc:
                        pass

                if button_class_string is None:
                    button_class_string = ""

                if len(button_class_string) > 1:
                    if 'disabled' in button_class_string:
                        row_is_enabled=False
                    if 'selected' in button_class_string:
                        # someone is selected. skip this process.
                        row_is_enabled=False
                        is_price_assign_by_bot = True
                        break

                if row_is_enabled:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if is_price_assign_by_bot:
        formated_area_list = None

    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            matched_blocks = []
            if len(area_keyword_list) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                row_index = 0
                for row in formated_area_list:
                    row_index += 1

                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False

                            if len(area_keyword_list) > 0:
                                # must match keyword.
                                is_match_area = True
                                area_keyword_array = area_keyword_list.split(' ')
                                for area_keyword in area_keyword_array:
                                    area_keyword = format_keyword_string(area_keyword)
                                    if not area_keyword in row_text:
                                        is_match_area = False
                                        break
                            else:
                                # without keyword.
                                is_match_area = True

                            if is_match_area:
                                matched_blocks.append(row)

            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if area_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        try:
            if target_area.is_enabled():
                target_area.click()
                is_price_assign_by_bot = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                is_price_assign_by_bot = True
            except Exception as exc:
                pass

    return is_need_refresh, is_price_assign_by_bot


def urbtix_ticket_number_auto_select(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_ticket_number_assigned = False

    ticket_number = config_dict["ticket_number"]
    ticket_number_str = str(ticket_number)

    # check ticket input textbox.
    ticket_price_input = None
    try:
        ticket_price_input = driver.find_element(By.CSS_SELECTOR, "input.ticket-count")
    except Exception as exc:
        pass

    if ticket_price_input is not None:
        current_ticket_number = ""
        is_visible = False

        try:
            current_ticket_number = str(ticket_price_input.get_attribute('value')).strip()
            is_visible = ticket_price_input.is_enabled()
        except Exception as exc:
            pass

        if len(current_ticket_number) > 0:
            if current_ticket_number == "0":
                try:
                    print("asssign ticket number:%s" % ticket_number_str)
                    ticket_price_input.clear()
                    ticket_price_input.send_keys(ticket_number_str)

                    is_ticket_number_assigned = True
                except Exception as exc:
                    print("asssign ticket number to ticket-price field Exception:")
                    print(exc)
                    try:
                        ticket_price_input.clear()
                        ticket_price_input.send_keys("1")
                        is_ticket_number_assigned = True
                    except Exception as exc2:
                        pass
            else:
                # already assigned.
                is_ticket_number_assigned = True

    ticket_count = 0

    if is_ticket_number_assigned:
        el_ticket_count = None
        try:
            my_css_selector = "div.left-content > span.total-count"
            el_ticket_count = driver.find_element(By.CSS_SELECTOR, my_css_selector)
            if not el_ticket_count is None:
                tmp_ticket_count = el_ticket_count.text
                if len(tmp_ticket_count) > 0: 
                    if tmp_ticket_count.isdigit():
                        ticket_count = int(tmp_ticket_count)
        except Exception as exc:
            pass

    if is_ticket_number_assigned and ticket_count==0:
        el_btn = None
        try:
            # this is "confirm"(確認) button.
            my_css_selector = "div.footer > div > div"
            el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if el_btn is not None:
            try:
                if el_btn.is_enabled():
                    el_btn.click()
                    print("varify site icon pressed.")
                    time.sleep(0.3)
            except Exception as exc:
                # use plan B
                if show_debug_message:
                    print("varify site icon pressed fail:", exc)
                '''
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_btn)
                    ret = True
                except Exception as exc:
                    pass
                '''
                pass
        else:
            if show_debug_message:
                print("varify site icon is None.")

    if is_ticket_number_assigned and ticket_count>0:
        el_btn = None
        try:
            # this is "add to cart"(加入購物籃)
            my_css_selector = "div.button-inner > div > div.button-text"
            el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

        if el_btn is not None:
            try:
                if el_btn.is_enabled():
                    el_btn.click()
                    time.sleep(0.3)
                    ret = True
                    print("shopping-cart icon pressed.")
            except Exception as exc:
                # use plan B
                if show_debug_message:
                    print("click on button fail:", exc)
                pass
                '''
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_btn)
                    ret = True
                except Exception as exc:
                    pass
                '''
        else:
            if show_debug_message:
                print("shopping-cart site icon is None.")

    return is_ticket_number_assigned

def urbtix_uncheck_adjacent_seat(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    el_checkbox_icon = None
    is_checkbox_checked = False
    try:
        my_css_selector = "div.quantity-inner > div.header > div.right > div.checkbox-wrapper > div.checkbox-icon"
        el_checkbox_icon = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not el_checkbox_icon is None:
            div_class_string = str(el_checkbox_icon.get_attribute('class'))
            if not div_class_string is None:
                if len(div_class_string) > 1:
                    if 'checked' in div_class_string:
                        is_checkbox_checked = True

    except Exception as exc:
        if show_debug_message:
            print(exc)
        pass

    try:
        if is_checkbox_checked:
            el_checkbox_icon.click()
    except Exception as exc:
        if show_debug_message:
            print(exc)

        # force to click when exception.
        try:
            driver.execute_script("arguments[0].click();", el_checkbox_icon)
        except Exception as exc2:
            pass

        pass

def urbtix_performance(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ret = False

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

        if show_debug_message:
            print("area_keyword:", area_keyword)

        if len(area_keyword) > 0:
            area_keyword_array = json.loads("["+ area_keyword +"]")
            for area_keyword_item in area_keyword_array:
                print("area_keyword_item for keyword:", area_keyword_item)
                is_need_refresh, is_price_assign_by_bot = urbtix_area_auto_select(driver, config_dict, area_keyword_item)
                if not is_need_refresh:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.
            is_need_refresh, is_price_assign_by_bot = urbtix_area_auto_select(driver, config_dict, "")

        # un-tested. disable refresh for now.
        is_need_refresh = False
        if is_need_refresh:
            try:
                driver.refresh()
            except Exception as exc:
                pass

        if config_dict["advanced"]["disable_adjacent_seat"]:
            urbtix_uncheck_adjacent_seat(driver, config_dict)

        # choose ticket.
        is_ticket_number_assigned = urbtix_ticket_number_auto_select(driver, config_dict)
        if show_debug_message:
            print("is_ticket_number_assigned:", is_ticket_number_assigned)


    return ret


# purpose: date auto select
def cityline_date_auto_select(driver, auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    ret = False
    matched_blocks = None

    # clean stop word.
    date_keyword = format_keyword_string(date_keyword)
    date_keyword_and = ""

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "button.date-time-position"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #date-time-position date list fail")
        print(exc)

    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                try:
                    if not row.is_enabled():
                        row_is_enabled=False
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

            if show_debug_message:
                print("formated_area_list count:", len(formated_area_list))

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", date_keyword)
                matched_blocks = []

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    #row_is_enabled=False
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if date_keyword in row_text:
                                if len(date_keyword_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and # is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if date_keyword_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        try:
            if target_area.is_enabled():
                target_area.click()
                ret = True
        except Exception as exc:
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                ret = True
            except Exception as exc:
                pass
    else:
        # no target.
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        driver.refresh()
                        time.sleep(0.3)
                    except Exception as exc:
                        pass

    return ret

# purpose: area auto select
# return:
#   True: area block appear.
#   False: area block not appear.
# ps: return is successfully click on the price radio.
def cityline_area_auto_select(driver, config_dict, area_keyword_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    matched_blocks = None

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = ".form-check"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                try:
                    my_css_selector = "span.price-limited > span"
                    span_price_limited = row.find_element(By.CSS_SELECTOR, my_css_selector)
                    if not span_price_limited is None:
                        #print("found span limited at idx:", row_index)
                        span_i18n_string = str(span_price_limited.get_attribute('data-i18n'))
                        if len(span_i18n_string) > 1:
                            if 'soldout' in span_i18n_string:
                                #print("found span limited soldout at idx:", row_index)
                                row_is_enabled=False
                except Exception as exc:
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            matched_blocks = []
            if len(area_keyword_list) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    #row_is_enabled=False
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            area_keyword_exclude = config_dict["area_auto_select"]["area_keyword_exclude"]
                            if len(area_keyword_exclude) > 0:
                                area_keyword_exclude_array = json.loads("["+ area_keyword_exclude +"]")
                                for exclude_item in area_keyword_exclude_array:
                                    if exclude_item in row_text:
                                        row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False

                            if len(area_keyword_list) > 0:
                                # must match keyword.
                                is_match_area = True
                                area_keyword_array = area_keyword_list.split(' ')
                                for area_keyword in area_keyword_array:
                                    area_keyword = format_keyword_string(area_keyword)
                                    if not area_keyword in row_text:
                                        is_match_area = False
                                        break
                            else:
                                # without keyword.
                                is_match_area = True

                            if is_match_area:
                                matched_blocks.append(row)

            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if area_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        el_btn = None
        try:
            #print("target_area text", target_area.text)
            my_css_selector = "input[type=radio]"
            el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
            if el_btn is not None:
                if el_btn.is_enabled():
                    if not el_btn.is_selected():
                        el_btn.click()
                        is_price_assign_by_bot = True
                    else:
                        is_price_assign_by_bot = True
                    #print("bingo, click target_area radio")
        except Exception as exc:
            print("click target_area radio a link fail")
            print(exc)
            pass

    return is_need_refresh, is_price_assign_by_bot

#[TODO]:
# double check selected radio matched by keyword/keyword_and.
def cityline_area_selected_text(driver):
    ret = False

    return ret

def cityline_ticket_number_auto_select(driver, ticket_number):
    selector_string = 'select.select-num'
    by_method = By.CSS_SELECTOR
    return assign_ticket_number_by_select(driver, ticket_number, by_method, selector_string)

def ibon_ticket_number_appear(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    selector_string = 'table.table > tbody > tr > td > select'
    by_method = By.CSS_SELECTOR

    form_select = None
    try:
        form_select = driver.find_element(by_method, selector_string)
    except Exception as exc:
        if show_debug_message:
            print("find ticket_number select fail")
            print(exc)
        pass

    is_visible = False
    if form_select is not None:
        try:
            is_visible = form_select.is_enabled()
        except Exception as exc:
            pass
    return is_visible

def ibon_ticket_number_auto_select(driver, config_dict):
    selector_string = 'table.table > tbody > tr > td > select'
    by_method = By.CSS_SELECTOR
    return assign_ticket_number_by_select(driver, config_dict, by_method, selector_string)

def assign_ticket_number_by_select(driver, config_dict, by_method, selector_string):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ticket_number = str(config_dict["ticket_number"])

    form_select = None
    try:
        form_select = driver.find_element(by_method, selector_string)
    except Exception as exc:
        if show_debug_message:
            print("find ticket_number select fail")
            print(exc)
        pass

    select_obj = None
    if form_select is not None:
        is_visible = False
        try:
            is_visible = form_select.is_enabled()
        except Exception as exc:
            pass
        if is_visible:
            try:
                select_obj = Select(form_select)
            except Exception as exc:
                pass

    is_ticket_number_assigned = False
    if not select_obj is None:
        row_text = None
        try:
            row_text = select_obj.first_selected_option.text
        except Exception as exc:
            pass
        if not row_text is None:
            if len(row_text) > 0:
                if row_text != "0":
                    # ticket assign.
                    is_ticket_number_assigned = True

        if not is_ticket_number_assigned:
            is_ticket_number_assigned = tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number)
        else:
            if show_debug_message:
                print("ticket_number assigned by previous action.")

    return is_ticket_number_assigned

def cityline_purchase_button_press(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ret = False

    date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
    is_date_assign_by_bot = cityline_date_auto_select(driver, date_auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable)

    el_btn = None
    try:
        el_btn = driver.find_element(By.CSS_SELECTOR, 'button.purchase-btn')
    except Exception as exc:
        print("find next button fail")
        #print(exc)
        pass

    if el_btn is not None:
        print("bingo, found next button")
        try:
            if el_btn.is_enabled():
                el_btn.click()
                ret = True
        except Exception as exc:
            print("press next button fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", el_btn)
                ret = True
            except Exception as exc:
                pass

    return ret


def cityline_next_button_press(driver):
    ret = False

    el_nav = None
    el_btn = None
    try:
        el_nav = driver.find_element(By.CSS_SELECTOR, '.puchase-bottom')
        el_btn = driver.find_element(By.CSS_SELECTOR, '#expressPurchaseBtn')
    except Exception as exc:
        print("find next button fail...")
        print(exc)

    if el_btn is not None and el_nav is not None:
        print("bingo, found next button, start to press")
        try:
            if el_btn.is_enabled():
                #el_btn.click()
                builder = ActionChains(driver)
                builder.move_to_element(el_nav)
                builder.click(el_btn)
                builder.perform()
                ret = True
        except Exception as exc:
            print("click next button fail...")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", el_btn)
                ret = True
            except Exception as exc:
                pass

    return ret


def cityline_performance(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

        if show_debug_message:
            print("area_keyword:", area_keyword)

        if len(area_keyword) > 0:
            area_keyword_array = json.loads("["+ area_keyword +"]")
            for area_keyword_item in area_keyword_array:
                is_need_refresh, is_price_assign_by_bot = cityline_area_auto_select(driver, config_dict, area_keyword_item)
                if not is_need_refresh:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.

            # PS: cityline price default value is selected at the first option.
            is_need_refresh, is_price_assign_by_bot = cityline_area_auto_select(driver, config_dict, "")


        # un-tested. disable refresh for now.
        is_need_refresh = False
        if is_need_refresh:
            try:
                driver.refresh()
            except Exception as exc:
                pass

        # choose ticket.
        ticket_number = str(config_dict["ticket_number"])
        is_ticket_number_assigned = cityline_ticket_number_auto_select(driver, ticket_number)

        if show_debug_message:
            print("ticket_number:", ticket_number)
            print("is_ticket_number_assigned:", is_ticket_number_assigned)

        if is_ticket_number_assigned:
            auto_press_next_step_button = True
            if auto_press_next_step_button:
                if not is_price_assign_by_bot:
                    #[TODO]:
                    # double check selected radio matched by keyword/keyword_and.
                    # cityline_area_selected_text(driver)
                    pass

                if is_price_assign_by_bot:
                    for i in range(2):
                        click_ret = cityline_next_button_press(driver)
                        if click_ret:
                            break

def ibon_date_auto_select(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
        print("auto_reload_coming_soon_page_enable:", auto_reload_coming_soon_page_enable)

    ret = False
    matched_blocks = None

    # clean stop word.
    date_keyword = format_keyword_string(date_keyword)
    date_keyword_and = ""

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "div.single-content > div > div.row > div > div.tr"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find date-time rows fail")
        print(exc)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []

            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                # default is enabled.
                row_is_enabled=True
                el_btn = None
                try:
                    my_css_selector = "button"
                    el_btn = row.find_element(By.TAG_NAME, my_css_selector)
                    if el_btn is not None:
                        if not el_btn.is_enabled():
                            #print("row's button disabled!")
                            row_is_enabled=False
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)
        if area_list_count > 0:
            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                if show_debug_message:
                    print("start to match keyword:", date_keyword)
                matched_blocks = []

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if date_keyword in row_text:
                                if len(date_keyword_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and # is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if date_keyword_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        is_button_clicked = False
        for i in range(3):
            el_btn = None
            try:
                my_css_selector = "button.btn"
                el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                pass

            if el_btn is not None:
                try:
                    if el_btn.is_enabled():
                        el_btn.click()
                        print("buy icon pressed.")
                        is_button_clicked = True
                except Exception as exc:
                    pass
                    # use plan B
                    '''
                    try:
                        print("force to click by js.")
                        driver.execute_script("arguments[0].click();", el_btn)
                        ret = True
                    except Exception as exc:
                        pass
                    '''
            if is_button_clicked:
                break
        ret = is_button_clicked

    else:
        # no target to click.
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        driver.refresh()
                        time.sleep(0.4)
                    except Exception as exc:
                        pass
    return ret

def ibon_area_auto_select(driver, config_dict, area_keyword_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    area_auto_select_mode = config_dict["area_auto_select"]["mode"]
    ticket_number = config_dict["ticket_number"]

    # when avaiable seat under this count, check seat text content.
    CONST_DETECT_SEAT_ATTRIBUTE_UNDER_ROW_COUNT = 20

    is_price_assign_by_bot = False
    is_need_refresh = False

    matched_blocks = None

    area_list = None
    try:
        #print("try to find cityline area block")
        #my_css_selector = "div.col-md-5 > table > tbody > tr[onclick=\"onTicketArea(this.id)\"]"
        my_css_selector = "div.col-md-5 > table > tbody > tr:not(.disabled)"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)
            print("area_keyword_list:", area_keyword_list)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True

                row_text = ""
                if row_is_enabled:
                    try:
                        row_text = row.text
                    except Exception as exc:
                        pass

                if row_text is None:
                    row_text = ""

                if '已售完' in row_text:
                    row_is_enabled=False

                if len(row_text) > 0:
                    area_keyword_exclude = config_dict["area_auto_select"]["area_keyword_exclude"]
                    if len(area_keyword_exclude) > 0:
                        area_keyword_exclude_array = json.loads("["+ area_keyword_exclude +"]")
                        for exclude_item in area_keyword_exclude_array:
                            if exclude_item in row_text:
                                row_text = ""

                if len(row_text) > 0:
                    if row_text == "座位已被選擇":
                        row_text=""
                    if row_text == "座位已售出":
                        row_text=""
                    if row_text == "舞台區域":
                        row_text=""

                # check ticket count when amount is few, because of it spent a lot of time at parsing element.
                if len(row_text) > 0:
                    if area_list_count <= CONST_DETECT_SEAT_ATTRIBUTE_UNDER_ROW_COUNT:
                        try:
                            area_seat_el = row.find_element(By.CSS_SELECTOR, 'td.action')
                            if not area_seat_el is None:
                                seat_text = area_seat_el.text
                                if seat_text is None:
                                    seat_text = ""
                                if seat_text.isdigit():
                                    seat_int = int(seat_text)
                                    if seat_int < ticket_number:
                                        # skip this row.
                                        if show_debug_message:
                                            print("skip not enought ticket number area at row_text:", row_text)
                                        row_text = ""
                        except Exception as exc:
                            if show_debug_message:
                                print(exc)
                            pass

                if row_text == "":
                    row_is_enabled=False

                if row_is_enabled:
                    try:
                        button_class_string = str(row.get_attribute('class'))
                        if not button_class_string is None:
                            if len(button_class_string) > 1:
                                if 'disabled' in button_class_string:
                                    row_is_enabled=False
                                if 'sold-out' in button_class_string:
                                    row_is_enabled=False
                    except Exception as exc:
                        pass

                if row_is_enabled:
                    pass
                    # each row to check is too slow.
                    '''
                    row_is_enabled = False
                    try:
                        row_id_string = str(row.get_attribute('id'))
                        if not row_id_string is None:
                            if len(row_id_string) > 1:
                                row_is_enabled = True
                    except Exception as exc:
                        pass
                    '''

                if row_is_enabled:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if is_price_assign_by_bot:
        formated_area_list = None

    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            matched_blocks = []
            if len(area_keyword_list) == 0:
                matched_blocks = formated_area_list
            else:
                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False

                            if len(area_keyword_list) > 0:
                                # must match keyword.
                                is_match_area = True
                                area_keyword_array = area_keyword_list.split(' ')
                                for area_keyword in area_keyword_array:
                                    area_keyword = format_keyword_string(area_keyword)
                                    if not area_keyword in row_text:
                                        is_match_area = False
                                        break
                            else:
                                # without keyword.
                                is_match_area = True

                            if is_match_area:
                                matched_blocks.append(row)

            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if area_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]
        else:
            is_need_refresh = True
            if show_debug_message:
                print("matched_blocks is empty, is_need_refresh")

    if target_area is not None:
        try:
            if target_area.is_enabled():
                target_area.click()
                is_price_assign_by_bot = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                is_price_assign_by_bot = True
            except Exception as exc:
                pass

    return is_need_refresh, is_price_assign_by_bot

def ibon_allow_not_adjacent_seat(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    agree_checkbox = None
    try:
        my_css_selector = 'div.not-consecutive > div.custom-control > span > input[type="checkbox"]'
        agree_checkbox = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find ibon seat checkbox Exception")
        if show_debug_message:
            print(exc)
        pass

    is_finish_checkbox_click = force_check_checkbox(driver, agree_checkbox)

    return is_finish_checkbox_click

def ibon_performance(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

        if show_debug_message:
            print("area_keyword:", area_keyword)

        is_need_refresh = False

        if len(area_keyword) > 0:
            area_keyword_array = json.loads("["+ area_keyword +"]")
            for area_keyword_item in area_keyword_array:
                is_need_refresh, is_price_assign_by_bot = ibon_area_auto_select(driver, config_dict, area_keyword_item)
                if not is_need_refresh:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.
            is_need_refresh, is_price_assign_by_bot = ibon_area_auto_select(driver, config_dict, area_keyword)

        if is_need_refresh:
            try:
                driver.refresh()
            except Exception as exc:
                pass

    return is_price_assign_by_bot

def ibon_purchase_button_press(driver):
    is_button_clicked = force_press_button(driver, By.CSS_SELECTOR, '#ticket-wrap > a.btn')
    return is_button_clicked

def facebook_login(driver, account, password):
    ret = False
    el_email = None
    try:
        el_email = driver.find_element(By.CSS_SELECTOR, '#email')
    except Exception as exc:
        pass

    is_visible = False
    if el_email is not None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if inputed_text is not None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            el_pass = driver.find_element(By.CSS_SELECTOR, '#pass')
        except Exception as exc:
            pass

    is_password_sent = False
    if el_pass is not None:
        try:
            if el_pass.is_enabled():
                inputed_text = el_pass.get_attribute('value')
                if inputed_text is not None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            el_pass.send_keys(password)
                            el_pass.send_keys(Keys.ENTER)
                            is_password_sent = True
                        time.sleep(0.1)
        except Exception as exc:
            pass

    ret = is_password_sent

    return ret

def kktix_login(driver, account, password):
    ret = False
    el_email = None
    try:
        el_email = driver.find_element(By.CSS_SELECTOR, '#user_login')
    except Exception as exc:
        pass

    is_visible = False
    if el_email is not None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if inputed_text is not None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            el_pass = driver.find_element(By.CSS_SELECTOR, '#user_password')
        except Exception as exc:
            pass

    is_password_sent = False
    if el_pass is not None:
        try:
            if el_pass.is_enabled():
                inputed_text = el_pass.get_attribute('value')
                if inputed_text is not None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            el_pass.send_keys(password)
                            el_pass.send_keys(Keys.ENTER)
                            is_password_sent = True
                        time.sleep(0.1)
        except Exception as exc:
            pass

    ret = is_password_sent

    return ret

def cityline_login(driver, account, password):
    ret = False
    el_email = None
    try:
        el_email = driver.find_element(By.CSS_SELECTOR, 'input.ant-input')
    except Exception as exc:
        pass

    is_visible = False
    if el_email is not None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if inputed_text is not None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            el_pass = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        except Exception as exc:
            pass


    is_password_sent = False
    if el_pass is not None:
        try:
            if el_pass.is_enabled():
                inputed_text = el_pass.get_attribute('value')
                if inputed_text is not None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            el_pass.send_keys(password)
                            el_pass.send_keys(Keys.ENTER)
                            is_password_sent = True
                        time.sleep(0.1)
        except Exception as exc:
            pass

    ret = is_password_sent

    return ret

def urbtix_login(driver, account, password):
    ret = False
    el_email = None
    try:
        el_email = driver.find_element(By.CSS_SELECTOR, 'input[name="loginId"]')
    except Exception as exc:
        #print("find #email fail")
        #print(exc)
        pass

    is_visible = False
    if el_email is not None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if inputed_text is not None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            el_pass = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
        except Exception as exc:
            pass

    is_password_sent = False
    if el_pass is not None:
        try:
            if el_pass.is_enabled():
                inputed_text = el_pass.get_attribute('value')
                if inputed_text is not None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            el_pass.send_keys(password)
                            is_password_sent = True
        except Exception as exc:
            pass

    el_btn = None
    if is_password_sent:
        try:
            el_btn = driver.find_element(By.CSS_SELECTOR, '.login-button')
            if not el_btn is None:
                el_btn.click()
        except Exception as exc:
            pass

    return ret

def kham_login(driver, account, password):
    ret = False
    el_email = None
    try:
        my_css_selector = '#ACCOUNT'
        el_email = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass

    is_visible = False
    if el_email is not None:
        try:
            if el_email.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

    is_email_sent = False
    if is_visible:
        try:
            inputed_text = el_email.get_attribute('value')
            if inputed_text is not None:
                if len(inputed_text) == 0:
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            my_css_selector = 'table.login > tbody > tr > td > input[type="password"]'
            el_pass = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

    is_password_sent = False
    if el_pass is not None:
        try:
            if el_pass.is_enabled():
                inputed_text = el_pass.get_attribute('value')
                if inputed_text is not None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            el_pass.send_keys(password)
                            is_password_sent = True
                        time.sleep(0.1)
        except Exception as exc:
            pass

    if is_password_sent:
        is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'div.memberContent > p > a > button.red')

    ret = is_password_sent

    return ret

def hkticketing_login(driver, account, password):
    ret = False
    el_email = None
    try:
        my_css_selector = 'div#myTick2Col > div.formMod2Col > div.formModule > div.loginContentContainer > input.borInput'
        el_email = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        #print("find_element exception")
        #print(exc)
        pass

    is_visible = False
    if el_email is not None:
        try:
            if el_email.is_enabled():
                is_visible = True
            else:
                el_email.click()
        except Exception as exc:
            pass
    else:
        #print("account field is None.")
        pass

    is_email_sent = False
    if is_visible:
        try:
            # PS: this is special case...
            el_email.click()

            inputed_text = el_email.get_attribute('value')
            if inputed_text is not None:
                if len(inputed_text) == 0:
                    #print("send account text:", account)
                    el_email.send_keys(account)
                    is_email_sent = True
                else:
                    if inputed_text == account:
                        is_email_sent = True
        except Exception as exc:
            pass

    el_pass = None
    if is_email_sent:
        try:
            my_css_selector = 'div.loginContentContainer > input[type="password"]'
            el_pass = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

    is_password_sent = False
    if el_pass is not None:
        try:
            if el_pass.is_enabled():
                el_pass.click()
                inputed_text = el_pass.get_attribute('value')
                if inputed_text is not None:
                    if len(inputed_text) == 0:
                        el_pass.click()
                        if(len(password)>0):
                            #print("send password text:", password)
                            el_pass.send_keys(password)
                            el_pass.send_keys(Keys.ENTER)
                            is_password_sent = True
                        time.sleep(0.1)
            else:
                el_pass.click()
        except Exception as exc:
            pass

    ret = is_password_sent

    return ret

def check_and_play_sound_for_captcha(config_dict):
    if config_dict["advanced"]["play_captcha_sound"]["enable"]:
        app_root = get_app_root()
        captcha_sound_filename = os.path.join(app_root, config_dict["advanced"]["play_captcha_sound"]["filename"].strip())
        play_mp3_async(captcha_sound_filename)

def play_mp3_async(sound_filename):
    import threading
    threading.Thread(target=play_mp3, args=(sound_filename,), daemon=True).start()

def play_mp3(sound_filename):
    from playsound import playsound
    try:
        playsound(sound_filename)
    except Exception as exc:
        msg=str(exc)
        print("play sound exeption:", msg)
        if platform.system() == 'Windows':
            import winsound
            try:
                winsound.PlaySound(sound_filename, winsound.SND_FILENAME)
            except Exception as exc2:
                pass

# purpose: check alert poped.
# PS: current version not enable...
def check_pop_alert(driver):
    is_alert_popup = False

    # https://stackoverflow.com/questions/57481723/is-there-a-change-in-the-handling-of-unhandled-alert-in-chromedriver-and-chrome
    default_close_alert_text = [""]
    if len(default_close_alert_text) > 0:
        try:
            alert = None
            if not driver is None:
                #alert = driver.switch_to.alert
                alert = WebDriverWait(driver, 0.2).until(EC.alert_is_present())
            if not alert is None:
                alert_text = str(alert.text)
                if not alert_text is None:
                    is_match_auto_close_text = False
                    for txt in default_close_alert_text:
                        if len(txt) > 0:
                            if txt in alert.text:
                                is_match_auto_close_text = True
                        else:
                            is_match_auto_close_text = True
                    #print("is_match_auto_close_text:", is_match_auto_close_text)
                    #print("alert3 text:", alert.text)

                    if is_match_auto_close_text:
                        alert.accept()
                        print("alert3 accepted")

                    is_alert_popup = True
            else:
                print("alert3 not detected")
        except NoAlertPresentException as exc1:
            #logger.error('NoAlertPresentException for alert')
            pass
        except NoSuchWindowException:
            pass
        except Exception as exc:
            #logger.error('Exception2 for alert')
            #logger.error(exc, exc_info=True)
            pass

    return is_alert_popup

def list_all_cookies(driver):
    cookies_dict = {}
    if not driver is None:
        all_cookies=driver.get_cookies();
        for cookie in all_cookies:
            cookies_dict[cookie['name']] = cookie['value']
    print(cookies_dict)

def set_non_browser_cookies(driver, url, Captcha_Browser):
    if not driver is None:
        domain_name = url.split('/')[2]
        #PS: need set cookies once, if user change domain.
        if not Captcha_Browser is None:
            Captcha_Browser.Set_cookies(driver.get_cookies())
            Captcha_Browser.Set_Domain(domain_name)

def ticketmaster_assign_ticket_number(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    table_select = None
    try:
        my_css_selector = 'table#ticketPriceList'
        table_select = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        if show_debug_message:
            print('fail to find my_css_selector:', my_css_selector)
            #print("find table#ticketPriceList fail", exc)
        pass

    form_select = None
    if not table_select is None:
        if show_debug_message:
            print('found table, start find select')

        try:
            my_css_selector = 'select'
            form_select = table_select.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            if show_debug_message:
                print('my_css_selector:', my_css_selector)
                print("find form-select fail", exc)
            pass

    select_obj = None
    if form_select is not None:
        if show_debug_message:
            print('found select.')

        is_visible = False
        try:
            if form_select.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        if is_visible:
            try:
                select_obj = Select(form_select)
            except Exception as exc:
                pass

    is_ticket_number_assigned = False
    if not select_obj is None:
        row_text = None
        try:
            row_text = select_obj.first_selected_option.text
        except Exception as exc:
            pass
        if not row_text is None:
            if show_debug_message:
                print('row_text:', row_text)

            if len(row_text) > 0:
                if row_text != "0":
                    if row_text.isnumeric():
                        # ticket assign.
                        is_ticket_number_assigned = True

    if show_debug_message:
        print('is_ticket_number_assigned:', is_ticket_number_assigned)


    # must wait select object ready to assign ticket number.
    if not is_ticket_number_assigned:
        ticket_number = str(config_dict["ticket_number"])
        is_ticket_number_assigned = tixcraft_ticket_number_auto_fill(driver, select_obj, ticket_number)

        # must wait ticket number assign to focus captcha.
        if is_ticket_number_assigned:
            is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'#autoMode')

def ticketmaster_captcha(driver, config_dict, ocr, Captcha_Browser, domain_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False
    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]

    if config_dict["auto_check_agree"]:
        for i in range(3):
            is_finish_checkbox_click = tixcraft_ticket_agree(driver, config_dict)
            if is_finish_checkbox_click:
                break

    if not config_dict["ocr_captcha"]["enable"]:
        tixcraft_keyin_captcha_code(driver)
    else:
        previous_answer = None
        for redo_ocr in range(999):
            is_need_redo_ocr, previous_answer, is_form_sumbited = tixcraft_auto_ocr(driver, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, domain_name)
            if is_form_sumbited:
                # start next loop.
                break

            if not away_from_keyboard_enable:
                break

            if not is_need_redo_ocr:
                break


def tixcraft_main(driver, url, config_dict, tixcraft_dict, ocr, Captcha_Browser):
    tixcraft_home_close_window(driver)
    
    home_url_list = ['https://tixcraft.com/'
    ,'https://www.tixcraft.com/'
    ,'https://indievox.com/'
    ,'https://www.indievox.com/'
    ,'https://teamear.tixcraft.com/activity'
    ,'https://www.ticketmaster.sg/'
    ,'https://www.ticketmaster.com/'
    ]
    for each_url in home_url_list:
        if each_url == url:
            if config_dict["ocr_captcha"]["enable"]:
                set_non_browser_cookies(driver, url, Captcha_Browser)
            break

    if "/activity/detail/" in url:
        is_redirected = tixcraft_redirect(driver, url)

    is_date_selected = False
    if "/activity/game/" in url:
        date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
        if date_auto_select_enable:
            domain_name = url.split('/')[2]
            is_date_selected = tixcraft_date_auto_select(driver, url, config_dict, domain_name)

    if '/artist/' in url and 'ticketmaster.com' in url:
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True
        if is_event_page:
            date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
            if date_auto_select_enable:
                domain_name = url.split('/')[2]
                is_date_selected = ticketmaster_date_auto_select(driver, url, config_dict, domain_name)

    # choose area
    if '/ticket/area/' in url:
        domain_name = url.split('/')[2]
        if not 'ticketmaster' in domain_name:
            if config_dict["area_auto_select"]["enable"]:
                tixcraft_area_auto_select(driver, url, config_dict)
        else:
            # area auto select is too difficult, skip in this version.
            ticketmaster_assign_ticket_number(driver, config_dict)

    # https://ticketmaster.sg/ticket/check-captcha/23_blackpink/954/5/75
    if '/ticket/check-captcha/' in url:
        domain_name = url.split('/')[2]
        ticketmaster_captcha(driver, config_dict, ocr, Captcha_Browser, domain_name)


    if '/ticket/verify/' in url:
        tixcraft_dict["answer_index"] = tixcraft_verify(driver, config_dict, tixcraft_dict["answer_index"])
    else:
        tixcraft_dict["answer_index"] = -1

    # main app, to select ticket number.
    if '/ticket/ticket/' in url:
        domain_name = url.split('/')[2]
        tixcraft_ticket_main(driver, config_dict, ocr, Captcha_Browser, domain_name)

    if '/ticket/checkout' in url:
        if config_dict["advanced"]["headless"]:
            if not tixcraft_dict["is_popup_checkout"]:
                domain_name = url.split('/')[2]
                checkout_url = "https://%s/ticket/checkout" % (domain_name)
                print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
                webbrowser.open_new(checkout_url)
                tixcraft_dict["is_popup_checkout"] = True
    else:
        tixcraft_dict["is_popup_checkout"] = False

    return tixcraft_dict

def kktix_main(driver, url, config_dict, kktix_dict):
    auto_press_next_step_button = config_dict["kktix"]["auto_press_next_step_button"]
    kktix_account = config_dict["advanced"]["kktix_account"]

    is_url_contain_sign_in = False
    # fix https://kktix.com/users/sign_in?back_to=https://kktix.com/events/xxxx and registerStatus: SOLD_OUT cause page refresh.
    if '/users/sign_in?' in url:
        if len(kktix_account) > 4:
            kktix_login(driver, kktix_account, decryptMe(config_dict["advanced"]["kktix_password"]))
        is_url_contain_sign_in = True

    if not is_url_contain_sign_in:
        if '/registrations/new' in url:
            kktix_dict["answer_index"], kktix_dict["kktix_register_status_last"] = kktix_reg_new(driver, url, kktix_dict["answer_index"], kktix_dict["kktix_register_status_last"], config_dict)
        else:
            is_event_page = False
            if '/events/' in url:
                # ex: https://xxx.kktix.cc/events/xxx-copy-1
                if len(url.split('/'))<=5:
                    is_event_page = True

            if is_event_page:
                if auto_press_next_step_button:
                    # pass switch check.
                    #print("should press next here.")
                    kktix_events_press_next_button(driver)

            kktix_dict["answer_index"] = -1
            kktix_dict["kktix_register_status_last"] = None

    if '/events/' in url and '/registrations/' in url and "-" in url:
        if config_dict["advanced"]["headless"]:
            if not kktix_dict["is_popup_checkout"]:
                is_event_page = False
                if len(url.split('/'))==8:
                    is_event_page = True
                if is_event_page:
                    confirm_clicked = kktix_confirm_order_button(driver)
                    if confirm_clicked:
                        domain_name = url.split('/')[2]
                        checkout_url = "https://%s/account/orders" % (domain_name)
                        print("搶票成功, 請前往該帳號訂單查看: %s" % (checkout_url))
                        webbrowser.open_new(checkout_url)
                        tixcraft_dict["is_popup_checkout"] = True
    else:
        kktix_dict["is_popup_checkout"] = False

    return kktix_dict

def famiticket_main(driver, url, config_dict):
    try:
        window_handles_count = len(driver.window_handles)
        if window_handles_count > 1:
            driver.switch_to.window(driver.window_handles[0])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
    except Exception as excSwithFail:
        pass

    if '/Home/Activity/Info/' in url:
        fami_activity(driver)
    if '/Sales/Home/Index/' in url:
        fami_home(driver, url, config_dict)

def urbtix_performance_confirm_dialog_popup(driver):
    ret = False

    el_div = None
    try:
        el_div = driver.find_element(By.CSS_SELECTOR, 'div.notification-confirm-btn > div.button-text')
    except Exception as exc:
        #print("find modal-dialog fail")
        #print(exc)
        pass

    if el_div is not None:
        print("bingo, found notification-confirm-btn")
        is_visible = False
        try:
            if el_div.is_enabled():
                if el_div.is_displayed():
                    is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            try:
                el_div.click()
                ret = True
            except Exception as exc:
                # use plan B
                '''
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_div)
                    ret = True
                except Exception as exc:
                    pass
                '''
                pass

        if ret:
            time.sleep(0.4)

    return ret

def get_urbtix_survey_answer_by_question(question_text):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    question_text = question_text.replace('  ',' ')
    question_text = full2half(question_text)

    seq = 0
    if '第' in question_text and '個' in question_text:
        temp_string = question_text.split('第')[1]
        seq_string  = temp_string.split('個')[0]
        if len(seq_string) > 0:
            if seq_string.isdigit():
                seq = int(seq_string)
            else:
                tmp_seq = normalize_chinese_numeric(seq_string)
                if not tmp_seq is None:
                    seq = tmp_seq

    if show_debug_message:
        print("seq:", seq)

    direction = "left"
    if '右起' in question_text:
        direction = "right"
    if '由右' in question_text:
        direction = "right"
    if '從右' in question_text:
        direction = "right"
    if '自右' in question_text:
        direction = "right"
    if '右算' in question_text:
        direction = "right"
    if '右邊' in question_text:
        direction = "right"
    if ' from the RIGHT' in question_text:
        direction = "right"

    if '有多少個' in question_text:
        direction = "count"
    if '有幾個' in question_text:
        direction = "count"
    if 'How many ' in question_text:
        direction = "count"

    if show_debug_message:
        print("direction:", direction)

    question_text_formated = question_text
    question_text_formated = question_text_formated.replace('「','')
    question_text_formated = question_text_formated.replace('」','')
    question_text_formated = question_text_formated.replace(' ','')
    question_text_formated = question_text_formated.replace('-','')
    question_text_formated = question_text_formated.replace('_','')

    # format question.
    question_text_formated = question_text_formated.replace(';','')
    question_text_formated = question_text_formated.replace('.','')
    question_text_formated = question_text_formated.replace(':','')
    question_text_formated = question_text_formated.replace(',','')

    question_answer_char = ""
    option_text_string = find_continuous_text(question_text_formated)
    

    if show_debug_message:
        print("option_text_string:", option_text_string)

    if direction in ['left','right']:
        if seq > 0:
            if len(option_text_string) > 1:
                if seq <= len(option_text_string):
                    if direction == "left":
                        question_answer_char = option_text_string[seq-1:seq]
                    if direction == "right":
                        question_answer_char = option_text_string[len(option_text_string)-seq:len(option_text_string)-seq+1]

    if direction == "count":
        if '個' in question_text_formated:
            count_target = None
            count_answer = 0

            tmp_seq = question_text_formated.split('個')[1]
            if len(tmp_seq) > 0:
                count_target_string = tmp_seq[:1]
                if len(count_target_string) > 0:
                    if count_target_string.isdigit():
                        count_target = int(count_target_string)
                    else:
                        count_target = normalize_chinese_numeric(count_target_string)

            if not count_target is None:
                for char in option_text_string:
                    if char == str(count_target):
                        count_answer += 1

            question_answer_char = str(count_answer)
            if show_debug_message:
                print("count_target:", count_target)
                print("count_answer:", count_answer)

    if show_debug_message:
        print("question_answer_char text:", question_answer_char)

    return question_answer_char, direction

# PS: due to open-ended question, disable this feature now.
def urbtix_auto_survey(driver, config_dict):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    questions_div = None
    try:
        questions_div = driver.find_elements(By.CSS_SELECTOR, 'div.modal-content > div.content > div.questions > div.question-item')
    except Exception as exc:
        #print("find modal-dialog fail")
        #print(exc)
        pass

    is_radio_clicked = False
    fill_question_count = 0

    if questions_div is not None:
        quetions_count = len(questions_div)
        if show_debug_message:
            print("quetions_count:", quetions_count)

        try:
            for each_question_div in questions_div:
                each_question_ask_div = each_question_div.find_element(By.CSS_SELECTOR, 'div.titles > div')
                if not each_question_ask_div is None:
                    question_text = each_question_ask_div.text
                    if question_text is None:
                        question_text = ""
                    if show_debug_message:
                        print("questions_div text:", question_text)

                    question_answer_char, question_direction = get_urbtix_survey_answer_by_question(question_text)
                    each_option_items_div = each_question_div.find_elements(By.CSS_SELECTOR, 'div.options > div.option-item')
                    if not each_option_items_div is None:
                        question_answered = False
                        for each_option_div in each_option_items_div:
                            option_content_div = each_option_div.find_element(By.CSS_SELECTOR, 'div.content-list')
                            if not option_content_div is None:
                                option_content_div_text = option_content_div.text
                                if option_content_div is None:
                                    option_content_div=""
                                option_content_div_text = option_content_div_text.strip()
                                option_content_div_text = full2half(option_content_div_text)

                                if question_direction in ['left','right']:
                                    for answer_item in synonyms(question_answer_char):
                                        if answer_item in option_content_div_text:
                                            is_radio_clicked = force_press_button(each_option_div, By.CSS_SELECTOR, 'div.radio-wrapper')
                                            if is_radio_clicked:
                                                if show_debug_message:
                                                    print("fill answer:", answer_item)
                                                question_answered = True
                                                break

                                if question_direction == "count":
                                    for answer_item in synonyms(question_answer_char):
                                        if answer_item in option_content_div_text:
                                            is_radio_clicked = force_press_button(each_option_div, By.CSS_SELECTOR, 'div.radio-wrapper')
                                            if is_radio_clicked:
                                                if show_debug_message:
                                                    print("fill answer:", answer_item)
                                                question_answered = True
                                                break

                                    if question_answer_char == '0':
                                        is_match_none = False
                                        if '沒有' in option_content_div_text:
                                            is_match_none = True
                                        if 'LESS THEN ONE' in option_content_div_text.upper():
                                            is_match_none = True
                                        if is_match_none:
                                            is_radio_clicked = force_press_button(each_option_div, By.CSS_SELECTOR, 'div.radio-wrapper')
                                            if is_radio_clicked:
                                                if show_debug_message:
                                                    print("fill answer:", '沒有')
                                                question_answered = True
                                                break

                                    int_answer_char = int(question_answer_char)
                                    if int_answer_char > 1:
                                        for i in range(int_answer_char-1):
                                            for answer_item in synonyms(str(i+1)):
                                                is_match_more_then = False
                                                if answer_item + '個或以上' in option_content_div_text:
                                                    is_match_more_then = True
                                                if answer_item + '個以上' in option_content_div_text:
                                                    is_match_more_then = True
                                                if '多於' in option_content_div_text and answer_item + '個' in option_content_div_text:
                                                    is_match_more_then = True
                                                if '更多' in option_content_div_text and answer_item + '個' in option_content_div_text:
                                                    is_match_more_then = True
                                                if 'MORE THEN' in option_content_div_text.upper() and answer_item + '個' in option_content_div_text:
                                                    is_match_more_then = True
                                                if is_match_more_then:
                                                    is_radio_clicked = force_press_button(each_option_div, By.CSS_SELECTOR, 'div.radio-wrapper')
                                                    if is_radio_clicked:
                                                        if show_debug_message:
                                                            print("fill answer:", answer_item + '個或以上')
                                                        question_answered = True
                                                        break
                                            if question_answered:
                                                break

                                if question_answered:
                                    fill_question_count += 1
                                    break

        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

        if show_debug_message:
            print("fill_question_count:", fill_question_count)

    #if is_radio_clicked and fill_question_count>=3:
    if is_radio_clicked and fill_question_count>=2:
        questions_remain_div = None
        questions_remain_text = ""
        try:
            questions_remain_div = driver.find_element(By.CSS_SELECTOR, 'div.surplus-questions-number')
            if not questions_remain_div is None:
                questions_remain_text = questions_remain_div.text
                questions_remain_text = questions_remain_text.strip()
        except Exception as exc:
            if show_debug_message:
                print(exc)
            pass

        if show_debug_message:
            #print("questions_remain_text:", questions_remain_text)
            pass
        
        if questions_remain_text == "0" or questions_remain_text == "":
            is_button_clicked = False
            #is_button_clicked = force_press_button(driver, By.CSS_SELECTOR, 'div.button-wrapper > div.button-text-multi-lines > div')

            # Message: Element <div class="text-tc"> is not clickable at point (351,566) because another element <div class="modal-wrapper landing-question"> obscures it
            btn_submit = None
            try:
                my_css_selector = 'div.landing-question > div.modal-inner > div.modal-content > div.content > div.button-container > div.button-and-number > div.button-wrapper > div.button-text-multi-lines > div.text-tc'
                btn_submit = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                if not btn_submit.is_enabled():
                    btn_submit = None
            except Exception as exc:
                if show_debug_message:
                    print(exc)
                pass

            if not btn_submit is None:
                try:
                    if show_debug_message:
                        print("start to click btn.")
                    btn_submit.click()
                    is_button_clicked = True
                    time.sleep(1.0)
                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass


def urbtix_main(driver, url, config_dict):
    # http://msg.urbtix.hk
    waiting_for_access_url = ['/session/landing-timer/','msg.urbtix.hk','busy.urbtix.hk']
    for waiting_url in waiting_for_access_url:
        if waiting_url in url:
            try:
                driver.get('https://www.urbtix.hk/')
            except Exception as exec1:
                pass
            pass
            # 刷太快, 會被封IP?
            time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    if '/logout?' in url:
        try:
            driver.get('https://www.urbtix.hk/')
        except Exception as exec1:
            pass
        pass

    # for new survey.
    if 'https://www.urbtix.hk/session/landing' == url:
        if config_dict["advanced"]["auto_guess_options"]:
            #urbtix_auto_survey(driver, config_dict)
            pass

    if '.hk/member-login' in url:
        urbtix_account = config_dict["advanced"]["urbtix_account"]
        if len(urbtix_account) > 2:
            urbtix_login(driver, urbtix_account, decryptMe(config_dict["advanced"]["urbtix_password"]))

    is_ready_to_buy_from_queue = False
    # Q: How to know ready to buy ticket from queue?
    if is_ready_to_buy_from_queue:
        # play sound when ready to buy ticket.
        check_and_play_sound_for_captcha(config_dict)

    # https://www.urbtix.hk/event-detail/00000/
    if '/event-detail/' in url:
        if config_dict["tixcraft"]["date_auto_select"]["enable"]:
            is_event_page = False
            if len(url.split('/'))<=6:
                is_event_page = True
            urbtix_purchase_ticket(driver, config_dict)

    # https://www.urbtix.hk/performance-detail/?eventId=00000&performanceId=00000
    is_performace_page = False
    if '/performance-detail/?eventId=' in url:
        is_performace_page = True

    if 'performance-detail?eventId' in url:
        is_performace_page = True

    if is_performace_page:
        if config_dict["area_auto_select"]["enable"]:
            is_confirm_dialog_popup = urbtix_performance_confirm_dialog_popup(driver)
            if is_confirm_dialog_popup:
                print("is_confirm_dialog_popup! auto press confirm...")
            else:
                urbtix_performance(driver, config_dict)

def check_modal_dialog_popup(driver):
    ret = False

    el_div = None
    try:
        el_div = driver.find_element(By.CSS_SELECTOR, 'div.modal-dialog > div.modal-content')
    except Exception as exc:
        #print("find modal-dialog fail")
        #print(exc)
        pass

    if el_div is not None:
        #print("bingo, found modal-dialog")
        try:
            if el_div.is_enabled():
                if el_div.is_displayed():
                    ret = True
        except Exception as exc:
            pass

    return ret


def cityline_shows_goto_cta(driver):
    ret = False

    el_btn = None
    try:
        el_btn = driver.find_element(By.CSS_SELECTOR, '.btn_cta')
    except Exception as exc:
        #print("find next button fail...")
        #print(exc)
        pass

    if el_btn is not None:
        #print("bingo, found next button, start to press")
        try:
            if el_btn.is_enabled() and el_btn.is_displayed():
                el_btn.click()
                ret = True
        except Exception as exc:
            print("click next button fail...")
            print(exc)

    return ret

def cityline_home_close_window(driver):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    close_styles_list = ['.anticon-close', '.cookieWrapper_closeBtn']

    for close_styles in close_styles_list:
        is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,  close_styles)

def cityline_main(driver, url, config_dict):
    #https://www.cityline.com/Events.html
    if 'cityline.com/Events.html' in url:
        cityline_home_close_window(driver)

    # https://www.cityline.com/Login.html?targetUrl=https%3A%2F%2F
    # ignore url redirect
    if '/Login.html' in url:
        cityline_account = config_dict["advanced"]["cityline_account"]
        if len(cityline_account) > 2:
            cityline_login(driver, cityline_account, decryptMe(config_dict["advanced"]["cityline_password"]))
        return

    # https://msg.cityline.com/ https://event.cityline.com/
    if 'msg.cityline.com' in url or 'event.cityline.com' in url:
        try:
            driver.execute_script("goEvent();")
        except Exception as exec1:
            pass
        pass
        # 刷太快, 會被封IP?
        time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    try:
        window_handles_count = len(driver.window_handles)
        if window_handles_count > 1:
            driver.switch_to.window(driver.window_handles[0])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(0.2)
    except Exception as excSwithFail:
        pass

    is_ready_to_buy_from_queue = False
    # Q: How to know ready to buy ticket from queue?
    if is_ready_to_buy_from_queue:
        # play sound when ready to buy ticket.
        check_and_play_sound_for_captcha(config_dict)

    if '/eventDetail?' in url:
        is_modal_dialog_popup = check_modal_dialog_popup(driver)
        if is_modal_dialog_popup:
            print("is_modal_dialog_popup! skip...")
        else:
            if config_dict["tixcraft"]["date_auto_select"]["enable"]:
                cityline_purchase_button_press(driver, config_dict)

    if '/performance?' in url:
        is_modal_dialog_popup = check_modal_dialog_popup(driver)
        if is_modal_dialog_popup:
            print("is_modal_dialog_popup! skip...")
        else:
            if config_dict["area_auto_select"]["enable"]:
                cityline_performance(driver, config_dict)

    if '.htm' in url:
        if not '/slim_end.htm' in url:
            if len(url.split('/'))>=5:
                cityline_shows_goto_cta(driver)

def guess_ibon_question(driver):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    inferred_answer_string = None
    answer_list = []

    form_select = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, 'div.editor-box > div > div.form-group > label')
    except Exception as exc:
        print("find verify textbox fail")
        pass

    question_text = None
    if form_select is not None:
        try:
            question_text = form_select.text
        except Exception as exc:
            print("get text fail")

    is_options_in_question = False

    if inferred_answer_string is None:
        if not question_text is None:
            inferred_answer_string, answer_list = get_answer_list_from_question_string(None, question_text)

    return inferred_answer_string, answer_list

def ibon_verification_question(driver, answer_index, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    presale_code = config_dict["tixcraft"]["presale_code"]
    presale_code_delimiter = config_dict["tixcraft"]["presale_code_delimiter"]

    inferred_answer_string = None
    answer_list = []

    is_retry_user_single_answer = False

    if len(presale_code) > 0:
        if len(presale_code_delimiter) > 0:
            if presale_code_delimiter in presale_code:
                answer_list = presale_code.split(presale_code_delimiter)
                if len(answer_list) > 0:
                    if answer_index < len(answer_list)-1:
                        inferred_answer_string = answer_list[answer_index+1]
        else:
            is_retry_user_single_answer = True
            if answer_index < 2:
                inferred_answer_string = presale_code

    if inferred_answer_string is None:
        inferred_answer_string, answer_list = guess_ibon_question(driver)
        if inferred_answer_string is None:
            if not answer_list is None:
                if len(answer_list) > 0:
                    if answer_index < len(answer_list)-1:
                        inferred_answer_string = answer_list[answer_index+1]

    if show_debug_message:
        print("answer_index:", answer_index)
        print("inferred_answer_string:", inferred_answer_string)
        print("answer_index:", answer_index)
        print("is_retry_user_single_answer:", is_retry_user_single_answer)

    form_input = None
    try:
        form_input = driver.find_element(By.CSS_SELECTOR, 'div.editor-box > div > div.form-group > input')
    except Exception as exc:
        print("find verify code fail")
        pass

    inputed_value = None
    if form_input is not None:
        try:
            inputed_value = form_input.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass

    if inputed_value is None:
        inputed_value = ""

    if not inferred_answer_string is None:
        is_password_sent = False
        if len(inputed_value)==0:
            try:
                # PS: sometime may send key twice...
                form_input.clear()
                form_input.send_keys(inferred_answer_string)
                is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'div.editor-box > div > div.form-group > a.btn')
                if is_button_clicked:
                    is_password_sent = True

                # guess answer mode.
                answer_index += 1

                if show_debug_message:
                    print("sent password by bot:", inferred_answer_string)
            except Exception as exc:
                pass
        else:
            if inputed_value == inferred_answer_string:
                if show_debug_message:
                    print("sent password by previous time.")
                is_password_sent = True
                try:
                    form_input.send_keys(Keys.ENTER)
                except Exception as exc:
                    pass

            if is_retry_user_single_answer:
                # increase counter for waiting for stop retry.
                answer_index += 1
            else:
                # guess answer mode.
                if answer_index > -1:
                    # here not is first option.
                    inferred_answer_previous = None
                    if answer_index < len(answer_list)-1:
                        inferred_answer_previous = answer_list[answer_index]
                    if inputed_value == inferred_answer_previous:
                        try:
                            form_input.clear()
                            form_input.send_keys(inferred_answer_string)
                            is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'div.editor-box > div > div.form-group > a.btn')
                            is_password_sent = True
                            if show_debug_message:
                                print("sent password by bot:", inferred_answer_string, "at index:", answer_index+2)

                            answer_index += 1
                        except Exception as exc:
                            pass

        if is_password_sent:
            for i in range(3):
                time.sleep(0.1)

                alert_ret = check_pop_alert(driver)
                if alert_ret:
                    if show_debug_message:
                        print("press accept button at time #", i+1)
                    break
    else:
        if len(inputed_value)==0:
            try:
                form_input.click()
            except Exception as exc:
                pass

    return answer_index


def ibon_ticket_agree(driver):
    # check agree
    form_checkbox = None
    try:
        form_checkbox = driver.find_element(By.ID, 'agreen')
    except Exception as exc:
        #print("find #agreen fail")
        pass

    is_finish_checkbox_click = False
    if form_checkbox is not None:
        try:
            if form_checkbox.is_enabled():
                if not form_checkbox.is_selected():
                    form_checkbox.click()
                    is_finish_checkbox_click = True
        except Exception as exc:
            print("click #agreen fail, try plan_b click label.")
            is_finish_checkbox_click = force_press_button(driver, By.CSS_SELECTOR,'label[for="agreen"]')

    return is_finish_checkbox_click

def ibon_check_sold_out(driver):
    is_sold_out = False

    div_ticket_info = None
    try:
        div_ticket_info = driver.find_element(By.CSS_SELECTOR, '#ticket-info')
    except Exception as exc:
        print("find #ticket-info fail")

    if div_ticket_info is not None:
        try:
            div_ticket_info_text = div_ticket_info.text
            if not div_ticket_info_text is None:
                if '已售完' in div_ticket_info_text:
                    is_sold_out = True
        except Exception as exc:
            pass

    return is_sold_out

def ibon_auto_signup(driver):
    is_button_clicked = force_press_button(driver, By.CSS_SELECTOR, '.btn.btn-signup')
    return is_button_clicked

def ibon_keyin_captcha_code(driver, answer = "", auto_submit = False):
    is_verifyCode_editing = False

    form_verifyCode = None
    try:
        my_css_selector = 'input[value="驗證碼"]'
        form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find blockLogin input fail")
        try:
            my_css_selector = 'input[placeholder="驗證碼"]'
            form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

    if form_verifyCode is not None:
        inputed_value = None
        try:
            inputed_value = form_verifyCode.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass

        if inputed_value is None:
            inputed_value = ""

        if inputed_value == "驗證碼":
            try:
                form_verifyCode.clear()
            except Exception as exc:
                print("clear verify code fail")
                pass
        else:
            if len(inputed_value) > 0:
                print("captcha text inputed.")
                form_verifyCode = None
                is_verifyCode_editing = True

    if form_verifyCode is not None:
        if len(answer) > 0:
            answer=answer.upper()
            is_visible = False
            try:
                if form_verifyCode.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    form_verifyCode.click()
                    is_verifyCode_editing = True
                except Exception as exc:
                    pass

                #print("start to fill answer.")
                try:
                    form_verifyCode.clear()
                    form_verifyCode.send_keys(answer)
                except Exception as exc:
                    print("send_keys ocr answer fail.")

    return is_verifyCode_editing

def ibon_auto_ocr(driver, config_dict, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, model_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    print("start to ddddocr")

    is_need_redo_ocr = False
    is_form_sumbited = False

    ocr_answer = None
    if not ocr is None:
        if show_debug_message:
            print("away_from_keyboard_enable:", away_from_keyboard_enable)
            print("previous_answer:", previous_answer)
            print("ocr_captcha_image_source:", ocr_captcha_image_source)

        ocr_start_time = time.time()

        img_base64 = None
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.Request_Captcha())
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'chk_pic'
            try:
                form_verifyCode_base64 = driver.execute_async_script("""
                    var canvas = document.createElement('canvas');
                    var context = canvas.getContext('2d');
                    var img = document.getElementById('%s');
                    if(img!=null) {
                    canvas.height = img.naturalHeight;
                    canvas.width = img.naturalWidth;
                    context.drawImage(img, 0, 0);
                    callback = arguments[arguments.length - 1];
                    callback(canvas.toDataURL()); }
                    """ % (image_id))
                if not form_verifyCode_base64 is None:
                    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
            except Exception as exc:
                if show_debug_message:
                    print("canvas exception:", str(exc))
                pass
        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                pass

        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        print("ocr elapsed time:", "{:.3f}".format(ocr_elapsed_time))
    else:
        print("ddddocr is None")

    if not ocr_answer is None:
        ocr_answer = ocr_answer.strip()
        print("ocr_answer:", ocr_answer)
        if len(ocr_answer)==4:
            who_care_var = ibon_keyin_captcha_code(driver, answer = ocr_answer, auto_submit = away_from_keyboard_enable)
        else:
            if not away_from_keyboard_enable:
                ibon_keyin_captcha_code(driver)
            else:
                is_need_redo_ocr = True
                if previous_answer != ocr_answer:
                    previous_answer = ocr_answer
                    print("click captcha again")
                    if True:
                        # selenium solution.
                        jquery_string = '$("#chk_pic").attr("src", "/pic.aspx?TYPE=%s&ts=" + new Date().getTime());' % (model_name)
                        driver.execute_script(jquery_string)

                        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
                            time.sleep(0.3)
                    else:
                        # Non_Browser solution.
                        if not Captcha_Browser is None:
                            new_captcha_url = Captcha_Browser.Request_Refresh_Captcha() #取得新的CAPTCHA
                            if new_captcha_url != "":
                                #PS:[TODO]
                                #tixcraft_change_captcha(driver, new_captcha_url) #更改CAPTCHA圖
                                pass
    else:
        print("ocr_answer is None")
        print("previous_answer:", previous_answer)
        if previous_answer is None:
            ibon_keyin_captcha_code(driver)
        else:
            # page is not ready, retry again.
            # PS: usually occur in async script get captcha image.
            is_need_redo_ocr = True

    return is_need_redo_ocr, previous_answer, is_form_sumbited

def ibon_captcha(driver, config_dict, ocr, Captcha_Browser, model_name):
    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False
    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]

    #PS: need a 'auto assign seat' feature to enable away_from_keyboard feature.
    away_from_keyboard_enable = False

    is_cpatcha_sent = False
    previous_answer = None
    for redo_ocr in range(999):
        is_need_redo_ocr, previous_answer, is_form_sumbited = ibon_auto_ocr(driver, config_dict, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, model_name)

        # TODO: must ensure the answer is corrent...
        if not is_need_redo_ocr:
            is_cpatcha_sent = True

        if is_form_sumbited:
            break

        if not away_from_keyboard_enable:
            break

        if not is_need_redo_ocr:
            break

    return is_cpatcha_sent

def ibon_main(driver, url, config_dict, ibon_dict, ocr, Captcha_Browser):
    home_url_list = ['https://ticket.ibon.com.tw/'
    ,'https://ticket.ibon.com.tw/Index/entertainment'
    ]
    for each_url in home_url_list:
        if each_url == url:
            if config_dict["ocr_captcha"]["enable"]:
                set_non_browser_cookies(driver, url, Captcha_Browser)
            break

    # https://tour.ibon.com.tw/event/e23010000300mxu
    if 'tour' in url and '/event/' in url:
        is_event_page = False
        if len(url.split('/'))==5:
            is_event_page = True

        if is_event_page:
            ibon_auto_signup(driver)

    is_match_target_feature = False

    if not is_match_target_feature:
        #https://ticket.ibon.com.tw/ActivityInfo/Details/0000?pattern=entertainment
        if '/ActivityInfo/Details/' in url:
            is_event_page = False
            if len(url.split('/'))==6:
                is_event_page = True

            if is_event_page:
                if config_dict["tixcraft"]["date_auto_select"]["enable"]:
                    is_match_target_feature = True
                    is_date_assign_by_bot = ibon_date_auto_select(driver, config_dict)

    if not is_match_target_feature:
        # validation question url:
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_0.aspx?rn=1180872370&PERFORMANCE_ID=B04M7XZT&PRODUCT_ID=B04KS88E&SHOW_PLACE_MAP=True
        if '/application/UTK02/' in url and '.aspx?rn=' in url:
            is_match_target_feature = True
            ibon_dict["answer_index"] = ibon_verification_question(driver, ibon_dict["answer_index"], config_dict)
        else:
            ibon_dict["answer_index"] = -1

    if not is_match_target_feature:
        # https://orders.ibon.com.tw/application/UTK02/UTK0201_000.aspx?PERFORMANCE_ID=0000
        if '/application/UTK02/' in url and '.aspx?PERFORMANCE_ID=' in url:
            is_event_page = False
            if len(url.split('/'))==6:
                is_event_page = True

            if is_event_page:
                if config_dict["area_auto_select"]["enable"]:
                    is_do_ibon_performance_with_ticket_number = False

                    if 'PRODUCT_ID=' in url:
                        # step 1: select area.
                        is_match_target_feature = True
                        is_price_assign_by_bot = ibon_performance(driver, config_dict)
                        if not is_price_assign_by_bot:
                            # this case show captcha and ticket-number in this page.
                            if ibon_ticket_number_appear(driver, config_dict):
                                is_do_ibon_performance_with_ticket_number = True

                    if 'PERFORMANCE_PRICE_AREA_ID=' in url:
                        is_do_ibon_performance_with_ticket_number = True

                    if is_do_ibon_performance_with_ticket_number:
                        if config_dict["advanced"]["disable_adjacent_seat"]:
                            is_finish_checkbox_click = ibon_allow_not_adjacent_seat(driver, config_dict)
                        
                        # captcha
                        is_cpatcha_sent = False
                        if config_dict["ocr_captcha"]["enable"]:
                            domain_name = url.split('/')[2]
                            model_name = url.split('/')[5]
                            if len(model_name) > 7:
                                model_name=model_name[:7]
                            captcha_url = '/pic.aspx?TYPE=%s' % (model_name)
                            #PS: need set cookies once, if user change domain.
                            if not Captcha_Browser is None:
                                Captcha_Browser.Set_Domain(domain_name, captcha_url=captcha_url)

                            is_cpatcha_sent = ibon_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

                        # assign ticket number.
                        is_match_target_feature = True
                        is_ticket_number_assigned = ibon_ticket_number_auto_select(driver, config_dict)
                        if is_ticket_number_assigned:
                            click_ret = ibon_purchase_button_press(driver)

                            if click_ret:
                                # only this case: "ticket number CHANGED by bot" and "cpatcha sent" to play sound!
                                if is_cpatcha_sent:
                                    check_and_play_sound_for_captcha(config_dict)
                        else:
                            is_sold_out = ibon_check_sold_out(driver)
                            if is_sold_out:
                                print("is_sold_out, go back , and refresh.")
                                # plan-A
                                #is_button_clicked = force_press_button(driver, By.CSS_SELECTOR, 'a.btn.btn-primary')
                                # plan-B, easy and better than plan-A
                                driver.back()
                                driver.refresh()

    if not is_match_target_feature:
        #https://orders.ibon.com.tw/application/UTK02/UTK0206_.aspx
        if 'orders.ibon.com.tw/application/UTK02/UTK020' in url and '.aspx' in url:
            is_event_page = False
            if len(url.split('/'))==6:
                is_event_page = True

            # it's pay money page.
            if '/UTK02/UTK0207_.aspx' in url:
                is_event_page = False

            if is_event_page:
                auto_check_agree = config_dict["auto_check_agree"]
                if auto_check_agree:
                    is_finish_checkbox_click = False
                    for i in range(3):
                        is_finish_checkbox_click = ibon_ticket_agree(driver)
                        if is_finish_checkbox_click:
                            break
                    if is_finish_checkbox_click:
                        is_button_clicked = force_press_button(driver, By.CSS_SELECTOR, 'a.btn.btn-pink.continue')

    return ibon_dict

def hkticketing_home(driver):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    # OMG, I forgot why I wrote this code.
    '''
    body_iframe = None
    body_iframe_list = None
    try:
        body_iframe_list = driver.find_elements(By.CSS_SELECTOR, 'body > iframe')
    except Exception as exc:
        if show_debug_message:
            print("find body_iframe fail")
        pass

    hotshow_btn = None
    if not body_iframe_list is None:
        if show_debug_message:
            print("iframe count:", len(body_iframe_list))
        for each_iframe in body_iframe_list:
            try:
                driver.switch_to.frame(each_iframe)
                hotshow_btn = driver.find_element(By.CSS_SELECTOR, 'div.hotshow > a.btn')
                if hotshow_btn is not None:
                    if hotshow_btn.is_enabled() and hotshow_btn.is_displayed():
                        hotshow_btn.click()
            except Exception as exc:
                pass
                if show_debug_message:
                    print("find hotshow btn fail:", exc)
            driver.switch_to.default_content()
    '''

def hkticketing_accept_cookie(driver):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    accept_all_cookies_btn = None
    try:
        accept_all_cookies_btn = driver.find_element(By.ID, 'closepolicy_new')
    except Exception as exc:
        if show_debug_message:
            print("find closepolicy_new fail")
        pass

    if accept_all_cookies_btn is not None:
        is_visible = False
        try:
            if accept_all_cookies_btn.is_enabled() and accept_all_cookies_btn.is_displayed():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            if show_debug_message:
                print("closepolicy_new visible. start to press.")
            try:
                accept_all_cookies_btn.click()
            except Exception as exc:
                pass
                '''
                print("try to click closepolicy_new fail")
                try:
                    driver.execute_script("arguments[0].click();", accept_all_cookies_btn)
                except Exception as exc:
                    pass
                '''
        else:
            if show_debug_message:
                print("closepolicy_new invisible.")

def hkticketing_date_buy_button_press(driver):
    is_date_submiting = False
    el_btn = None
    try:
        my_css_selector = "#buyButton > input"
        el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass

    if el_btn is not None:
        try:
            if el_btn.is_enabled() and el_btn.is_displayed():
                el_btn.click()
                print("buy button pressed.")
                is_date_submiting = True
            else:
                if not el_btn.is_enabled():
                    print("force to press disabled buy button.")
                    try:
                        driver.execute_script("arguments[0].click();", el_btn)
                        ret = True
                    except Exception as exc:
                        pass
        except Exception as exc:
            pass
            # use plan B
            '''
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", el_btn)
                ret = True
            except Exception as exc:
                pass
            '''
    return is_date_submiting

def hkticketing_date_auto_select(driver, auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    matched_blocks = None

    # clean stop word.
    date_keyword = format_keyword_string(date_keyword)
    date_keyword_and = ""

    form_select = None
    try:
        form_select = driver.find_element(By.CSS_SELECTOR, '#p')
    except Exception as exc:
        print("find select#p fail")
        pass

    select_obj = None
    if form_select is not None:
        is_visible = False
        try:
            if form_select.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        if is_visible:
            try:
                select_obj = Select(form_select)
            except Exception as exc:
                pass

    is_date_assigned = False
    if not select_obj is None:
        row_text = None
        try:
            row_text = select_obj.first_selected_option.text
        except Exception as exc:
            pass
        if not row_text is None:
            if len(row_text) > 8:
                if '20' in row_text:
                    # ticket assign.
                    is_date_assigned = True

    if show_debug_message:
        print("is_date_assigned:", is_date_assigned)

    #PS: some blocks are generate by ajax, not appear at first time.
    formated_area_list = None
    is_page_ready = True
    if not is_date_assigned:
        area_list = None
        try:
            my_css_selector = "#p > option"
            area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            print("find #p options date list fail")
            print(exc)

        if area_list is not None:
            area_list_count = len(area_list)
            if show_debug_message:
                print("date_list_count:", area_list_count)

            if area_list_count == 0:
                is_page_ready = False
            else:
                formated_area_list = []

                # filter list.
                row_index = 0
                for row in area_list:
                    row_index += 1
                    row_is_enabled=False
                    option_value_string = None
                    try:
                        if row.is_enabled():
                            '''
                            option_value_string = str(row.get_attribute('value'))
                            if len(option_value_string) > 6:
                                row_is_enabled=True
                            '''
                            # alway disable.
                            option_text_string = str(row.text)
                            print("option_text_string:", option_text_string)
                            if '20' in option_text_string:
                                row_is_enabled=True
                            if ' Exhausted' in option_text_string:
                                row_is_enabled=False
                            if '配售完畢' in option_text_string:
                                row_is_enabled=False
                            if '配售完毕' in option_text_string:
                                row_is_enabled=False
                            if 'No Longer On Sale' in option_text_string:
                                row_is_enabled=False
                            if '已停止發售' in option_text_string:
                                row_is_enabled=False
                            if '已停止发售' in option_text_string:
                                row_is_enabled=False

                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        pass

                    if row_is_enabled:
                        formated_area_list.append(row)

        if formated_area_list is not None:
            area_list_count = len(formated_area_list)
            if show_debug_message:
                print("formated_area_list count:", area_list_count)
            if area_list_count > 0:

                if len(date_keyword) == 0:
                    matched_blocks = formated_area_list
                else:
                    # match keyword.
                    if show_debug_message:
                        print("start to match keyword:", date_keyword)
                    matched_blocks = []

                    row_index = 0
                    for row in formated_area_list:
                        row_index += 1
                        row_is_enabled=True
                        if row_is_enabled:
                            row_text = ""
                            try:
                                row_text = row.text
                            except Exception as exc:
                                print("get text fail")
                                break

                            if row_text is None:
                                row_text = ""

                            if len(row_text) > 0:
                                row_text = format_keyword_string(row_text)
                                if show_debug_message:
                                    print("row_text:", row_text)

                                is_match_area = False
                                match_area_code = 0

                                if date_keyword in row_text:
                                    if len(date_keyword_and) == 0:
                                        if show_debug_message:
                                            print('keyword_and # is empty, directly match.')
                                        # keyword #2 is empty, direct append.
                                        is_match_area = True
                                        match_area_code = 2
                                    else:
                                        if date_keyword_and in row_text:
                                            if show_debug_message:
                                                print('match keyword_and')
                                            is_match_area = True
                                            match_area_code = 3
                                        else:
                                            if show_debug_message:
                                                print('not match keyword_and')
                                            pass

                                if is_match_area:
                                    matched_blocks.append(row)

                    if show_debug_message:
                        if not matched_blocks is None:
                            print("after match keyword, found count:", len(matched_blocks))
            else:
                print("not found date-time-position")
                pass
        else:
            print("date date-time-position is None")
            pass

        target_area = None
        if matched_blocks is not None:
            if len(matched_blocks) > 0:
                target_row_index = 0

                if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    pass

                if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                    target_row_index = len(matched_blocks)-1

                if auto_select_mode == CONST_RANDOM:
                    target_row_index = random.randint(0,len(matched_blocks)-1)

                target_area = matched_blocks[target_row_index]

        if target_area is not None:
            try:
                if target_area.is_enabled():
                    target_area.click()
                    is_date_assigned = True
            except Exception as exc:
                print("click target_area link fail")
                print(exc)
                # use plan B
                '''
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", target_area)
                    is_date_assigned = True
                except Exception as exc:
                    pass
                '''

    # alway, auto submit
    is_date_submiting = False
    el_btn = None
    try:
        my_css_selector = "#buyButton > input"
        el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        pass

    if el_btn is not None:
        try:
            if el_btn.is_enabled() and el_btn.is_displayed():
                el_btn.click()
                print("buy button pressed.")
                is_date_submiting = True
        except Exception as exc:
            pass
            # use plan B
            '''
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", el_btn)
                ret = True
            except Exception as exc:
                pass
            '''
    else:
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            is_need_refresh = True

            if is_date_assigned:
                # if select box assign.
                is_need_refresh = False
            else:
                if not formated_area_list is None:
                    if len(formated_area_list) > 0:
                        # option waiting to assign at next loop.
                        is_need_refresh = False

            # due to select option not generated by server side.
            if is_need_refresh:
                if not is_page_ready:
                    is_need_refresh = False

            if is_need_refresh:
                try:
                    print("is_need_refresh...")
                    driver.refresh()
                    time.sleep(0.3)
                except Exception as exc:
                    pass

    return is_date_submiting

def hkticketing_show(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    date_auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_keyword:", date_keyword)
        print("auto_reload_coming_soon_page_enable:", auto_reload_coming_soon_page_enable)
    is_date_submiting = hkticketing_date_auto_select(driver, date_auto_select_mode, date_keyword, auto_reload_coming_soon_page_enable)

    return is_date_submiting

def hkticketing_area_auto_select(driver, config_dict, area_keyword_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    matched_blocks = None

    area_list = None
    try:
        my_css_selector = "#ticketSelectorContainer > ul > li"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                try:
                    button_class_string = str(row.get_attribute('class'))
                    if len(button_class_string) > 1:
                        if 'disabled' in button_class_string:
                            row_is_enabled=False
                        if 'unavailable' in button_class_string:
                            row_is_enabled=False
                        if 'selected' in button_class_string:
                            # someone is selected. skip this process.
                            is_price_assign_by_bot = True
                            break
                except Exception as exc:
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if is_price_assign_by_bot:
        formated_area_list = None

    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            matched_blocks = []
            if len(area_keyword_list) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            area_keyword_exclude = config_dict["area_auto_select"]["area_keyword_exclude"]
                            if len(area_keyword_exclude) > 0:
                                area_keyword_exclude_array = json.loads("["+ area_keyword_exclude +"]")
                                for exclude_item in area_keyword_exclude_array:
                                    if exclude_item in row_text:
                                        row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if len(area_keyword_list) > 0:
                                # must match keyword.
                                is_match_area = True
                                area_keyword_array = area_keyword_list.split(' ')
                                for area_keyword in area_keyword_array:
                                    area_keyword = format_keyword_string(area_keyword)
                                    if not area_keyword in row_text:
                                        is_match_area = False
                                        break
                            else:
                                # without keyword.
                                is_match_area = True

                            if is_match_area:
                                matched_blocks.append(row)

            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if area_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    if target_area is not None:
        try:
            if target_area.is_enabled():
                target_area.click()
                is_price_assign_by_bot = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                is_price_assign_by_bot = True
            except Exception as exc:
                pass

    return is_need_refresh, is_price_assign_by_bot

def hkticketing_ticket_number_auto_select(driver, config_dict):
    selector_string = 'select.shortSelect'
    by_method = By.CSS_SELECTOR
    return assign_ticket_number_by_select(driver, config_dict, by_method, selector_string)

def hkticketing_nav_to_footer(driver):
    try:
        el_nav = None
        el_nav = driver.find_element(By.CSS_SELECTOR, '#wrapFooter')
        if not el_nav is None:
            builder = ActionChains(driver)
            builder.move_to_element(el_nav)
            builder.click(el_nav)
            builder.perform()
    except Exception as exc:
        pass

def hkticketing_next_button_press(driver):
    ret = False

    el_btn = None
    try:
        el_btn = driver.find_element(By.CSS_SELECTOR, '#continueBar > div.chooseTicketsOfferDiv > button')
    except Exception as exc:
        print("find next button fail...")
        print(exc)

    if el_btn is not None:
        print("bingo, found next button, start to press")
        hkticketing_nav_to_footer(driver)
        try:
            if el_btn.is_enabled() and el_btn.is_displayed():
                el_btn.click()
                ret = True
        except Exception as exc:
            print("click next button fail...")
            print(exc)

    return ret

def hkticketing_go_to_payment(driver):
    ret = False

    el_btn = None
    try:
        el_btn = driver.find_element(By.CSS_SELECTOR, '#goToPaymentButton')
    except Exception as exc:
        print("find next button fail...")
        print(exc)

    if el_btn is not None:
        print("bingo, found next button, start to press")
        try:
            if el_btn.is_enabled() and el_btn.is_displayed():
                el_btn.click()
                ret = True
        except Exception as exc:
            print("click next button fail...")
            print(exc)

    return ret

def hkticketing_ticket_delivery_option(driver):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    is_delivery_option_assigned = False

    form_select = None
    try:
        selector_string = '#selectDeliveryType'
        form_select = driver.find_element(By.CSS_SELECTOR, selector_string)
    except Exception as exc:
        if show_debug_message:
            print("find selectDeliveryType select fail")
            print(exc)
        pass

    select_obj = None
    if form_select is not None:
        is_visible = False
        try:
            is_visible = form_select.is_enabled()
        except Exception as exc:
            pass
        if is_visible:
            try:
                select_obj = Select(form_select)
            except Exception as exc:
                pass

    if select_obj is not None:
        try:
            select_obj.select_by_value("1")
            is_delivery_option_assigned = True
        except Exception as exc:
            print("delivery_option fail")
            print(exc)


    return is_delivery_option_assigned

def hkticketing_hide_tickets_blocks(driver):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    actionBlock_divs = None
    try:
        selector_string = 'div.actionBlock.note'
        actionBlock_divs = driver.find_elements(By.CSS_SELECTOR, selector_string)
        for each_div in actionBlock_divs:
            driver.execute_script("arguments[0].innerHTML='';", each_div);
    except Exception as exc:
        if show_debug_message:
            print("find selectDeliveryType select fail")
            print(exc)
        pass

    detailModuleCopy_divs = None
    try:
        selector_string = 'div.detailModuleCopy'
        detailModuleCopy_divs = driver.find_elements(By.CSS_SELECTOR, selector_string)
        if not detailModuleCopy_divs is None:
            driver.execute_script("arguments[0].innerHTML='';", detailModuleCopy_divs);
    except Exception as exc:
        pass

    mapWrapper_divs = None
    try:
        selector_string = 'div.mapWrapper'
        mapWrapper_divs = driver.find_elements(By.CSS_SELECTOR, selector_string)
        if not mapWrapper_divs is None:
            driver.execute_script("arguments[0].innerHTML='';", mapWrapper_divs);
    except Exception as exc:
        pass


def hkticketing_performance(driver, config_dict, domain_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

        if show_debug_message:
            print("area_keyword:", area_keyword)

        if len(area_keyword) > 0:
            area_keyword_array = json.loads("["+ area_keyword +"]")
            for area_keyword_item in area_keyword_array:
                is_need_refresh, is_price_assign_by_bot = hkticketing_area_auto_select(driver, config_dict, area_keyword_item)
                if not is_need_refresh:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.
            is_need_refresh, is_price_assign_by_bot = hkticketing_area_auto_select(driver, config_dict, "")

        if is_need_refresh:
            if show_debug_message:
                print("is_need_refresh:", is_need_refresh)
            try:
                driver.refresh()
            except Exception as exc:
                pass

        # hide blocks.
        #hkticketing_hide_tickets_blocks(driver)

        # goto bottom.
        hkticketing_nav_to_footer(driver)

        # choose ticket.
        is_ticket_number_assigned = hkticketing_ticket_number_auto_select(driver, config_dict)
        if show_debug_message:
            print("is_ticket_number_assigned:", is_ticket_number_assigned)

        # Select a delivery option
        is_delivery_option_assigned = True
        if not 'galaxymacau.com' in domain_name:
            # hkticketing
            is_delivery_option_assigned = False
            if is_ticket_number_assigned:
                is_delivery_option_assigned = hkticketing_ticket_delivery_option(driver)
            if show_debug_message:
                print("is_delivery_option_assigned:", is_delivery_option_assigned)

        if is_delivery_option_assigned:
            auto_press_next_step_button = True
            if auto_press_next_step_button:
                if is_price_assign_by_bot:
                    for i in range(2):
                        click_ret = hkticketing_next_button_press(driver)
                        time.sleep(0.2)
                        if click_ret:
                            break


    return is_price_assign_by_bot


def hkticketing_escape_robot_detection(driver):
    ret = False

    el_main_iframe = None
    try:
        el_main_iframe = driver.find_element(By.ID, 'main-iframe')
    except Exception as exc:
        #print("find el_main_iframe fail...")
        #print(exc)
        pass

    if el_main_iframe is not None:
        print("we have been detected..., found el_main_iframe")
        #entry_url="https://queue.hkticketing.com/hotshow.html"
        entry_url="https://premier.hkticketing.com/"
        try:
            #print("start to escape..")
            #driver.get(entry_url)
            pass
        except Exception as exc:
            print(exc)

    return ret


def hkticketing_main(driver, url, config_dict, hkticketing_dict):
    home_url_list = ['https://premier.hkticketing.com/'
    ,'https://hotshow.hkticketing.com/'
    ,'https://premier.hkticketing.com/default.aspx'
    ,'https://hotshow.hkticketing.com/default.aspx'
    ,'https://premier.hkticketing.com/Membership/Login.aspx'
    ,'https://hotshow.hkticketing.com/Membership/Login.aspx'
    ]
    for each_url in home_url_list:
        if each_url == url:
            hkticketing_home(driver)
            break

    hkticketing_accept_cookie(driver)

    if 'queue.hkticketing.com/hotshow.html' in url:
        entry_url = 'http://entry-hotshow.hkticketing.com/'
        try:
            driver.get(entry_url)
        except Exception as exc:
            pass
        # 刷太快, 會被封IP?
        time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    # PS: share function with galaxymacau, but memeber is not shared.
    if 'hkticketing.com/Membership/Login.aspx' in url:
        account = config_dict["advanced"]["hkticketing_account"].strip()
        if len(account) > 4:
            hkticketing_login(driver, account, decryptMe(config_dict["advanced"]["hkticketing_password"]))

    is_ready_to_buy_from_queue = False
    # Q: How to know ready to buy ticket from queue?
    if is_ready_to_buy_from_queue:
        # play sound when ready to buy ticket.
        check_and_play_sound_for_captcha(config_dict)

    #https://premier.hkticketing.com/shows/show.aspx?sh=XXXX
    if 'shows/show.aspx?' in url:
        is_modal_dialog_popup = check_modal_dialog_popup(driver)
        if is_modal_dialog_popup:
            print("is_modal_dialog_popup! skip...")
        else:
            is_event_page = False
            if len(url.split('/'))==5:
                is_event_page = True

            if is_event_page:
                if config_dict["tixcraft"]["date_auto_select"]["enable"]:
                    if not hkticketing_dict["is_date_submiting"]:
                        hkticketing_dict["is_date_submiting"] = hkticketing_show(driver, config_dict)
                        pass
                    else:
                        #print('double check buy button status.')
                        hkticketing_date_buy_button_press(driver)
    else:
        hkticketing_dict["is_date_submiting"] = False

    # https://premier.hkticketing.com/events/XXX/venues/KSH/performances/XXX/tickets
    if '/events/' in url and '/performances/' in url:
        robot_detection = hkticketing_escape_robot_detection(driver)

        is_modal_dialog_popup = check_modal_dialog_popup(driver)
        if is_modal_dialog_popup:
            print("is_modal_dialog_popup! skip...")
        else:
            if '/tickets' in url:
                domain_name = url.split('/')[2]
                if config_dict["area_auto_select"]["enable"]:
                    hkticketing_performance(driver, config_dict, domain_name)
                    pass

            if '/seatmap' in url:
                # goto bottom.
                hkticketing_nav_to_footer(driver)
                hkticketing_go_to_payment(driver)

    # for ticketing.galaxymacau
    if "/busy_galaxy." in url:
        domain_name = url.split('/')[2]
        new_url = "https://%s/default.aspx" % (domain_name)
        print("redirecting to url:", new_url)
        try:
            # web server is too busy to reponse.
            driver.execute_script("document.location.href = \"/default.aspx\";")
        except Exception as exc:
            pass

        try:
            driver.get(new_url)
        except Exception as exc:
            pass

        # 刷太快, 會被封IP?
        time.sleep(config_dict["advanced"]["auto_reload_page_interval"])

    
    is_check_access_deined = False
    macau_url_list = ["galaxymacau.com/default.aspx"
    , "galaxymacau.com/shows/show.aspx?sh="
    , "galaxymacau.com/detection.aspx"]
    for macau_url in macau_url_list:
        if macau_url in url:
            is_check_access_deined = True
            break
    if "https://www.ticketing.galaxymacau.com/" == url:
        is_check_access_deined = True

    macau_retry_string_list = [ "Access Denied"
    , "Service Unavailable"
    , "service is unavailable"
    , "HTTP Error 503"
    , "The network path was not found"
    , "Could not open a connection to SQL Server"]
    if is_check_access_deined:
        domain_name = url.split('/')[2]
        new_url = "https://%s/default.aspx" % (domain_name)

        is_need_refresh = False
        macau_body = None
        try:
            my_css_selector = "body"
            macau_body = driver.find_element(By.CSS_SELECTOR, my_css_selector)
            if not macau_body is None:
                for macau_retry_string in macau_retry_string_list:
                    if macau_retry_string in macau_body.text:
                        is_need_refresh = True
                        break
        except Exception as exc:
            pass

        if is_need_refresh:
            print("Start to automatically refresh page for galaxymacau.")
            try:
                driver.get(new_url)
            except Exception as exc:
                pass

    return hkticketing_dict

def khan_go_buy_redirect(driver, domain_name):
    is_button_clicked = False
    if 'kham.com' in domain_name:
        is_button_clicked = force_press_button(driver, By.CSS_SELECTOR, 'p > a > button.red')
    if 'ticket.com' in domain_name:
        is_button_clicked = force_press_button(driver, By.CSS_SELECTOR, 'div.row > div > a.btn.btn-order.btn-block')
    return is_button_clicked

def hkam_date_auto_select(driver, domain_name, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    ret = False
    matched_blocks = None

    # clean stop word.
    date_keyword = format_keyword_string(date_keyword)
    date_keyword_and = ""

    # default not selected.
    is_date_assigned = False
    if not is_date_assigned:
        area_list = None
        try:
            # for kham.com
            my_css_selector = "table.eventTABLE > tbody > tr"
            if 'ticket.com' in domain_name:
                my_css_selector = "div.description > table.table.table-striped.itable > tbody > tr"

            area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            print("find #date-time tr list fail")
            print(exc)

        #PS: some blocks are generate by ajax, not appear at first time.
        formated_area_list = None
        if area_list is not None:
            area_list_count = len(area_list)
            if show_debug_message:
                print("date_list_count:", area_list_count)

            if area_list_count > 0:
                formated_area_list = []

                # filter list.
                row_index = 0
                for row in area_list:
                    row_index += 1

                    row_is_enabled=False

                    row_text = ""
                    try:
                        row_text = row.text
                    except Exception as exc:
                        if show_debug_message:
                            print(exc)
                        pass

                    if row_text is None:
                        row_text=""

                    if '立即訂購' in row_text:
                        try:
                            # for kham.com
                            my_css_selector = "a > button"
                            if 'ticket.com' in domain_name:
                                my_css_selector = "td > button.btn"

                            el_btn = row.find_element(By.CSS_SELECTOR, my_css_selector)
                            if el_btn is not None:
                                if el_btn.is_enabled():
                                    #print("row's button enabled.")
                                    row_is_enabled=True
                        except Exception as exc:
                            if show_debug_message:
                                print(exc)
                            pass

                    if row_is_enabled:
                        formated_area_list.append(row)
            else:
                if show_debug_message:
                    print("area_list is None...")

        if formated_area_list is not None:
            area_list_count = len(formated_area_list)
            if show_debug_message:
                print("formated_area_list count:", area_list_count)
            if area_list_count > 0:
                if len(date_keyword) == 0:
                    matched_blocks = formated_area_list
                else:
                    # match keyword.
                    if show_debug_message:
                        print("start to match keyword:", date_keyword)
                    matched_blocks = []

                    row_index = 0
                    for row in formated_area_list:
                        row_index += 1
                        row_is_enabled=True
                        if row_is_enabled:
                            row_text = ""
                            try:
                                row_text = row.text
                            except Exception as exc:
                                print("get text fail")
                                break

                            if row_text is None:
                                row_text = ""

                            if len(row_text) > 0:
                                row_text = format_keyword_string(row_text)
                                if show_debug_message:
                                    print("row_text:", row_text)

                                is_match_area = False
                                match_area_code = 0

                                if date_keyword in row_text:
                                    if len(date_keyword_and) == 0:
                                        if show_debug_message:
                                            print('keyword_and # is empty, directly match.')
                                        # keyword #2 is empty, direct append.
                                        is_match_area = True
                                        match_area_code = 2
                                    else:
                                        if date_keyword_and in row_text:
                                            if show_debug_message:
                                                print('match keyword_and')
                                            is_match_area = True
                                            match_area_code = 3
                                        else:
                                            if show_debug_message:
                                                print('not match keyword_and')
                                            pass

                                if is_match_area:
                                    matched_blocks.append(row)

                    if show_debug_message:
                        if not matched_blocks is None:
                            print("after match keyword, found count:", len(matched_blocks))
            else:
                print("not found date-time-position")
                pass
        else:
            print("date date-time-position is None")
            pass

        target_area = None
        if matched_blocks is not None:
            if len(matched_blocks) > 0:
                target_row_index = 0

                if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                    pass

                if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                    target_row_index = len(matched_blocks)-1

                if auto_select_mode == CONST_RANDOM:
                    target_row_index = random.randint(0,len(matched_blocks)-1)

                target_area = matched_blocks[target_row_index]

        if target_area is not None:
            el_btn = None
            try:
                # for kham.com
                my_css_selector = "a > button"
                if 'ticket.com' in domain_name:
                    my_css_selector = "td > button.btn"
                el_btn = target_area.find_element(By.CSS_SELECTOR, my_css_selector)
            except Exception as exc:
                pass

            if el_btn is not None:
                try:
                    if el_btn.is_enabled() and el_btn.is_displayed():
                        el_btn.click()
                        print("buy button pressed.")
                        ret = True
                except Exception as exc:
                    # use plan B
                    try:
                        print("force to click by js.")
                        driver.execute_script("arguments[0].click();", el_btn)
                        ret = True
                    except Exception as exc:
                        pass

    '''
        if auto_reload_coming_soon_page_enable:
            # auto refresh for date list page.
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        driver.refresh()
                        time.sleep(0.4)
                    except Exception as exc:
                        pass
    '''

    return ret

def kham_product(driver, domain_name, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_date_assign_by_bot = hkam_date_auto_select(driver, domain_name, config_dict)

    if not is_date_assign_by_bot:
        # click not on sale now.
        is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'div.ui-dialog-buttonset > button.ui-button')
        pass

    return is_date_assign_by_bot

def kham_area_auto_select(driver, domain_name, config_dict, area_keyword_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    matched_blocks = None

    area_list = None
    try:
        # for kham.com
        my_css_selector = "table#salesTable > tbody > tr.status_tr"
        if "ticket.com.tw" in domain_name:
            my_css_selector = "li.main"
            print("my_css_selector:",my_css_selector)
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find #ticket-price-tbl date list fail")
        print(exc)

    readme_table_mode = False
    if area_list is None:
        readme_table_mode = True
    else:
        if len(area_list)==0:
            readme_table_mode = True
    if readme_table_mode:
        # TODO://
        # ...
        pass

    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)
            print("area_keyword_list:", area_keyword_list)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                
                row_is_enabled=True

                row_text = ""
                try:
                    row_text = row.text
                except Exception as exc:
                    pass

                if row_text is None:
                    row_text = ""

                if len(row_text) > 0:
                    area_keyword_exclude = config_dict["area_auto_select"]["area_keyword_exclude"]
                    if len(area_keyword_exclude) > 0:
                        area_keyword_exclude_array = json.loads("["+ area_keyword_exclude +"]")
                        for exclude_item in area_keyword_exclude_array:
                            if exclude_item in row_text:
                                row_text = ""

                if '售完' in row_text:
                    row_is_enabled = False

                if len(row_text) == 0:
                    row_is_enabled = False

                if row_is_enabled:
                    pass
                    # too many rows, too slow, disable to check.
                    '''
                    try:
                        is_row_with_id = False
                        tr_id_string = str(row.get_attribute('id'))
                        if len(tr_id_string) > 1:
                            is_row_with_id = True
                        if is_row_with_id:
                            row_is_enabled=True
                    except Exception as exc:
                        pass
                    '''

                if row_is_enabled:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            matched_blocks = []
            if len(area_keyword_list) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False

                            if len(area_keyword_list) > 0:
                                # must match keyword.
                                is_match_area = True
                                area_keyword_array = area_keyword_list.split(' ')
                                for area_keyword in area_keyword_array:
                                    area_keyword = format_keyword_string(area_keyword)
                                    if not area_keyword in row_text:
                                        is_match_area = False
                                        break
                            else:
                                # without keyword.
                                is_match_area = True

                            if is_match_area:
                                matched_blocks.append(row)

            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if area_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]
    else:
        if show_debug_message:
            print("matched_blocks is None.")

    if target_area is not None:
        try:
            if target_area.is_enabled():
                target_area.click()
                is_price_assign_by_bot = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                is_price_assign_by_bot = True
            except Exception as exc:
                pass
    else:
        if show_debug_message:
            print("target_area is None, no target to click.")

    if show_debug_message:
        print("is_need_refresh:", is_need_refresh)
        print("is_price_assign_by_bot:", is_price_assign_by_bot)

    return is_need_refresh, is_price_assign_by_bot

def kham_performance_ticket_number(driver, config_dict):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_ticket_number_assigned = False

    ticket_number = config_dict["ticket_number"]

    form_input = None
    try:
        form_input = driver.find_element(By.CSS_SELECTOR, '#AMOUNT')
    except Exception as exc:
        if show_debug_message:
            print("find #AMOUNT fail")
            print(exc)
        pass

    inputed_value = None
    if form_input is not None:
        try:
            inputed_value = form_input.get_attribute('value')
        except Exception as exc:
            print("get_attribute value fail")
            pass

    if inputed_value is None:
        inputed_value = ""

    if inputed_value == "" or inputed_value == "0":
        is_visible = False
        try:
            if form_input.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            try:
                form_input.click()
                form_input.clear()
                form_input.send_keys(str(ticket_number))
                is_ticket_number_assigned = True
            except Exception as exc:
                # use plan B
                '''
                try:
                    print("force to click by js.")
                    driver.execute_script("arguments[0].click();", el_div)
                    ret = True
                except Exception as exc:
                    pass
                '''
                pass

    if len(inputed_value) > 0:
        if not inputed_value=="0":
            is_ticket_number_assigned = True

    return is_ticket_number_assigned

def kham_choice_auto_seat(driver):
    is_switch_to_auto_seat = False

    btn_switch_to_auto_seat = None
    try:
        my_css_selector = '#BUY_TYPE_2'
        btn_switch_to_auto_seat = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        #print("find BUY_TYPE_2 input fail")
        pass

    if btn_switch_to_auto_seat is not None:
        button_class_string = None
        try:
            button_class_string = form_verifyCode.get_attribute('class')
        except Exception as exc:
            #print("get_attribute('class') fail")
            pass

        if button_class_string is None:
            button_class_string = ""

        if button_class_string == "":
            try:
                btn_switch_to_auto_seat.click()
                is_switch_to_auto_seat = True
            except Exception as exc:
                try:
                    driver.execute_script("arguments[0].click();", btn_switch_to_auto_seat)
                    ret = True
                except Exception as exc:
                    pass

        if button_class_string == "red":
            is_switch_to_auto_seat = True

    return is_switch_to_auto_seat


def kham_performance(driver, config_dict, ocr, Captcha_Browser, domain_name, model_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()

        if show_debug_message:
            print("area_keyword:", area_keyword)

        is_need_refresh = False

        if len(area_keyword) > 0:
            area_keyword_array = json.loads("["+ area_keyword +"]")
            for area_keyword_item in area_keyword_array:
                is_need_refresh, is_price_assign_by_bot = kham_area_auto_select(driver, domain_name, config_dict, area_keyword_item)
                if not is_need_refresh:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.
            is_need_refresh, is_price_assign_by_bot = kham_area_auto_select(driver, domain_name, config_dict, "")

        if is_need_refresh:
            if show_debug_message:
                print("is_need_refresh:", is_need_refresh)
            try:
                driver.refresh()
            except Exception as exc:
                pass

        is_captcha_sent = kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

    return is_price_assign_by_bot


def kham_keyin_captcha_code(driver, answer = "", auto_submit = False):
    is_verifyCode_editing = False

    form_verifyCode = None
    try:
        my_css_selector = 'input[value="驗證碼"]'
        form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find blockLogin input fail")
        try:
            my_css_selector = 'input[placeholder="驗證碼"]'
            form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        except Exception as exc:
            pass

    is_start_to_input_answer = False
    if form_verifyCode is not None:
        if len(answer) > 0:
            inputed_value = None
            try:
                inputed_value = form_verifyCode.get_attribute('value')
            except Exception as exc:
                print("find verify code fail")
                pass

            if inputed_value is None:
                inputed_value = ""

            if inputed_value == "驗證碼":
                try:
                    form_verifyCode.clear()
                except Exception as exc:
                    print("clear verify code fail")
                    pass
            else:
                if len(inputed_value) > 0:
                    print("captcha text inputed:", inputed_value, "target answer:", answer)
                    is_verifyCode_editing = True
                else:
                    is_start_to_input_answer = True
        else:
            try:
                form_verifyCode.clear()
            except Exception as exc:
                print("clear verify code fail")
                pass

    if is_start_to_input_answer:
        answer=answer.upper()
        #print("start to fill answer.")
        try:
            form_verifyCode.clear()
            form_verifyCode.send_keys(answer)
        except Exception as exc:
            print("send_keys ocr answer fail:", answer)

    return is_verifyCode_editing

def kham_auto_ocr(driver, config_dict, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, model_name):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    print("start to ddddocr")

    is_need_redo_ocr = False
    is_form_sumbited = False

    ocr_answer = None
    if not ocr is None:
        if show_debug_message:
            print("away_from_keyboard_enable:", away_from_keyboard_enable)
            print("previous_answer:", previous_answer)
            print("ocr_captcha_image_source:", ocr_captcha_image_source)

        ocr_start_time = time.time()

        img_base64 = None
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.Request_Captcha())
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'chk_pic'
            try:
                form_verifyCode_base64 = driver.execute_async_script("""
                    var canvas = document.createElement('canvas');
                    var context = canvas.getContext('2d');
                    var img = document.getElementById('%s');
                    if(img!=null) {
                    canvas.height = img.naturalHeight;
                    canvas.width = img.naturalWidth;
                    context.drawImage(img, 0, 0);
                    callback = arguments[arguments.length - 1];
                    callback(canvas.toDataURL()); }
                    """ % (image_id))
                if not form_verifyCode_base64 is None:
                    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
            except Exception as exc:
                if show_debug_message:
                    print("canvas exception:", str(exc))
                pass
        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                pass

        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        print("ocr elapsed time:", "{:.3f}".format(ocr_elapsed_time))
    else:
        print("ddddocr is None")

    if not ocr_answer is None:
        ocr_answer = ocr_answer.strip()
        print("ocr_answer:", ocr_answer)
        if len(ocr_answer)==4:
            who_care_var = kham_keyin_captcha_code(driver, answer = ocr_answer, auto_submit = away_from_keyboard_enable)
        else:
            if not away_from_keyboard_enable:
                kham_keyin_captcha_code(driver)
            else:
                is_need_redo_ocr = True
                if previous_answer != ocr_answer:
                    previous_answer = ocr_answer
                    print("click captcha again")
                    if True:
                        # selenium solution.
                        jquery_string = '$("#chk_pic").attr("src", "/pic.aspx?TYPE=%s&ts=" + new Date().getTime());' % (model_name)
                        driver.execute_script(jquery_string)

                        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
                            time.sleep(0.3)
                    else:
                        # Non_Browser solution.
                        if not Captcha_Browser is None:
                            new_captcha_url = Captcha_Browser.Request_Refresh_Captcha() #取得新的CAPTCHA
                            if new_captcha_url != "":
                                #PS:[TODO]
                                #tixcraft_change_captcha(driver, new_captcha_url) #更改CAPTCHA圖
                                pass
    else:
        print("ocr_answer is None")
        print("previous_answer:", previous_answer)
        if previous_answer is None:
            kham_keyin_captcha_code(driver)
        else:
            # page is not ready, retry again.
            # PS: usually occur in async script get captcha image.
            is_need_redo_ocr = True

    return is_need_redo_ocr, previous_answer, is_form_sumbited

def kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name):
    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False
    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]

    #PS: need a 'auto assign seat' feature to enable away_from_keyboard feature.
    away_from_keyboard_enable = False

    is_cpatcha_sent = False
    previous_answer = None
    for redo_ocr in range(999):
        is_need_redo_ocr, previous_answer, is_form_sumbited = kham_auto_ocr(driver, config_dict, ocr, away_from_keyboard_enable, previous_answer, Captcha_Browser, ocr_captcha_image_source, model_name)

        # TODO: must ensure the answer is corrent...
        is_cpatcha_sent = True

        if is_form_sumbited:
            break

        if not away_from_keyboard_enable:
            break

        if not is_need_redo_ocr:
            break

    return is_cpatcha_sent

def kham_check_captcha_text_error(driver, config_dict):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_reset_password_text = False
    el_message = None
    try:
        my_css_selector = 'div.ui-dialog > div#dialog-message.ui-dialog-content'
        el_message = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not el_message is None:
            el_message_text = el_message.text
            if show_debug_message:
                print("el_message_text", el_message_text)
            if el_message_text is None:
                el_message_text = ""
            if "【驗證碼】輸入錯誤" in el_message_text:
                is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'div.ui-dialog-buttonset > button.ui-button')
                is_reset_password_text = True
                kham_keyin_captcha_code(driver)
    except Exception as exc:
        pass

    return is_reset_password_text

def kham_allow_not_adjacent_seat(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    agree_checkbox = None
    try:
        my_css_selector = 'table.eventTABLE > tbody > tr > td > input[type="checkbox"]'
        agree_checkbox = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find ibon adjacent_seat checkbox Exception")
        if show_debug_message:
            print(exc)
        pass

    is_finish_checkbox_click = force_check_checkbox(driver, agree_checkbox)

    return is_finish_checkbox_click

def kham_main(driver, url, config_dict, ocr, Captcha_Browser):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True
   
    home_url_list = ['https://kham.com.tw/'
    ,'https://kham.com.tw/application/utk01/utk0101_.aspx'
    ,'https://kham.com.tw/application/utk01/utk0101_03.aspx'
    ,'https://ticket.com.tw/application/utk01/utk0101_.aspx'
    ]
    for each_url in home_url_list:
        if each_url == url.lower():
            is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'.closeBTN')

            if config_dict["ocr_captcha"]["enable"]:
                domain_name = url.split('/')[2]
                if not Captcha_Browser is None:
                    Captcha_Browser.Set_cookies(driver.get_cookies())
                    Captcha_Browser.Set_Domain(domain_name)
            break

    #https://kham.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=XXX
    if 'utk0201_.aspx?product_id=' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            domain_name = url.split('/')[2]
            khan_go_buy_redirect(driver, domain_name)

    # https://kham.com.tw/application/UTK02/UTK0201_00.aspx?PRODUCT_ID=N28TFATD
    if 'utk0201_00.aspx?product_id=' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            date_auto_select_enable = config_dict["tixcraft"]["date_auto_select"]["enable"]
            if date_auto_select_enable:
                domain_name = url.split('/')[2]
                kham_product(driver, domain_name, config_dict)

    # https://kham.com.tw/application/UTK02/UTK0204_.aspx?PERFORMANCE_ID=N28UQPA1&PRODUCT_ID=N28TFATD
    if '.aspx?performance_id=' in url.lower() and 'product_id=' in url.lower():
        domain_name = url.split('/')[2]
        model_name = url.split('/')[5]
        if len(model_name) > 7:
            model_name=model_name[:7]
        captcha_url = '/pic.aspx?TYPE=%s' % (model_name)
        #PS: need set cookies once, if user change domain.
        if not Captcha_Browser is None:
            Captcha_Browser.Set_Domain(domain_name, captcha_url=captcha_url)

        if config_dict["ocr_captcha"]["enable"]:
            is_reset_password_text = kham_check_captcha_text_error(driver, config_dict)
            if is_reset_password_text:
                is_captcha_sent = kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

        is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'div.ui-dialog-buttonset > button.ui-button')
        if config_dict["area_auto_select"]["enable"]:
            is_switch_to_auto_seat = kham_choice_auto_seat(driver)
            is_price_assign_by_bot = kham_performance(driver, config_dict, ocr, Captcha_Browser, domain_name, model_name)

    #https://kham.com.tw/application/UTK02/UTK0205_.aspx?PERFORMANCE_ID=XXX&GROUP_ID=30&PERFORMANCE_PRICE_AREA_ID=XXX
    if '.aspx?performance_id=' in url.lower() and 'performance_price_area_id=' in url.lower():
        domain_name = url.split('/')[2]
        model_name = url.split('/')[5]
        if len(model_name) > 7:
            model_name=model_name[:7]
        captcha_url = '/pic.aspx?TYPE=%s' % (model_name)
        #PS: need set cookies once, if user change domain.
        if not Captcha_Browser is None:
            Captcha_Browser.Set_Domain(domain_name, captcha_url=captcha_url)

        is_captcha_sent = False
        if config_dict["ocr_captcha"]["enable"]:
            is_reset_password_text = kham_check_captcha_text_error(driver, config_dict)
            if is_reset_password_text:
                is_captcha_sent = kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

        if config_dict["advanced"]["disable_adjacent_seat"]:
            is_finish_checkbox_click = kham_allow_not_adjacent_seat(driver, config_dict)


        is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'div.ui-dialog-buttonset > button.ui-button')
        if config_dict["ocr_captcha"]["enable"]:
            if not is_captcha_sent:
                is_captcha_sent = kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)

            is_ticket_number_assigned = kham_performance_ticket_number(driver, config_dict)
            if is_ticket_number_assigned:
                if is_captcha_sent:
                    el_btn = None
                    my_css_selector = 'button[onclick="addShoppingCart();return false;"]'
                    try:
                        el_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                        if not el_btn is None:
                            el_btn.click()
                    except Exception as exc:
                        print("find chkCart button fail")
                        pass

    if '/utk13/utk1306_.aspx' in url.lower():
        is_button_clicked = force_press_button(driver, By.CSS_SELECTOR,'div.ui-dialog-buttonset > button.ui-button')
        if config_dict["ocr_captcha"]["enable"]:
            domain_name = url.split('/')[2]
            model_name = url.split('/')[5]
            if len(model_name) > 7:
                model_name=model_name[:7]
            captcha_url = '/pic.aspx?TYPE=%s' % (model_name)
            #PS: need set cookies once, if user change domain.
            if not Captcha_Browser is None:
                Captcha_Browser.Set_Domain(domain_name, captcha_url=captcha_url)

            kham_captcha(driver, config_dict, ocr, Captcha_Browser, model_name)
            account = config_dict["advanced"]["kham_account"]
            if len(account) > 4:
                kham_login(driver, account, decryptMe(config_dict["advanced"]["kham_password"]))

def ticketplus_date_auto_select(driver, config_dict):
    show_debug_message = True    # debug.
    show_debug_message = False   # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    # read config.
    auto_select_mode = config_dict["tixcraft"]["date_auto_select"]["mode"]
    date_keyword = config_dict["tixcraft"]["date_auto_select"]["date_keyword"].strip()
    # TODO: implement this feature.
    date_keyword_and = ""
    pass_date_is_sold_out_enable = config_dict["tixcraft"]["pass_date_is_sold_out"]
    auto_reload_coming_soon_page_enable = config_dict["tixcraft"]["auto_reload_coming_soon_page"]

    if show_debug_message:
        print("date_auto_select_mode:", auto_select_mode)
        print("date_keyword:", date_keyword)

    area_list = None
    try:
        area_list = driver.find_elements(By.CSS_SELECTOR, 'div#buyTicket > div.sesstion-item')
    except Exception as exc:
        print("find #gameList fail")

    find_ticket_text_list = ['立即購票']
    sold_out_text_list = ['銷售一空','尚未開賣']

    matched_blocks = None
    formated_area_list = None

    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("date_list_count:", area_list_count)

        if area_list_count > 0:
            formated_area_list = []
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True
                try:
                    if not row.is_enabled():
                        row_is_enabled=False
                    
                    row_text = ""
                    # check buy button.
                    if row_is_enabled:
                        row_text = row.text
                        if row_text is None:
                            row_text = ""

                        row_is_enabled=False
                        for text_item in find_ticket_text_list:
                            if text_item in row_text:
                                row_is_enabled = True
                                break

                    # check sold out text.
                    if row_is_enabled:
                        if pass_date_is_sold_out_enable:
                            for sold_out_item in sold_out_text_list:
                                if sold_out_item in row_text:
                                    row_is_enabled = False
                                    if show_debug_message:
                                        print("match sold out text: %s, skip this row." % (sold_out_item))
                                    break

                except Exception as exc:
                    if show_debug_message:
                        print(exc)
                    pass

                if row_is_enabled:
                    formated_area_list.append(row)

            if show_debug_message:
                print("formated_area_list count:", len(formated_area_list))

            if len(date_keyword) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                date_keyword = format_keyword_string(date_keyword)
                if show_debug_message:
                    print("start to match formated keyword:", date_keyword)
                matched_blocks = []

                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False
                            match_area_code = 0

                            if date_keyword in row_text:
                                if len(date_keyword_and) == 0:
                                    if show_debug_message:
                                        print('keyword_and # is empty, directly match.')
                                    # keyword #2 is empty, direct append.
                                    is_match_area = True
                                    match_area_code = 2
                                else:
                                    if date_keyword_and in row_text:
                                        if show_debug_message:
                                            print('match keyword_and')
                                        is_match_area = True
                                        match_area_code = 3
                                    else:
                                        if show_debug_message:
                                            print('not match keyword_and')
                                        pass

                            if is_match_area:
                                matched_blocks.append(row)

                if show_debug_message:
                    if not matched_blocks is None:
                        print("after match keyword, found count:", len(matched_blocks))
        else:
            print("not found date-time-position")
            pass
    else:
        print("date date-time-position is None")
        pass

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]

    is_date_clicked = False
    if target_area is not None:
        target_button = None
        try:
            target_button = target_area.find_element(By.CSS_SELECTOR, 'button')
            if not target_button is None:
                if target_button.is_enabled():
                    if show_debug_message:
                        print("start to press button...")
                    target_button.click()
                    is_date_clicked = True
            else:
                if show_debug_message:
                    print("target_button in target row is None.")
        except Exception as exc:
            if show_debug_message:
                print("find or press button fail:", exc)

            if not target_button is None:
                print("try to click button fail, force click by js.")
                try:
                    driver.execute_script("arguments[0].click();", target_button)
                except Exception as exc:
                    pass

    # [PS]: current reload condition only when
    if auto_reload_coming_soon_page_enable:
        if not is_date_clicked:
            if not formated_area_list is None:
                if len(formated_area_list) == 0:
                    try:
                        driver.refresh()
                        time.sleep(0.3)
                    except Exception as exc:
                        pass

    return is_date_clicked

def ticketplus_order_expansion_auto_select(driver, config_dict, area_keyword_list):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    area_auto_select_mode = config_dict["area_auto_select"]["mode"]

    is_price_assign_by_bot = False
    is_need_refresh = False

    matched_blocks = None

    area_list = None
    try:
        #print("try to find cityline area block")
        my_css_selector = "div.v-expansion-panels > div.v-expansion-panel"
        area_list = driver.find_elements(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find .v-expansion-panel date list fail")
        print(exc)

    formated_area_list = None
    if area_list is not None:
        area_list_count = len(area_list)
        if show_debug_message:
            print("area_list_count:", area_list_count)
            print("area_keyword_list:", area_keyword_list)

        if area_list_count > 0:
            formated_area_list = []
            # filter list.
            row_index = 0
            for row in area_list:
                row_index += 1
                row_is_enabled=True

                if row_is_enabled:
                    row_text = ""
                    try:
                        row_text = row.text
                    except Exception as exc:
                        pass

                    if row_text is None:
                        row_text = ""

                    if '剩餘：0' in row_text:
                        row_is_enabled=False

                    if len(row_text) > 0:
                        area_keyword_exclude = config_dict["area_auto_select"]["area_keyword_exclude"]
                        if len(area_keyword_exclude) > 0:
                            area_keyword_exclude_array = json.loads("["+ area_keyword_exclude +"]")
                            for exclude_item in area_keyword_exclude_array:
                                if exclude_item in row_text:
                                    row_text = ""

                    if row_text == "":
                        row_is_enabled=False

                if row_is_enabled:
                    formated_area_list.append(row)
        else:
            if show_debug_message:
                print("area_list_count is empty.")
            pass
    else:
        if show_debug_message:
            print("area_list_count is None.")
        pass

    if is_price_assign_by_bot:
        formated_area_list = None

    if formated_area_list is not None:
        area_list_count = len(formated_area_list)
        if show_debug_message:
            print("formated_area_list count:", area_list_count)

        if area_list_count > 0:
            matched_blocks = []
            if len(area_keyword_list) == 0:
                matched_blocks = formated_area_list
            else:
                # match keyword.
                row_index = 0
                for row in formated_area_list:
                    row_index += 1
                    row_is_enabled=True
                    if row_is_enabled:
                        row_text = ""
                        try:
                            row_text = row.text
                        except Exception as exc:
                            print("get text fail")
                            break

                        if row_text is None:
                            row_text = ""

                        if len(row_text) > 0:
                            row_text = format_keyword_string(row_text)
                            if show_debug_message:
                                print("row_text:", row_text)

                            is_match_area = False

                            if len(area_keyword_list) > 0:
                                # must match keyword.
                                is_match_area = True
                                area_keyword_array = area_keyword_list.split(' ')
                                for area_keyword in area_keyword_array:
                                    area_keyword = format_keyword_string(area_keyword)
                                    if not area_keyword in row_text:
                                        is_match_area = False
                                        break
                            else:
                                # without keyword.
                                is_match_area = True

                            if is_match_area:
                                matched_blocks.append(row)

            if show_debug_message:
                print("after match keyword, found count:", len(matched_blocks))

            if len(matched_blocks) == 0:
                matched_blocks = None
                is_need_refresh = True

    target_area = None
    if matched_blocks is not None:
        if len(matched_blocks) > 0:
            target_row_index = 0

            if area_auto_select_mode == CONST_FROM_TOP_TO_BOTTOM:
                pass

            if area_auto_select_mode == CONST_FROM_BOTTOM_TO_TOP:
                target_row_index = len(matched_blocks)-1

            if area_auto_select_mode == CONST_RANDOM:
                target_row_index = random.randint(0,len(matched_blocks)-1)

            target_area = matched_blocks[target_row_index]
        else:
            is_need_refresh = True
            if show_debug_message:
                print("matched_blocks is empty, is_need_refresh")

    if target_area is not None:
        try:
            if target_area.is_enabled():
                target_area.click()
                is_price_assign_by_bot = True
        except Exception as exc:
            print("click target_area link fail")
            print(exc)
            # use plan B
            try:
                print("force to click by js.")
                driver.execute_script("arguments[0].click();", target_area)
                is_price_assign_by_bot = True
            except Exception as exc:
                pass

    if is_price_assign_by_bot:
        ticket_number_div = None
        try:
            ticket_number_div = target_area.find_element(By.CSS_SELECTOR, 'div.count-button > div')
        except Exception as exc:
            print("find ticket_number_div fail")

        ticket_number = config_dict["ticket_number"]
        if not ticket_number_div is None:
            ticket_number_text = ""
            ticket_number_text_int = 0
            try:
                ticket_number_text = ticket_number_div.text
            except Exception as exc:
                print("get ticket_number_text fail")
                pass

            if ticket_number_text is None:
                ticket_number_text = ""
            if len(ticket_number_text) > 0:
                ticket_number_text_int = int(ticket_number_text)

                if show_debug_message:
                    print("ticket_number_text_int:", ticket_number_text_int)

                if ticket_number_text_int < ticket_number:
                    ticket_number_plus = None
                    try:
                        ticket_number_plus = target_area.find_element(By.CSS_SELECTOR, 'button > span > i.mdi-plus')
                    except Exception as exc:
                        print("find ticket_number_plus fail")

                    if not ticket_number_plus is None:
                        # add
                        add_count = ticket_number - ticket_number_text_int
                        if show_debug_message:
                            print("add_count:", add_count)
                        for i in range(add_count):
                            if show_debug_message:
                                print("click on plus button #",i)
                            try:
                                if ticket_number_plus.is_enabled():
                                    ticket_number_plus.click()
                                    time.sleep(0.1)
                            except Exception as exc:
                                pass

    return is_need_refresh, is_price_assign_by_bot

def ticketplus_order_expansion_panel(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    is_price_assign_by_bot = False
    is_need_refresh = False

    auto_fill_ticket_number = True
    if auto_fill_ticket_number:
        # click price row.
        area_keyword = config_dict["area_auto_select"]["area_keyword"].strip()
        if show_debug_message:
            print("area_keyword:", area_keyword)

        is_need_refresh = False

        if len(area_keyword) > 0:
            area_keyword_array = json.loads("["+ area_keyword +"]")
            for area_keyword_item in area_keyword_array:
                is_need_refresh, is_price_assign_by_bot = ticketplus_order_expansion_auto_select(driver, config_dict, area_keyword_item)
                if not is_need_refresh:
                    break
                else:
                    print("is_need_refresh for keyword:", area_keyword_item)
        else:
            # empty keyword, match all.
            is_need_refresh, is_price_assign_by_bot = ticketplus_order_expansion_auto_select(driver, config_dict, "")

        if is_need_refresh:
            try:
                driver.refresh()
            except Exception as exc:
                pass

    return is_price_assign_by_bot

def ticketplus_order(driver, config_dict, ocr, Captcha_Browser):
    next_step_button = None
    is_button_disabled = False
    try:
        my_css_selector = "div.order-footer > div.container > div.row > div > div.row > div > button.nextBtn"
        next_step_button = driver.find_element(By.CSS_SELECTOR, my_css_selector)
        if not next_step_button is None:
            if not next_step_button.is_enabled():
                is_button_disabled = True
    except Exception as exc:
        print("find next_step_button fail")
        print(exc)

    #print("is_button_disabled:", is_button_disabled)
    if is_button_disabled:
        is_price_assign_by_bot = ticketplus_order_expansion_panel(driver, config_dict)
        if is_price_assign_by_bot:
            if config_dict["ocr_captcha"]["enable"]:
                ticketplus_order_ocr(driver, config_dict, ocr, Captcha_Browser)
                pass

def ticketplus_order_ocr(driver, config_dict, ocr, Captcha_Browser):
    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False

    is_cpatcha_sent = False
    previous_answer = None
    for redo_ocr in range(999):
        is_need_redo_ocr, previous_answer, is_form_sumbited = ticketplus_auto_ocr(driver, config_dict, ocr, previous_answer, Captcha_Browser)

        # TODO: must ensure the answer is corrent...
        is_cpatcha_sent = True

        if is_form_sumbited:
            break

        if not away_from_keyboard_enable:
            break

        if not is_need_redo_ocr:
            break

def ticketplus_auto_ocr(driver, config_dict, ocr, previous_answer, Captcha_Browser):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ocr_captcha_image_source = config_dict["ocr_captcha"]["image_source"]
    away_from_keyboard_enable = config_dict["ocr_captcha"]["force_submit"]
    if not config_dict["ocr_captcha"]["enable"]:
        away_from_keyboard_enable = False

    print("start to ddddocr")

    is_need_redo_ocr = False
    is_form_sumbited = False

    ocr_answer = None

    # check ocr inputed.
    is_verifyCode_editing, is_form_sumbited = ticketplus_keyin_captcha_code(driver)
    
    is_do_ocr = False
    if not ocr is None:
        if not is_verifyCode_editing:
            is_do_ocr = True

    if is_do_ocr:
        if show_debug_message:
            print("away_from_keyboard_enable:", away_from_keyboard_enable)
            print("previous_answer:", previous_answer)
            print("ocr_captcha_image_source:", ocr_captcha_image_source)

        ocr_start_time = time.time()

        img_base64 = None
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_NON_BROWSER:
            if not Captcha_Browser is None:
                img_base64 = base64.b64decode(Captcha_Browser.Request_Captcha())
        if ocr_captcha_image_source == CONST_OCR_CAPTCH_IMAGE_SOURCE_CANVAS:
            image_id = 'span.captcha-img'
            try:
                form_verifyCode_base64 = driver.execute_async_script("""
function svgToPng(svg, callback) {
  const url = getSvgUrl(svg);
  svgUrlToPng(url, (imgData) => {
    callback(imgData);
    URL.revokeObjectURL(url);
  });
}
function getSvgUrl(svg) {
  return URL.createObjectURL(new Blob([svg], {
    type: 'image/svg+xml'
  }));
}
function svgUrlToPng(svgUrl, callback) {
  const svgImage = document.createElement('img');
  document.body.appendChild(svgImage);
  svgImage.onload = () => {
    const canvas = document.createElement('canvas');
    canvas.width = svgImage.clientWidth;
    canvas.height = svgImage.clientHeight;
    const canvasCtx = canvas.getContext('2d');
    canvasCtx.fillStyle = 'white';
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
    canvasCtx.drawImage(svgImage, 0, 0);
    const imgData = canvas.toDataURL('image/png');
    callback(imgData);
  };
  svgImage.src = svgUrl;
}
const img=document.querySelector('%s');
if(img!=null) {
const svg=img.innerHTML;
svgToPng(svg, (imgData) => {
  callback = arguments[arguments.length - 1];
  callback(imgData);
}); }
                    """ % (image_id))
                if not form_verifyCode_base64 is None:
                    img_base64 = base64.b64decode(form_verifyCode_base64.split(',')[1])
            except Exception as exc:
                if show_debug_message:
                    print("canvas exception:", str(exc))
                pass
        if not img_base64 is None:
            try:
                ocr_answer = ocr.classification(img_base64)
            except Exception as exc:
                pass

        ocr_done_time = time.time()
        ocr_elapsed_time = ocr_done_time - ocr_start_time
        print("ocr elapsed time:", "{:.3f}".format(ocr_elapsed_time))
    else:
        print("ddddocr is None")

    if not ocr_answer is None:
        ocr_answer = ocr_answer.strip()
        print("ocr_answer:", ocr_answer)
        if len(ocr_answer)==4:
            who_care_var, is_form_sumbited = ticketplus_keyin_captcha_code(driver, answer = ocr_answer, auto_submit = away_from_keyboard_enable)
        else:
            if not away_from_keyboard_enable:
                ticketplus_keyin_captcha_code(driver)
                #tixcraft_toast(driver, "※ OCR辨識失敗Q_Q，驗證碼請手動輸入...")
            else:
                is_need_redo_ocr = True
                if previous_answer != ocr_answer:
                    previous_answer = ocr_answer
                    print("refresh captcha...")
                    refresh_btn = None
                    try:
                        my_css_selector = 'i.v-icon.mdi.mdi-refresh'
                        refresh_btn = driver.find_element(By.CSS_SELECTOR, my_css_selector)
                        if not refresh_btn is None:
                            refresh_btn.click()
                            time.sleep(0.3)
                    except Exception as exc:
                        print("find refresh_btn fail")

    else:
        print("ocr_answer is None")
        print("previous_answer:", previous_answer)
        if previous_answer is None:
            is_verifyCode_editing, is_form_sumbited = ticketplus_keyin_captcha_code(driver)
        else:
            # page is not ready, retry again.
            # PS: usually occur in async script get captcha image.
            is_need_redo_ocr = True

    return is_need_redo_ocr, previous_answer, is_form_sumbited


def ticketplus_keyin_captcha_code(driver, answer = "", auto_submit = False):
    is_verifyCode_editing = False
    is_form_sumbited = False

    # manually keyin verify code.
    form_verifyCode = None
    try:
        my_css_selector = 'input[placeholder="請輸入驗證碼"]'
        form_verifyCode = driver.find_element(By.CSS_SELECTOR, my_css_selector)
    except Exception as exc:
        print("find captcha input fail")

    if form_verifyCode is not None:
        inputed_value = None
        try:
            inputed_value = form_verifyCode.get_attribute('value')
        except Exception as exc:
            print("find verify code fail")
            pass

        if inputed_value is None:
            inputed_value = ""

        if inputed_value == "請輸入驗證碼":
            try:
                form_verifyCode.clear()
            except Exception as exc:
                print("clear verify code fail")
                pass
        else:
            if len(inputed_value) > 0:
                print("captcha text inputed.")
                form_verifyCode = None
                is_verifyCode_editing = True

    if form_verifyCode is not None:
        if len(answer) > 0:
            answer=answer.upper()
            
            is_visible = False
            try:
                if form_verifyCode.is_enabled():
                    is_visible = True
            except Exception as exc:
                pass

            if is_visible:
                try:
                    form_verifyCode.click()
                    is_verifyCode_editing = True
                except Exception as exc:
                    pass

                try:
                    form_verifyCode.clear()
                    form_verifyCode.send_keys(answer)
                
                    if auto_submit:
                        form_verifyCode.send_keys(Keys.ENTER)
                        is_verifyCode_editing = False
                        is_form_sumbited = True
                    else:
                        print("select all captcha text")
                        driver.execute_script("arguments[0].select();", form_verifyCode)
                        if len(answer) > 0:
                            #tixcraft_toast(driver, "※ 按 Enter 如果答案是: " + answer)
                            pass
                except Exception as exc:
                    print("send_keys ocr answer fail.")

    return is_verifyCode_editing, is_form_sumbited

def ticketplus_main(driver, url, config_dict, ocr, Captcha_Browser):
    home_url_list = ['https://ticketplus.com.tw/']
    for each_url in home_url_list:
        if each_url == url.lower():
            if config_dict["ocr_captcha"]["enable"]:
                domain_name = url.split('/')[2]
                if not Captcha_Browser is None:
                    Captcha_Browser.Set_cookies(driver.get_cookies())
                    Captcha_Browser.Set_Domain(domain_name)
            break

    # https://ticketplus.com.tw/activity/XXX
    if '/activity/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==5:
            is_event_page = True

        if is_event_page:
            if config_dict["tixcraft"]["date_auto_select"]["enable"]:
                ticketplus_date_auto_select(driver, config_dict)

    #https://ticketplus.com.tw/order/XXX/OOO
    if '/order/' in url.lower():
        is_event_page = False
        if len(url.split('/'))==6:
            is_event_page = True

        if is_event_page:
            ticketplus_order(driver, config_dict, ocr, Captcha_Browser)


def main(args):
    config_dict = get_config_dict(args)

    driver = None
    if not config_dict is None:
        for i in range(50):
            driver = get_driver_by_config(config_dict)
            if not driver is None:
                break
            else:
                time.sleep(0.05)
    else:
        print("Load config error!")

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""
    last_url = ""

    # for tixcraft
    tixcraft_dict = {}
    tixcraft_dict["answer_index"]=-1
    tixcraft_dict["is_popup_checkout"] = False

    # for kktix
    kktix_dict = {}
    kktix_dict["answer_index"]=-1
    kktix_dict["kktix_register_status_last"] = None
    kktix_dict["is_popup_checkout"] = False

    ibon_dict = {}
    ibon_dict["answer_index"]=-1

    hkticketing_dict = {}
    hkticketing_dict["is_date_submiting"] = False

    ocr = None
    Captcha_Browser = None
    try:
        if config_dict["ocr_captcha"]["enable"]:
            ocr_beta_mode = True
            if "ticketplus" in config_dict["homepage"]:
                #ocr_beta_mode = False
                pass
            ocr = ddddocr.DdddOcr(show_ad=False, beta=ocr_beta_mode)
            Captcha_Browser = NonBrowser()

            if len(config_dict["advanced"]["tixcraft_sid"]) > 1:
                set_non_browser_cookies(driver, config_dict["homepage"], Captcha_Browser)
    except Exception as exc:
        print(exc)
        pass

    DISCONNECTED_MSG = ': target window already closed'

    while True:
        time.sleep(0.05)

        is_alert_popup = False

        # pass if driver not loaded.
        if driver is None:
            print("web driver not accessible!")
            break

        #is_alert_popup = check_pop_alert(driver)

        #MUST "do nothing: if alert popup.
        #print("is_alert_popup:", is_alert_popup)
        if is_alert_popup:
            continue

        url = ""
        try:
            url = driver.current_url
        except NoSuchWindowException:
            print('NoSuchWindowException at this url:', url )
            #print("last_url:", last_url)
            #print("get_log:", driver.get_log('driver'))
            window_handles_count = 0
            try:
                window_handles_count = len(driver.window_handles)
                #print("window_handles_count:", window_handles_count)
                if window_handles_count >= 1:
                    driver.switch_to.window(driver.window_handles[0])
                    driver.switch_to.default_content()
                    time.sleep(0.2)
            except Exception as excSwithFail:
                #print("excSwithFail:", excSwithFail)
                pass
            if window_handles_count==0:
                try:
                    driver_log = driver.get_log('driver')[-1]['message']
                    print("get_log:", driver_log)
                    if DISCONNECTED_MSG in driver_log:
                        print('quit bot by NoSuchWindowException')
                        driver.quit()
                        sys.exit()
                        break
                except Exception as excGetDriverMessageFail:
                    #print("excGetDriverMessageFail:", excGetDriverMessageFail)
                    except_string = str(excGetDriverMessageFail)
                    if 'HTTP method not allowed' in except_string:
                        print('quit bot by close browser')
                        driver.quit()
                        sys.exit()
                        break

        except UnexpectedAlertPresentException as exc1:
            print('UnexpectedAlertPresentException at this url:', url )
            # PS: do nothing...
            # PS: current chrome-driver + chrome call current_url cause alert/prompt dialog disappear!
            # raise exception at selenium/webdriver/remote/errorhandler.py
            # after dialog disappear new excpetion: unhandled inspector error: Not attached to an active page
            is_pass_alert = False
            is_pass_alert = True
            if is_pass_alert:
                try:
                    driver.switch_to.alert.accept()
                except Exception as exc:
                    pass

        except Exception as exc:
            logger.error('Maxbot URL Exception')
            logger.error(exc, exc_info=True)

            #UnicodeEncodeError: 'ascii' codec can't encode characters in position 63-72: ordinal not in range(128)
            str_exc = ""
            try:
                str_exc = str(exc)
            except Exception as exc2:
                pass

            if len(str_exc)==0:
                str_exc = repr(exc)

            exit_bot_error_strings = ['Max retries exceeded'
            , 'chrome not reachable'
            , 'unable to connect to renderer'
            , 'failed to check if window was closed'
            , 'Failed to establish a new connection'
            , 'Connection refused'
            , 'disconnected'
            , 'without establishing a connection'
            , 'web view not found'
            , 'invalid session id'
            ]
            for each_error_string in exit_bot_error_strings:
                if isinstance(str_exc, str):
                    if each_error_string in str_exc:
                        print('quit bot by error:', each_error_string)
                        driver.quit()
                        sys.exit()
                        break

            # not is above case, print exception.
            print("Exception:", str_exc)
            pass

        if url is None:
            continue
        else:
            if len(url) == 0:
                continue

        # 說明：輸出目前網址，覺得吵的話，請註解掉這行。
        #print("url:", url)

        if len(url) > 0 :
            if url != last_url:
                print(url)
                write_last_url_to_file(url)
                if os.path.exists(CONST_MAXBOT_INT28_FILE):
                    print("MAXBOT Paused.")
            last_url = url

        if os.path.exists(CONST_MAXBOT_INT28_FILE):
            time.sleep(0.2)
            continue

        tixcraft_family = False
        if 'tixcraft.com' in url:
            tixcraft_family = True

        if 'indievox.com' in url:
            tixcraft_family = True

        if 'ticketmaster.' in url:
            tixcraft_family = True

        if tixcraft_family:
            tixcraft_dict = tixcraft_main(driver, url, config_dict, tixcraft_dict, ocr, Captcha_Browser)

        # for kktix.cc and kktix.com
        if 'kktix.c' in url:
            kktix_dict = kktix_main(driver, url, config_dict, kktix_dict)

        if 'famiticket.com' in url:
            famiticket_main(driver, url, config_dict)

        if 'ibon.com' in url:
            ibon_dict = ibon_main(driver, url, config_dict, ibon_dict, ocr, Captcha_Browser)

        kham_family = False
        if 'kham.com.tw' in url:
            kham_family = True

        if 'ticket.com.tw' in url:
            kham_family = True

        if kham_family:
            kham_main(driver, url, config_dict, ocr, Captcha_Browser)

        if 'ticketplus.com' in url:
            ticketplus_main(driver, url, config_dict, ocr, Captcha_Browser)

        if 'urbtix.hk' in url:
            urbtix_main(driver, url, config_dict)

        if 'cityline.com' in url:
            cityline_main(driver, url, config_dict)

        if 'hkticketing.com' in url:
            hkticketing_dict = hkticketing_main(driver, url, config_dict, hkticketing_dict)

        if 'galaxymacau.com' in url:
            hkticketing_dict = hkticketing_main(driver, url, config_dict, hkticketing_dict)

        # for facebook
        facebook_login_url = 'https://www.facebook.com/login.php?'
        if url[:len(facebook_login_url)]==facebook_login_url:
            facebook_account = config_dict["advanced"]["facebook_account"].strip()
            if len(facebook_account) > 4:
                facebook_login(driver, facebook_account, decryptMe(config_dict["advanced"]["facebook_password"]))

def cli():
    parser = argparse.ArgumentParser(
            description="resize image to new width")

    parser.add_argument("--input",
        help="config file path",
        type=str)

    parser.add_argument("--homepage",
        help="overwrite homepage setting",
        type=str)

    parser.add_argument("--ticket_number",
        help="overwrite ticket_number setting",
        type=int)

    parser.add_argument("--tixcraft_sid",
        help="overwrite tixcraft sid field",
        type=str)

    parser.add_argument("--kktix_account",
        help="overwrite kktix_account field",
        type=str)

    parser.add_argument("--kktix_password",
        help="overwrite kktix_password field",
        type=str)

    parser.add_argument("--ibonqware",
        help="overwrite ibonqware field",
        type=str)

    parser.add_argument("--headless",
        help="headless mode",
        default='False',
        type=str)

    parser.add_argument("--browser",
        help="overwrite browser setting",
        default='',
        choices=['chrome','firefox','edge','safari'],
        type=str)

    args = parser.parse_args()
    main(args)

if __name__ == "__main__":
    CONST_MODE_GUI = 0
    CONST_MODE_CLI = 1
    mode = CONST_MODE_GUI
    #mode = CONST_MODE_CLI

    if mode == CONST_MODE_GUI:
        cli()
    else:
        #for test kktix infer answer.
        captcha_text_div_text = u"請回答下列問題,請在下方空格輸入DELIGHT（請以半形輸入法作答，大小寫需要一模一樣）"
        #captcha_text_div_text = u"請在下方空白處輸入引號內文字：「abc」"
        #captcha_text_div_text = u"請在下方空白處輸入引號內文字：「0118eveconcert」（請以半形小寫作答。）"
        #captcha_text_div_text = "在《DEEP AWAKENING見過深淵的人》專輯中，哪一首為合唱曲目？ 【V6】深淵 、【Z5】浮木、【J8】無聲、【C1】以上皆非 （請以半形輸入法作答，大小寫/阿拉伯數字需要一模一樣，範例：A2）"
        #captcha_text_div_text = "Super Junior 的隊長是以下哪位?  【v】神童 【w】藝聲 【x】利特 【y】始源  若你覺得答案為 a，請輸入 a  (英文為半形小寫)"
        #captcha_text_div_text = "請問XXX, 請以英文為半形小寫(例如：a) a. 1月5日 b. 2月5日 c. 3月5日 d. 4月5日"
        #captcha_text_div_text = "以下為選擇題：請問 「OHM NANON 1st Fan Meeting in Hong Kong」 舉行日期是？請以半形細楷英文於下方輸入答案 (例如：a)  a. 1月5日 b. 2月5日 c. 3月5日 d. 4月5日"
        #captcha_text_div_text = "以下哪個「不是」正確的林俊傑與其他藝人合唱的歌曲組合？（選項為歌名/合作藝人 ，請以半形輸入法作答選項，大小寫需要一模一樣，範例:jju） 選項： (jja)小酒窩/A-Sa蔡卓妍 (jjb)被風吹過的夏天/金莎 (jjc)友人說/張懷秋 (jjd)全面開戰/五月天阿信 (jje)小說/阿杜"
        #captcha_text_div_text = "請問《龍的傳人2060》演唱會是以下哪位藝人的演出？（請以半形輸入法作答，大小寫需要一模一樣，範例：B2）A1.周杰倫 B2.林俊傑 C3.張學友 D4.王力宏"
        #captcha_text_div_text = "王力宏何時發行第一張專輯?（請以半形輸入法作答，大小寫需要一模一樣，範例:B2） A1.1985 B2.2005 C3.2015 D4.1995"
        #captcha_text_div_text = "朴寶劍三月以歌手出道的日期和單曲名為？ Answer the single’s name & the debut date. *以半形輸入，大小寫/符號須都相同。例:(E1) Please use the same format given in the options.ex:(E1) (A1)20/Bloomin'(B1)2/Blossom(C1)2/Bloomin'(D1)20/Blossom"
        #captcha_text_div_text = "以下哪位不是LOVELYZ成員? (請以半形輸入選項內的英文及數字，大小寫須符合)，範例:E5e。 (A1a)智愛 (B2b)美珠 (C3c)JON (D4d)叡仁"
        #captcha_text_div_text = "題請問此次 RAVI的SOLO專輯名稱為?（請以半形輸入法作答，大小寫需要一模一樣，範例:Tt） Aa [ BOOK] 、 Bb [OOK BOOK.R] 、 Cc [R.OOK BOOK] 、 Dd [OOK R. BOOK]"
        #captcha_text_div_text = "請問下列哪個選項皆為河成雲的創作歌曲？ Aa) Don’t Forget、Candle Bb) Don’t Forget、Forever+1 Cc) Don’t Forget、Flowerbomb Dd) Don’t Forget、One Love 請以半形輸入，大小寫含括號需一模一樣 【範例:答案為B需填入Bb)】"
        #captcha_text_div_text = "魏如萱得過什麼獎?(1) 金馬獎 最佳女主角(2) 金鐘獎 戲劇節目女主角(3) 金曲獎 最佳華語女歌手(4) 走鐘獎 好好聽音樂獎 (請輸入半形數字)"
        #captcha_text_div_text = "Love in the Air 是由哪兩本小說改篇而成呢？(A)Love Strom & Love Sky (B)Love Rain & Love Cloud (C)Love Wind & Love Sun (D)Love Dry & Love Cold (請輸入選項大寫英文單字 範例：E)"
        #captcha_text_div_text = "請問以下哪一部戲劇是Off Gun合作出演的戲劇？【1G】Midnight Museum 【2F】10 Years Ticket 【8B】Not Me (請以半形輸入法作答，大小寫/阿拉伯數字需要一模一樣，範例：9A)"
        #captcha_text_div_text = "請將以下【歌曲】已發行日期由「新到舊」依序排列 【H1】 After LIKE 【22】 I AM 【R3】 ELEVEN 【74】LOVE DIVE 請以半形輸入法輸入正確答案之\"選項\"，大小寫/阿拉伯數字需要一模一樣，範例：A142X384"
        #captcha_text_div_text = "請將以下【歌曲】已發行日期由「新到舊」依序排列 【H】 After LIKE 【2】 I AM 【R】 ELEVEN 【7】LOVE DIVE 請以半形輸入法輸入正確答案之\"選項\"，大小寫/阿拉伯數字需要一模一樣，範例：A4X8"
        captcha_text_div_text = "1. 以下哪個為正確的OffGun粉絲名稱？（請以半形數字及細楷英文字母於下方輸入答案）\n3f）Baby\n6r）Babii\n9e）Babe"
        #captcha_text_div_text = "2. 以下那齣並不是OffGun有份演出的劇集？（請以半形數字及細楷英文字母於下方輸入答案）\n2m）《我的貓貓男友》\n4v）《愛情理論》\n6k）《Not Me》"
        #captcha_text_div_text = "2. 以下那齣並不是OffGun有份演出的劇集？（請以半形數字及細楷英文字母於下方輸入答案）\n2m:《我的貓貓男友》\n4v:《愛情理論》\n6k:《Not Me》"
        inferred_answer_string, answer_list = get_answer_list_from_question_string(None, captcha_text_div_text)
        print("inferred_answer_string:", inferred_answer_string)
        print("answer_list:", answer_list)

        ocr = ddddocr.DdddOcr(show_ad=False, beta=True)
        image_file = 'captcha-xxxx.png'
        if os.path.exists(image_file):
            with open(image_file, 'rb') as f:
                image_bytes = f.read()
            res = ocr.classification(image_bytes)
            print(res)

        # for urbtix survey.
        question_text = "「6- -V- -U - n--s- -z - j」由右起第三個數字/字母是甚麼?"
        question_text = "「6---2 - 3 _ 8- -8 _ 4 - 1--4 _ 7」中有多少個「二」?"
        question_answer_char, question_direction = get_urbtix_survey_answer_by_question(question_text)
        print("question_text:", question_text)
        print("question_answer_char:", question_answer_char)
        print("question_text:", question_direction)

