import requests
from bs4 import BeautifulSoup
import time
import csv
import json
from fake_useragent import UserAgent
import os
# ############# url #############
url = "https://calorizator.ru"
# ############# url #############


def fake_header():
    """генерируем headers"""
    ua = UserAgent()
    header = {"User-Agent": str(ua.chrome)}
    return header


def query(link):
    """функция "берем с сайта всю инфу и возвращаем src"""
    response = requests.get(link, headers=fake_header())
    src = response.text

    return src


def record(name, file_record):
    """сохраняем в нужный файл код страницы"""
    with open(name, "w", encoding="utf-8") as file:
        file.write(file_record)


def transfer_to_soup(name):
    """считываем из нашего документа страничку"""
    with open(name, "r", encoding='utf-8') as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")

    return soup


def to_dict(link_list):
    """принимаем лист с тегами и делаем из него словарик с сылками и названием """
    all_dict ={}
    for item in link_list:
        item_text = item.text
        item_href = item.find("a").get("href")
        all_dict[item_text] = url + "/" + item_href

    return all_dict


def main():
    """бегаем по словарю и парсим инфу по отдельным катогрияму, а так же сохраняем"""
    # ###################### делаем запрос
    src = query(url)
    if not os.path.exists("general"):
        os.mkdir("general")
    record("general/index.html", src)
    soup = transfer_to_soup("general/index.html")

    # ############### с общей страницы вытягиваем что нам нужно, в данный момент продукты
    general_links = soup.find("ul", class_="links primary-links").find_all("li")
    all_categories_dict = to_dict(general_links)

    # ################## разбор по продуктам
    src = query(all_categories_dict["Продукты"])
    record("general/product.html", src)
    soup_primary = transfer_to_soup("general/product.html")
    product = soup_primary.find("div", class_="node-content").find_all("li")
    all_product_category = to_dict(product)

    count = 0
    for item_name in all_product_category:
        if count < 2:
            src = query(all_product_category[item_name])
            record(f"general/{item_name}.html", src)
            soup = transfer_to_soup(f"general/{item_name}.html")
            product_info = []
            product_data = soup.find("tbody").find_all("tr")

            for item in product_data:
                product_information = item.find_all("td")

                item_product = product_information[1].find("a").text.lower().replace(" ", "_")
                item_protein = product_information[2].text.strip()
                item_fat = product_information[3].text.strip()
                item_carbohydrates = product_information[4].text.strip()
                item_calories = product_information[5].text.strip()

                product_info.append(
                    {
                        "title": item_product,
                        "protein": item_protein,
                        "fat": item_fat,
                        "carbohydrates": item_carbohydrates,
                        "calories": item_calories
                    }
                )

            with open(f"general/{item_name}.json", "a", encoding="utf-8") as file:
                json.dump(product_info, file, indent=4, ensure_ascii=False)

        count += 1


if __name__ == "__main__":
    main()




