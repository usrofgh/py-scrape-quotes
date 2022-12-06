import csv
import requests

from bs4 import BeautifulSoup
from dataclasses import dataclass, astuple
from urllib.parse import urljoin


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


URL_BASE = "https://quotes.toscrape.com/"
PATH_FOR_WRITING_RESULT = "./../tests/correct_quotes.csv"


def get_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=quote.select_one(".quote .keywords")["content"].split(",")
    )


def get_all_quotes_from_page(page_soup: BeautifulSoup) -> [Quote]:
    return [get_single_quote(quote)
            for quote in page_soup.select(".quote")]


def step_over_all_pages() -> [Quote]:
    current_page = BeautifulSoup(requests.get(URL_BASE).content, "html.parser")
    all_quotes = get_all_quotes_from_page(current_page)
    while True:
        if current_page.select_one("li.next a"):
            page = requests.get(urljoin(
                URL_BASE,
                current_page.select_one("li.next a")["href"])).content

            current_page = BeautifulSoup(page, "html.parser")
            all_quotes.extend(get_all_quotes_from_page(current_page))
            continue
        break
    return all_quotes


def write_quotes_into_file(quotes: [Quote], output_csv_path: str) -> None:
    header = dir(quotes[0])[-3::]
    with open(output_csv_path, "w", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes_from_all_pages = step_over_all_pages()
    write_quotes_into_file(quotes_from_all_pages, output_csv_path)


if __name__ == "__main__":
    main(PATH_FOR_WRITING_RESULT)
