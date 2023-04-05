from bs4 import BeautifulSoup
import requests
import pandas as pd
from header import HEADERS
import multiprocessing as mp
import time
import logging

BASE_SITE = "https://www.amazon.com"
URL = f"{BASE_SITE}/s?k=gaming+monitor&crid=1MWO6K0F604A2&sprefix=gaming+monitor%2Caps%2C140&ref=nb_sb_noss_1"

valid_us_proxies = [
    "192.154.253.67:8123",
    "161.156.166.16:8080",
    "64.225.8.191:9987",
    "20.99.187.69:8443",
    "217.79.253.106:80",
    "216.246.40.215:8999",
    "64.225.4.81:9991",
    "43.249.11.165:45787",
    "34.170.89.64:80",
    "174.138.167.182:8888",
    "12.88.29.66:9080",
    "50.199.32.226:8080",
    "143.198.228.250:80",
    "137.184.100.135:80",
    "35.209.198.222:80"
]
counter = 0


def make_request(link: str):
    global counter
    n = len(valid_us_proxies)
    proxy = {"http": valid_us_proxies[counter % n], "https": valid_us_proxies[counter % n]}
    response = requests.get(link, headers=HEADERS, proxies=proxy)
    counter += 1
    return response


def main():
    page = make_request(URL)
    soup = BeautifulSoup(page.content, "lxml")
    main_divs = soup.findAll("div", class_="a-section a-spacing-small a-spacing-top-small")
    names = [div.find("span", class_="a-size-medium a-color-base a-text-normal") for div in main_divs]
    links = [div.find("a", class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal") for div in main_divs]
    prices = [div.find("span", class_="a-price") for div in main_divs]

    """
    specs usually in a table class
    "table", class_="a-bordered a-horizontal-stripes aplus-tech-spec-table"
    this is the single table view
    "table" id="HLCXComparisonTable" class="a-bordered a-horizontal-stripes a-spacing-none a-size-base comparison_table"
    this is the comparison table
    the selected element will be tagged with comparison_baseitem_column
    """
    data = []
    specific_pages = []

    for name, link, price in zip(names, links, prices):
        if not any([name, link, price]):
            continue
        price = float(price.find('span').text.replace('$', '').replace(',', '')) if price else None
        link = f"{BASE_SITE}{link.get('href')}" if link else None
        data.append({"product_name": name.text if name else None, "link": link, "price": price})
        # keep these seperate just for convenience
        specific_pages.append(link)

    with mp.Pool(max(len(specific_pages), 32)) as p:
        responses = p.map(make_request, specific_pages)

    for idx, response in enumerate(responses):
        specific_soup = BeautifulSoup(response.content, "lxml")
        price_whole = specific_soup.find("span", class_="a-price-whole")
        price_dec = specific_soup.find("span", class_="a-price-fraction")
        if not data[idx]["price"] == float(price_whole.text.replace('$', '').replace(',', '')+price_dec.text):
            print(data[idx]["product_name"])
            print(data[idx]["price"], f"{price_whole.text}{price_dec.text}")
            print(data[idx]["link"])
    print(pd.DataFrame(data))


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    print("total time")
    print(time.perf_counter() - start)
