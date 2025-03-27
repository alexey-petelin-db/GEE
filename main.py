from time import sleep

from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import os
import json

from datetime import datetime
import calendar

# Get a list of all month names
months = list(calendar.month_name)
# Set up the WebDriver using Driver Manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open a website


def navigate_to(year: str, month: str):
    print("Navigating to:", year,  month)
    dropdown = driver.find_element(By.CSS_SELECTOR, 'select[data-select-name="years"]')
    select = Select(dropdown)

    selected_value = select.first_selected_option.get_attribute("value")

    if selected_value != year:
        select.select_by_value(year)
        sleep(10)
    else:
        print("Year already selected")

    dropdown = driver.find_element(By.CSS_SELECTOR, 'select[data-select-name="months"]')
    select = Select(dropdown)
    select.select_by_index(months.index(month))
    sleep(5)

driver.get("https://www.db.com/media/news?language_id=1")
driver.implicitly_wait(5)
input("Close cookies...")
sleep(5)

for language, id in (('EN', 1), ('DE', 2)):
    driver.get(f"https://www.db.com/media/news?language_id={id}")
    driver.implicitly_wait(5)

    for year in range(2015, 2026):
        year = str(year)
        for month_index, month in enumerate(months[1:]):
            directory = f"article_urls/{year}/{language}"
            file_name = f"{month_index:02d}.json"

            if os.path.exists(f"{directory}/{file_name}"):
                print("Data already exists:", language, year, month)
                continue

            navigate_to(year, month)

            try:
                load_more = driver.find_element(By.XPATH, '//button[text()="Load More"]')
                load_more.click()
            except:
                print("No more data to be discovered")

            articles = driver.find_elements(By.CSS_SELECTOR, 'div[class="news-stream-entry-info"] > div > h3 > a')
            articles_urls = [article.get_attribute('href') for article in articles]
            print(articles_urls)

            os.makedirs(directory, exist_ok=True)
            with open(f"{directory}/{file_name}", "w", encoding="utf-8") as out_file:
                json.dump(articles_urls, out_file, indent=4)
                print("Writing done")


# Keep the browser open for a while
input("Press Enter to close the browser...")

# Close the browser
driver.quit()
