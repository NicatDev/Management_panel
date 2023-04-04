import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os
from workspace.models import Status
from instagrapi import Client
from PIL import Image


from account.models import Instagram


def initial_driver():
    # configure the webdriver to use a specific browser
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument("--disable-dev-shm-usage")
    ser = Service(executable_path="/usr/local/bin/chromedriver")
    return webdriver.Chrome(options=options, service=ser)


def check_account(account, instagram_id):
    driver = initial_driver()
    cookies_path = os.path.join(os.path.abspath(f'{__file__}/../../'), 'cookies')
    instagram = Instagram.objects.get(id=instagram_id)
    status = Status.objects.get(name='2FA activation')
    driver.get("https://www.instagram.com")
    time.sleep(3)
    # Enter the username and password
    username = driver.find_element(By.NAME, "username")
    username.send_keys(instagram.username)

    password = driver.find_element(By.NAME, "password")
    password.send_keys(instagram.password)

    # Submit the form to log in
    password.send_keys(Keys.RETURN)

    # Wait for the 2FA prompt to appear
    try:
        print('2FA -a girdi =================================================')
        time.sleep(5)
        two_factor_prompt = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "verificationCode"))
        )
        if two_factor_prompt:
            instagram.status = status
            instagram.save()
            control = True
            while control:
                instagram.refresh_from_db()
                print(instagram.twoFACode)
                if instagram.twoFACode:
                    two_factor_prompt.send_keys(instagram.twoFACode)
                    two_factor_prompt.send_keys(Keys.RETURN)
                    control = False
                else:
                    time.sleep(5)
                    print('bir padxod getdi ==============================================')
                    continue
    except:
        print('no 2FA ========================================================')
        print(status, 'status =================================================')

    # No 2FA prompt appeared, continue with the script
    time.sleep(8)
    save_info = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[text()='Save Info']"))
    )
    save_info.click()
    time.sleep(2)

    # Save the cookies
    if not os.path.exists(f"{cookies_path}/{account.id}"):
        os.makedirs(f"{cookies_path}/{account.id}")
    with open(f"{cookies_path}/{account.id}/cookies.pkl", "wb") as f:
        json.dump(driver.get_cookies(), f)
    print('yoxladi ===============================================================')


def publish_image(account, task):
    task.status = task.status.next_step
    task.save()
    client = Client()
    instagram = account.instagram.first()
    client.login(username=instagram.username, password=instagram.password)
    upload_files_path = os.path.join(os.path.abspath(f'{__file__}/../../'), 'media')
    file_name = task.files.first().file.name
    client.photo_upload(
        f"{upload_files_path}/{file_name}",
        task.text,
    )
    print('media paylasildii ========================================================')



# def share_post(account, task):
#     driver = initial_driver()
#     # delete the current cookies
#     driver.delete_all_cookies()
#
#     import Xlib.display
#     import pyautogui
#     pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ['DISPLAY'])
#
#     instagram = account.instagram.first()
#     upload_files_path = os.path.join(os.path.abspath(f'{__file__}/../../'), f'media/files/task/{task.id}')
#     cookies_path = os.path.join(os.path.abspath(f'{__file__}/../../'), 'cookies')
#     print('instagram username ===============================', instagram.username)
#     # Try to load the cookies for the account
#     # with open(f"{cookies_path}/{account.id}/cookies.pkl", "rb") as f:
#     #     cookies = pickle.load(f)
#     #     for cookie in cookies:
#     #         driver.add_cookie(cookie)
#     # Navigate to the homepage to check if the session is still valid
#     driver.get("https://www.instagram.com/accounts/login/")
#     time.sleep(6)
#     username = driver.find_element(By.NAME, "username")
#     username.send_keys(instagram.username)
#
#     password = driver.find_element(By.NAME, "password")
#     password.send_keys(instagram.password)
#
#     # Submit the form to log in
#     password.send_keys(Keys.RETURN)
#     time.sleep(1)
#     driver.save_screenshot('login_olub.png')
#     # Loading the image
#     image = Image.open("login_olub.png")
#
#     # Showing the image
#     image.show()
#     try:
#         save_info = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//button[text()='Save Info']"))
#         )
#         save_info.click()
#         time.sleep(2)
#     except:
#         time.sleep(2)
#     driver.save_screenshot('error.png')
#     image2 = Image.open("error.png")
#
#     # Showing the image
#     image2.show()
#     # navigate to the upload page
#     driver.find_element(By.XPATH, "//*[@aria-label='New post']").click()
#     # wait for the upload page to load
#     time.sleep(5)
#     driver.find_element(By.XPATH, "//button[text()='Select from computer']").click()
#
#     for index, upload_file in enumerate(os.listdir(upload_files_path)):
#         time.sleep(3)
#         pyautogui.typewrite(f'{upload_files_path}/{upload_file}')
#         time.sleep(3)
#         pyautogui.press('enter')
#         if index + 1 != len(os.listdir(upload_files_path)):
#             time.sleep(3)
#             driver.find_element(By.XPATH, "//*[@aria-label='Open media gallery']").click()
#             driver.find_element(By.XPATH, "//*[@aria-label='Plus icon']").click()
#     time.sleep(3)
#     driver.find_element(By.XPATH, "//button[text()='Next']").click()
#     time.sleep(2)
#     driver.find_element(By.XPATH, "//button[text()='Next']").click()
#     time.sleep(2)
#     # driver.find_element(By.XPATH, "//textarea[contains(@aria-label, 'Write a caption...)]").send_keys ("Demo Caption")
#     driver.find_element(By.XPATH, "//button[text()='Share']").click()
#     time.sleep(2)
#     WebDriverWait(driver, 30).until(EC.text_to_be_present_in_element((By.XPATH, "//div[text()='Post shared']"), "Post shared"))
#     driver.find_element(By.XPATH, "//*[@aria-label='Close']").click()
#     driver.refresh()
#
#     # find the file input and enter the path to the image or video you want to share
#     # file_input = driver.find_element(By.XPATH, "//input[@type='file']")
#     # file_input.send_keys("http://75.119.147.165:85/media/books/images/Untitlwwqed-5547889ee1.png")
#
#     # wait for the upload process to finish
#     time.sleep(30)
#
#     # add a caption and share the post
#     caption_input = driver.find_element(By.XPATH, "//textarea[@aria-label='Write a caption…']")
#     caption_input.send_keys("Your caption goes here")
#     share_button = driver.find_element(By.XPATH, "//button[text()='Share']")
#     share_button.click()
#
#     # wait for the post to be shared
#     time.sleep(10)
#
#     # close the browser window
#     driver.quit()


# account = 'qelenderovisa'
# upload_files_path = os.path.join(os.path.abspath(f'{__file__}/../../'), 'media/files')
# cookies_path = os.path.join(os.path.abspath(f'{__file__}/../../'), 'cookies')
# print(cookies_path)
# # Try to load the cookies for the account
# try:
#     with open(f"{cookies_path}/{account}/cookies.pkl", "rb") as f:
#         cookies = pickle.load(f)
#         for cookie in cookies:
#             driver.add_cookie(cookie)
#
#     # Navigate to the homepage to check if the session is still valid
#     driver.get("https://www.instagram.com/")
# except:
#     driver.get("https://www.instagram.com/accounts/login/")
#     time.sleep(3)
#     # Enter the username and password
#     username = driver.find_element(By.NAME, "username")
#     username.send_keys("planlayici2022")
#
#     password = driver.find_element(By.NAME, "password")
#     password.send_keys("planlayici2022&&")
#
#     # Submit the form to log in
#     password.send_keys(Keys.RETURN)
#
#     # Wait for the 2FA prompt to appear
#     try:
#         two_factor_prompt = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.NAME, "verificationCode"))
#         )
#
#         # Enter the 2FA code
#         two_factor_code = input("Enter the 2FA code: ")
#         two_factor_prompt.send_keys(two_factor_code)
#
#         # Submit the 2FA code
#         # driver.find_element(By.XPATH, "//button[text()='Confirm']").click()
#         two_factor_prompt.send_keys(Keys.RETURN)
#
#         save_info = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//button[text()='Save Info']"))
#         )
#         save_info.click()
#         time.sleep(2)
#         # Save the cookies
#         if not os.path.exists(f"{cookies_path}/{account}"):
#             os.makedirs(f"{cookies_path}/{account}")
#         with open(f"{cookies_path}/{account}/cookies.pkl", "wb") as f:
#             pickle.dump(driver.get_cookies(), f)
#     except:
#         # No 2FA prompt appeared, continue with the script
#         save_info = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//button[text()='Save Info']"))
#         )
#         save_info.click()
#         time.sleep(2)
#         # Save the cookies
#         if not os.path.exists(f"{cookies_path}/{account}"):
#             os.makedirs(f"{cookies_path}/{account}")
#         with open(f"{cookies_path}/{account}/cookies.pkl", "wb") as f:
#             pickle.dump(driver.get_cookies(), f)
# time.sleep(3)
# # navigate to the upload page
# driver.find_element(By.XPATH, "//*[@aria-label='New post']").click()
# # wait for the upload page to load
# time.sleep(5)
# driver.find_element(By.XPATH, "//button[text()='Select from computer']").click()
#
# for index, upload_file in enumerate(os.listdir(upload_files_path)):
#     time.sleep(3)
#     pyautogui.typewrite(f'{upload_files_path}/{upload_file}')
#     time.sleep(3)
#     pyautogui.press('enter')
#     if index + 1 != len(os.listdir(upload_files_path)):
#         time.sleep(3)
#         driver.find_element(By.XPATH, "//*[@aria-label='Open media gallery']").click()
#         driver.find_element(By.XPATH, "//*[@aria-label='Plus icon']").click()
# time.sleep(3)
# driver.find_element(By.XPATH, "//button[text()='Next']").click()
# time.sleep(2)
# driver.find_element(By.XPATH, "//button[text()='Next']").click()
# time.sleep(2)
# # driver.find_element(By.XPATH, "//textarea[contains(@aria-label, 'Write a caption...)]").send_keys ("Demo Caption")
# driver.find_element(By.XPATH, "//button[text()='Share']").click()
# time.sleep(2)
# WebDriverWait(driver, 30).until(EC.text_to_be_present_in_element((By.XPATH, "//div[text()='Post shared']"), "Post shared"))
# driver.find_element(By.XPATH, "//*[@aria-label='Close']").click()
# driver.refresh()
#
# # find the file input and enter the path to the image or video you want to share
# # file_input = driver.find_element(By.XPATH, "//input[@type='file']")
# # file_input.send_keys("http://75.119.147.165:85/media/books/images/Untitlwwqed-5547889ee1.png")
#
# # wait for the upload process to finish
# time.sleep(30)
#
# # add a caption and share the post
# caption_input = driver.find_element(By.XPATH, "//textarea[@aria-label='Write a caption…']")
# caption_input.send_keys("Your caption goes here")
# share_button = driver.find_element(By.XPATH, "//button[text()='Share']")
# share_button.click()
#
#
# # http://75.119.147.165:85/media/books/images/Untitlwwqed-efghjhjee1.png
# # wait for the post to be shared
# time.sleep(10)
#
# # close the browser window
# driver.quit()
