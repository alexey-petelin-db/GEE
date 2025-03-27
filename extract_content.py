import calendar
import itertools
import json
import os
from dataclasses import dataclass, asdict
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


@dataclass
class ArticleModel:
    url: str
    language: str
    article_type: str
    publish_date: str
    tags: list[str]
    title: str
    body: str
    number_of_ratings: int
    rating: float
    likes: int


MONTHS = list(calendar.month_name)


def read_article_urls(year: str, language: str, month_id: int) -> list[str]:
    with open(f"article_urls/{year}/{language}/{month_id:02d}.json", 'r', encoding="utf-8") as fp:
        return json.load(fp)


def setup_driver() -> webdriver.Chrome:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get("https://www.db.com/media/news?language_id=1")
    driver.implicitly_wait(5)
    input("Close cookies...")
    sleep(5)

    return driver


def retrieve_article_data(
        driver: webdriver.Chrome,
        url: str,
        language: str,
) -> ArticleModel:
    print(url)
    driver.get(url)
    sleep(7)

    spans = driver.find_elements(By.CSS_SELECTOR, 'div[class="tag-bar"] > ul > li > a > span')
    tags = [span.text for span in spans]

    article_type, publish_date = driver.find_element(By.CSS_SELECTOR, 'div[class="meta-bar"]').find_elements(
        By.CSS_SELECTOR, "span")
    article_type, publish_date = article_type.text, publish_date.text

    title = driver.find_element(By.CSS_SELECTOR, 'section[class="mod-page-headline"] > h1').text

    body = driver.find_element(By.CSS_SELECTOR, 'div[class="news-text"]').text

    number_of_ratings = int(
        driver.find_element(
            By.XPATH,
            '//ul[@class="news-meta-links-list"]/li[1]/a/span[@class="meta-link-text"]'
        )
        .text
        .split(" ")[0]
    )
    if number_of_ratings == 0:
        rating = None
    else:
        rating = float(driver.find_element(By.CSS_SELECTOR, 'span[class="rating-result"]').text.split(" ")[1].split("/")[0])
    likes = int(driver.find_element(By.XPATH,
                                    '//ul[@class="news-meta-links-list"]/li[2]/a/span[@class="meta-link-text"]').text.split(
        " ")[0])

    return ArticleModel(
        url=url,
        language=language,
        article_type=article_type,
        publish_date=publish_date,
        tags=tags,
        title=title,
        body=body,
        number_of_ratings=number_of_ratings,
        rating=rating,
        likes=likes
    )


def save_article(language: str, year: str, month: int, index: int, article: ArticleModel) -> None:
    directory = f"article/{language}/{year}/{month:02d}"
    file_name = f"{index:03d}.json"
    os.makedirs(directory, exist_ok=True)

    with open(f"{directory}/{file_name}", "w", encoding="utf-8") as fp:
        json.dump(asdict(article), fp, indent=4)


def main():
    driver = setup_driver()

    languages = ("EN", "DE")
    years = list(map(str, range(2015, 2026)))
    months = enumerate(MONTHS[1:])



    for language, year, (month_id, month) in itertools.product(languages, years, months):
        print(language, year, month_id, month)
        article_urls = read_article_urls(
            year,
            language,
            month_id
        )

        for idx, article_url in enumerate(article_urls):
            directory = f"article/{language}/{year}/{month_id:02d}"
            file_name = f"{idx:03d}.json"

            if os.path.exists(f"{directory}/{file_name}"):
                print(f"Skipping {article_url}", f"{directory}/{file_name}")
                continue

            try:
                article = retrieve_article_data(
                    driver,
                    article_url,
                    language
                )
                save_article(
                    language,
                    year,
                    month_id,
                    idx,
                    article
                )
            except:
                print(f"Failed to extract {article_url}", f"{directory}/{file_name}")


if __name__ == "__main__":
    main()
