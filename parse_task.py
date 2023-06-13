from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json
import multiprocessing


def _get_driver() -> webdriver:
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    return driver

def get_products_on_page(url_path: str) -> list:
    """Получение информации о продуктах на странице"""
    products_list = list()
    driver = _get_driver()
    driver.get(url_path)
    try:
        wait = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'products-inner')))
        products = driver.find_element(By.ID, 'products-inner').find_elements(By.CLASS_NAME,
                                                                                'catalog-2-level-product-card')
        for product in products:
            product_info = dict()
            product_info['id'] = product.get_attribute('data-sku')
            href_and_name = product.find_element(By.CLASS_NAME, 'product-card-name')
            product_info['name'] = href_and_name.text
            product_info['href'] = href_and_name.get_attribute('href')
            prices = product.find_elements(By.CLASS_NAME, 'product-price__sum')
            if prices != []:
                product_info['price'] = prices[-1].text.replace('д', 'р')
                product_info['pro_price'] = prices[0].text.replace('д', 'р') if len(prices) > 1 else '-'
            else:
                product_info['price'] = '-'
                product_info['pro_price'] = '-'
            products_list.append(product_info)
        driver.close()
        print(f'URL: {url_path} Complite')
    except TimeoutException:
        driver.close()
    finally:
        return products_list

def get_count_pages(url_path: str) -> int:
    """Получение количества страниц с данным товаром"""
    driver = _get_driver()
    driver.get(url_path)
    try:
        wait = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'products-inner')))
        count_page = driver.find_elements(By.CLASS_NAME, 'v-pagination__item')[-1].text
        driver.close()
        return int(count_page)
    except TimeoutException:
        driver.close()
        return 0

def main():
    url_path = 'https://online.metro-cc.ru/category/molochnye-prodkuty-syry-i-yayca/syry'
    count_page = get_count_pages(url_path)
    url_pages = [f'{url_path}?page={number_page}' for number_page in range(1, count_page+1)]
    with multiprocessing.Pool(2) as pool:
        products_list = pool.map(get_products_on_page, url_pages)

    with open("result.json", "w", encoding='utf-8') as write_file:
        json.dump({'data': products_list}, write_file, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()