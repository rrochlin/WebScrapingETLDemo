from bs4 import BeautifulSoup
import requests
import pandas as pd
from header import HEADERS
import multiprocessing as mp
import time
from base_logger import logger
import re
from random import randint, random
from SQL_Connection_Handler import SQL_Connection_Handler as SQL


BASE_SITE = "https://www.amazon.com"
URL = "/s?k=gaming+monitor&page={}&crid=1MWO6K0F604A2&qid=1680676316&sprefix=gaming+monitor%2Caps%2C140&ref=sr_pg_{}"
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


def make_request(link: str, proxy_ip: str):
    time.sleep(random())
    logger.info("making req")
    proxy = {"http": proxy_ip, "https": proxy_ip}
    global good_proxies
    try:
        response = requests.get(link, headers=HEADERS, proxies=proxy, timeout=5)
        logger.info("request succeeded")
        good_proxies.put(proxy_ip)
    except Exception:  # requests.exceptions.ProxyError
        logger.warning("proxy timed out retrying")
        if not good_proxies.empty():
            new_proxy_ip = good_proxies.get()
            logger.info("used the queue")
        else:
            new_proxy_ip = valid_us_proxies[randint(0, len(valid_us_proxies) - 1)]
        response = make_request(link, new_proxy_ip)
    return response


def initialize_worker(queue):
    global good_proxies
    good_proxies = queue


def main():

    num_pages = 200
    URLS = [f"{BASE_SITE}{URL.format(i, i)}" for i in range(1, num_pages)]
    global good_proxies
    good_proxies = mp.Queue()
    if len(URLS) > len(valid_us_proxies):
        pages_and_proxies = zip(URLS, valid_us_proxies*(len(URLS)//len(valid_us_proxies)))
    else:
        pages_and_proxies = zip(URLS, valid_us_proxies[:len(URLS)])
    num_pool = min(len(URLS), len(valid_us_proxies), mp.cpu_count())
    with mp.Pool(num_pool, initializer=initialize_worker, initargs=(good_proxies,)) as p:
        pages = p.starmap(make_request, pages_and_proxies)
    names = []
    links = []
    prices = []
    filtered_divs = []
    item_element_class = "a-section a-spacing-small a-spacing-top-small"
    name_class = "a-size-medium a-color-base a-text-normal"
    link_class = "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"
    price_class = "a-price"

    for page in pages:
        soup = BeautifulSoup(page.content, "lxml")
        main_divs = soup.findAll("div", class_=item_element_class)
        for div in main_divs:
            if not (name := div.find("span", class_=name_class)):
                continue
            if re.search(r"monitor", name.text, re.IGNORECASE) and not re.search(r"desk", name.text, re.IGNORECASE):
                filtered_divs.append(div)
    print(len(filtered_divs))
    names = [div.find("span", class_=name_class) for div in filtered_divs]
    links = [div.find("a", class_=link_class) for div in filtered_divs]
    prices = [div.find("span", class_=price_class) for div in filtered_divs]
    """
    specs usually in a table class
    "table", class_="a-bordered a-horizontal-stripes aplus-tech-spec-table"
    this is the single table view
    "table" id="HLCXComparisonTable" class="a-bordered a-horizontal-stripes a-spacing-none a-size-base comparison_table"
    this is the comparison table
    the selected element will be tagged with comparison_baseitem_column
    """
    data = []
    for name, link, price in zip(names, links, prices):
        if not any([name, link, price]):
            continue
        price = float(price.find('span').text.replace('$', '').replace(',', '')) if price else None
        link = f"{BASE_SITE}{link.get('href')}" if link else None
        data.append({"product_name": name.text if name else None, "link": link, "price": price})
    df = pd.DataFrame(data).dropna()
    sql = SQL()
    dbconn = sql.engine.connect()

    logger.info(df)
    logger.info("writing to sql db")
    df.to_sql("amazon_monitor_info", con=dbconn, schema="public", index=False)
    logger.info("writing to local excel file")
    df.to_excel("amazon_monitor_info.xlsx", index=False)


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    logger.info("total time")
    logger.info(time.perf_counter() - start)
