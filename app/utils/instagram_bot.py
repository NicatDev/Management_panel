import os
import pickle
import time
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from django.conf import settings


from account.models import Instagram
CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver"



class InstagramBOT(webdriver.Chrome):
    def __init__(self, driver_path=CHROME_DRIVER_PATH):
        options = webdriver.ChromeOptions()
        # options.add_argument(f'--proxy-server=91.246.192.17:6018')

        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--disable-blink-features")

        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument("disable-infobars")  # disabling infobars
        options.add_argument("--disable-extensions")  # disabling extensions
        options.add_argument("--disable-gpu")  # applicable to windows os only

        options.add_argument("start-maximized")
        # overcome limited resource problems
        options.add_argument("--disable-dev-shm-usage")
        # Bypass OS security model
        options.add_argument("--no-sandbox")
        # options.add_argument(f"user-data-dir=./chromeprofiles/chromeprofile{account_id}")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--start-maximized")
        # options.add_argument(f'user-agent={ua.random}')
        options.add_experimental_option(

            "excludeSwitches",
            ["enable-automation"]
        )
        options.add_experimental_option('useAutomationExtension', False)

        super(InstagramBOT, self).__init__(
            executable_path=driver_path,
            options=options,
        )

        # self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #     "source": """
        #         const newProto = navigator.__proto__
        #         delete newProto.webdriver
        #         navigator.__proto__ = newProto
        #         """
        # })

        stealth(self,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.quit()

    def open_page(self, url: str = 'https://www.instagram.com/?hl=en'):
        return self.get(url)

    def bypass_authorization(self, login: str, password: str):
        """
            Login on INSTAGRAM
        """
        # _______CHECK FOR COOKIE SELECT
        try:

            driver_wait = WebDriverWait(self, 10)
            accept_cookies_button_xpath = '//button[text()="Turn On"]'

            accept_cookies_modal = driver_wait.until(

                EC.presence_of_element_located(
                    (By.XPATH, accept_cookies_button_xpath)
                )
            )

            if accept_cookies_modal:
                accept_cookies_button = self.find_element(
                    By.XPATH, accept_cookies_button_xpath
                )

                accept_cookies_button.click()

        except:
            pass

        try:

            driver_wait = WebDriverWait(self, 10)
            accept_cookies_button_xpath = '//button[text()="Allow essential and optional cookies"]'

            accept_cookies_modal = driver_wait.until(

                EC.presence_of_element_located(
                    (By.XPATH, accept_cookies_button_xpath)
                )
            )

            if accept_cookies_modal:
                accept_cookies_button = self.find_element(
                    By.XPATH, accept_cookies_button_xpath
                )

                accept_cookies_button.click()

        except:
            pass

        # _____________

        try:

            driver_wait = WebDriverWait(self, 10)
            _ = driver_wait.until(

                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[type="submit"]')
                )
            )

            login_input = self.find_element(
                By.CSS_SELECTOR,
                'input[aria-label="Phone number, username, or email"]',
            )
            password_input = self.find_element(
                By.CSS_SELECTOR,
                'input[aria-label="Password"]',
            )

            login_input.send_keys(login)
            sleep(1)
            password_input.send_keys(password)
            sleep(1)
            submit_button = self.find_element(By.CSS_SELECTOR,
                                              'button[type="submit"]')
            _ = driver_wait.until(

                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[type="submit"]')
                )
            )

            submit_button.click()
        except:pass

    def new_post(self,
                 filepath: str = None,
                 cover_filepath=None,
                 frame_mode: int = 1,
                 text: str = None,
                 ):
        # _______CHECK FOR COOKIE SELECT
        try:

            driver_wait = WebDriverWait(self, 10)
            accept_cookies_button_xpath = '//button[text()="Allow essential and optional cookies"]'

            accept_cookies_modal = driver_wait.until(

                EC.presence_of_element_located(
                    (By.XPATH, accept_cookies_button_xpath)
                )
            )

            if accept_cookies_modal:
                accept_cookies_button = self.find_element(
                    By.XPATH, accept_cookies_button_xpath
                )

                accept_cookies_button.click()

        except:
            pass

        try:

            driver_wait = WebDriverWait(self, 10)
            accept_cookies_button_xpath = '//button[text()="Turn On"]'

            accept_cookies_modal = driver_wait.until(

                EC.presence_of_element_located(
                    (By.XPATH, accept_cookies_button_xpath)
                )
            )

            if accept_cookies_modal:
                accept_cookies_button = self.find_element(
                    By.XPATH, accept_cookies_button_xpath
                )

                accept_cookies_button.click()

        except:
            pass

        # _____________

        driver_wait = WebDriverWait(self, 120)
        _ = driver_wait.until(

            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'svg[aria-label="New post"]')
            )
        )

        new_post_button = self.find_element(
            By.CSS_SELECTOR, 'svg[aria-label="New post"]'
        )
        new_post_button.click()
        # ________________________________
        _ = driver_wait.until(

            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[type="file"]')
            )
        )

        upload_file = self.find_element(
            By.CSS_SELECTOR, 'input[type="file"]'
        )

        upload_file.send_keys(filepath)
        # _______________________________________

        try:
            info_modal_text = '//span[text()="Video posts are now shared as reels"]'
            _ = driver_wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, info_modal_text)
                )
            )
            info_modal = self.find_element(By.XPATH, info_modal_text)
            accept_info_button = self.find_element(By.XPATH, '//button[text()="OK"]')
            accept_info_button.click()
            sleep(3)
        except:pass


        _ = driver_wait.until(

            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'svg[aria-label="Select crop"]')
            )
        )

        frame_size_select_button = self.find_element(
            By.CSS_SELECTOR, 'svg[aria-label="Select crop"]'
        )

        frame_size_select_button.click()
        # _______________________________________

        FRAMES_MODE_XPATH = {
            1: '//div[text()="Original"]',
            2: '//div[text()="1:1"]',
            3: '//div[text()="9:16"]',
            4: '//div[text()="16:9"]',
        }

        original = self.find_element(
            By.XPATH, FRAMES_MODE_XPATH.get(frame_mode)
        )

        if original:
            original.click()

        sleep(10)
        # _______________________________________
        next_button_xpath = '//div[text()="Next"]'

        _ = driver_wait.until(

            EC.element_to_be_clickable(
                (By.XPATH, next_button_xpath)
            )
        )

        next_button = self.find_element(
            By.XPATH, next_button_xpath
        )

        next_button.click()

        # _______________________________________
        if cover_filepath:
            _ = driver_wait.until(

                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[type="file"]')
                )
            )

            upload_file = self.find_element(
                By.CSS_SELECTOR, 'input[type="file"]'
            )

            upload_file.send_keys(cover_filepath)
            sleep(10)

        # _______________________________________

        next_button_xpath = '//div[text()="Next"]'

        _ = driver_wait.until(

            EC.element_to_be_clickable(
                (By.XPATH, next_button_xpath)
            )
        )

        next_button = self.find_element(
            By.XPATH, next_button_xpath
        )

        next_button.click()

        # _______________________________________

        # Write a caption...

        _ = driver_wait.until(

            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[aria-label="Write a caption..."]')
            )
        )

        frame_size_select_button = self.find_element(
            By.CSS_SELECTOR, 'div[aria-label="Write a caption..."]'
        )
        if text:
            frame_size_select_button.send_keys(text)

        sleep(2)

        # _______________________________________

        share_button_xpath = '//div[text()="Share"]'

        _ = driver_wait.until(

            EC.element_to_be_clickable(
                (By.XPATH, share_button_xpath)
            )
        )

        share_button = self.find_element(
            By.XPATH, share_button_xpath
        )

        share_button.click()

        # _______________________________________

        # CHECK DONE  Animated checkmark
        driver_wait = WebDriverWait(self, 1800)

        check = driver_wait.until(

            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'img[alt="Animated checkmark"]')
            )
        )

        if check:
            print(check, ' ok')
            return True
        else:
            return False
