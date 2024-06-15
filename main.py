import csv
import datetime
import logging
import sys
import time

from bs4 import BeautifulSoup
from undetected_chromedriver2 import Chrome
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def parse_data(html):
    bs4 = BeautifulSoup(html, 'lxml')
    number = bs4.find('div', class_='card-phones-view__number')
    if number:
        number = number.text.replace('Показать телефон', '').strip()
        return number
    return ''


def main():
    url = 'https://yandex.ru/maps'
    query = input("Введите запрос:\n")
    result_set = set()

    options = webdriver.ChromeOptions()
    options.headless = False

    browser = Chrome(
        driver_executable_path='driver/chromedriver',
        version_main=126,
        options=options,
        )
    browser.maximize_window()
    start = datetime.datetime.now()
    browser.get(url)
    browser.implicitly_wait(120)
    search_input = browser.find_element(By.CLASS_NAME, 'input__control')
    search_input.send_keys(query)
    search_input.send_keys(Keys.RETURN)
    browser.implicitly_wait(120)
    result_list = browser.find_elements(By.CLASS_NAME, 'search-snippet-view')
    results = len(result_list)

    filename = f'{str(datetime.datetime.now()).split(".")[0]} - {query}.csv'.replace(':', '-').replace(':', '-')
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Номер телефона'])

    logging.info('Загрузка результатов...')
    while True:
        ActionChains(browser).scroll_to_element(result_list[-1]).perform()
        if len(result_list) % 25 == 0:
            time.sleep(7)
        if results == len(browser.find_elements(By.CLASS_NAME, 'search-snippet-view')):
            ActionChains(browser).scroll_to_element(result_list[0]).perform()
            break
        result_list = browser.find_elements(By.CLASS_NAME, 'search-snippet-view')
        results = len(result_list)
    logging.info(f'По запросу {query} найдено {len(result_list)}')
    for element in result_list:
        try:
            ActionChains(browser).scroll_to_element(element).perform()
            element.find_element(By.CLASS_NAME, 'search-business-snippet-view__title').click()
        except Exception as e:
            logging.error(e)
            continue
        phone_number = parse_data(browser.page_source)
        if not phone_number:
            continue
        phone_number = phone_number.strip()

        logging.info(phone_number)

        result_set.add(phone_number)

    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not result_set:
            logging.info('Номера телефонов не найдены')
        else:
            for row in result_set:
                writer.writerow([row,])

    browser.close()
    browser.quit()
    logging.info('Парсинг завершен')
    end = datetime.datetime.now()
    logging.info(f'Затрачено {str(end - start).split(".")[0]}')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format=('%(asctime)s, '
                '%(levelname)s, '
                '%(funcName)s, '
                '%(lineno)d, '
                '%(message)s'
                ),
        encoding='UTF-8',
        handlers=[logging.FileHandler('parser.log'),
                  logging.StreamHandler(sys.stdout)]
    )
    main()
