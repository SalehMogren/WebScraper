# Import necessary packages
import os
import random
import string
from io import BytesIO
from itertools import zip_longest
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup

# from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1024,768")
chrome_options.add_argument("--no-sandbox")


def haraj_scrapper(
    query: str, folder_location: str, POSTS_LIMIT: int = 100, city: str = "الرياض"
):
    search = "تمر سكري مفتل"  # search whatever you want
    query.replace(" ", "%20")
    # url=f"https://haraj.com.sa/search/{search.split(' ')[0]}%20{search.split(' ')[1]}%20{search.split(' ')[2]}"
    browser = webdriver.Chrome(chrome_options=chrome_options)
    url = f"https://haraj.com.sa/search/{query}/city/{city}"

    """
    url="https://haraj.com.sa/search/تمر%20سكري%20مفتل" 
    """

    """ downloading the main page """
    # browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.implicitly_wait(5)
    browser.get(url)
    sleep(5)
    bottom = browser.find_element(by=By.XPATH, value="//div[@class='footer_wrapper']")
    body = browser.find_element(By.TAG_NAME, "body")

    btn = browser.find_element(
        by=By.XPATH, value="//button[@data-testid='posts-load-more']"
    )
    btn.click()

    posts_num = 0

    """ going to bottom and pressing read more to view all the posts """
    while (
        posts_num < POSTS_LIMIT
    ):  # change to how many posts you want (chose a number that is a multiple of 20 )
        # scroll to the bottom of the page
        for i in range(5):
            body.send_keys(Keys.PAGE_DOWN)
            # add some delay to allow the page to load
            sleep(1)

        bottom.click()
        try:
            btn = browser.find_element(by=By.XPATH, value="//button[@id='more']")
            btn.click()
        except:
            bottom.click()
        posts_num += 20

    """
    now we start scraping posts, links and images

    """

    innerHTML = browser.execute_script("return document.body.innerHTML")

    # soup = BeautifulSoup(innerHTML, "lxml")

    posts = browser.find_elements(
        by=By.XPATH, value="//a[@data-testid='post-title-link']"
    )
    links = []
    images = []
    data = []

    for post in posts:
        link = post.get_attribute("href")
        links.append(link)

    print("going to each link")

    for link in links:
        browser.get(link)
        page_source = browser.page_source
        # print(page.status_code) #has to be 200, if another number appeard that means that the script could not get inside the page
        # soup = BeautifulSoup(page_source, "lxml")

        author = browser.find_element(
            by=By.XPATH, value="//a[@data-testid='post-author']"
        ).text
        ad_title = browser.find_element(
            by=By.XPATH, value="//h1[@data-testid='post_title']"
        ).text
        ad_description = browser.find_element(
            by=By.XPATH, value="//article[@data-testid='post-article']"
        ).text

        # Getting the auther number
        browser.find_element(
            by=By.XPATH, value="//button[@data-testid='post-contact']"
        ).click()
        author_number = browser.find_element(
            by=By.XPATH,
            value="/html/body/reach-portal[2]/div/div[2]/div/div/div/a[2]/div[2]",
        ).text

        # except:
        #     img = None

        # if img != None:
        #     images.append(img)
        data.append(
            {
                "link": link,
                "author": author,
                "ad_title": ad_title,
                "ad_description": ad_description,
                "author_number": author_number,
            }
        )

    print(data)
    df = pd.DataFrame(data)
    df.to_csv(f"{query}.csv", index=False)

    print("------------------------")
    print(f"Haraj Scrapper summary fo {query}")
    print(f"Number of posts :{len(posts)}")
    print(f"Number of links :{len(links)}")

    browser.quit()


if __name__ == "__main__":
    query = input("Enter your query: ")
    haraj_scrapper(query, "C:\\Users\\moham\\Desktop\\", POSTS_LIMIT=100, city="الرياض")
