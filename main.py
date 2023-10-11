import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_item_text(item, by, value):
    """
    Получение текста элемента
    """
    try:
        res = item.find_element(by=by, value=value)
    except:
        return None
    return res.text


def get_item_link(item, by, value):
    """
    Получение ссылки на товар
    """

    try:
        link = item.find_element(by=by, value=value)
    except:
        return None
    return link.get_attribute("href")


def get_next_page(item):
    """
    Получение следующей страницы
    """

    try:
        next_page = item.find_element(by=By.XPATH, value='//li[contains(@class, "b-pagination__item--next") and not(contains(@class, "b-pagination__item--disabled"))]')
        next_page = next_page.find_element(by=By.TAG_NAME, value="a")
    except:
        return None
    return next_page


def check_available(item):
    """
    Проверка наличия товара
    """
    try:
        info = item.find_element(by=By.CLASS_NAME, value='b-common-item__additional-information')
        available = info.find_element(by=By.CLASS_NAME, value='b-common-item__text')
    except:
        return True
    return available.text != "Нет в наличии"


def get_row(item):
    """
    Получение необходимой инфы о товаре
    """

    is_available = check_available(item)
    brand = get_item_text(item, By.CLASS_NAME, 'span-strong')
    if not is_available:
        print(f"Нет в наличии {brand}")
        return None
    brand = get_item_text(item, By.CLASS_NAME, 'span-strong')
    if not brand:
        return None
    name = get_item_text(item, By.CLASS_NAME, 'b-item-name')
    current_price = get_item_text(item, By.CLASS_NAME, 'js-price-block')
    original_price = get_item_text(item, By.CLASS_NAME, 'b-common-item__prev-price')[:-2]
    if not original_price:
        original_price = current_price
    link = get_item_link(item, By.CLASS_NAME, 'b-common-item__description-wrap')
    id_ = link.split('=')[-1]
    return [id_, name, link, original_price, current_price, brand]


def parse(file_name):
    link = "https://4lapy.ru/catalog/koshki/korm-koshki/sukhoy/"
    result = []
    options = Options()
    options.page_load_strategy = 'none'
    
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'b-common-item')))
    
    next_page = True
    while next_page:
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'b-pagination__item--next')))
        time.sleep(2)
        items = driver.find_elements(by=By.CLASS_NAME, value='b-common-item')
        for item in items:
            row = get_row(item)
            # Скипаем, если товар не в наличии
            if not row:
                continue
            result.append(row)
        next_page = get_next_page(driver)
        if not next_page:
            break
        next_page.click()
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "b-preloader b-preloader--fixed") and not(contains(@class, "active"))]')))
    driver.quit()
    
    file_name = file_name
    headers = ["id", "name", "link", "original_price", "current_price", "brand"]
    with open(file_name, 'w', encoding="UTF-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(result)


def main():
    parse("4lapy.csv")

main()
