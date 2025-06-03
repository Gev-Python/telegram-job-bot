# parser.py
import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_usd_to_amd():
    url = "https://api.exchangerate.host/latest?base=USD&symbols=AMD"
    response = requests.get(url)
    data = response.json()
    rate = data["rates"]["AMD"]
    return round(rate, 2)

def parse_laptops(filename="laptops_auto.xlsx"):
    base_url = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops"
    page = 1
    all_laptops = []

    while True:
        url = base_url if page == 1 else f"{base_url}?page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("div", class_="card")
        if not items:
            break

        for item in items:
            title_tag = item.find("a", class_="title")
            if not title_tag:
                continue
            title = title_tag.text.strip()
            price = item.find("h4", class_="price").text.strip()
            description = item.find("p", class_="description").text.strip()
            link = "https://webscraper.io" + title_tag["href"]
            img_tag = item.find("img")
            img_url = "https://webscraper.io" + img_tag["src"] if img_tag else ""
            rating_tag = item.find("p", attrs={"data-rating": True})
            rating = int(rating_tag["data-rating"]) if rating_tag else 0

            all_laptops.append({
                "title": title,
                "price": price,
                "description": description,
                "link": link,
                "image_url": img_url,
                "rating": rating
            })

        page += 1

    df = pd.DataFrame(all_laptops)
    df.to_excel(filename, index=False, engine="openpyxl")
