import csv
import datetime

from bs4 import BeautifulSoup
from undetected_chromedriver2 import Chrome
import selenium
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def parse_data(html):
    bs4 = BeautifulSoup(html, 'lxml')
    number = bs4.find('div', class_='card-phones-view__number')
    whats = bs4.find('a', {'aria-label': 'Соцсети, whatsapp'})
    if number:
        number = number.text.replace('Показать телефон', '').strip()
    if whats:
        whats = whats.get('href')
    print(number, whats)
    return number, whats


ROOT_URL = 'https://yandex.ru/maps'
query = input("Введите запрос:\n")
result_set = set()

options = webdriver.ChromeOptions()
options.headless = False

browser = Chrome(
    options=options,
    version_main=126
)
browser.maximize_window()
browser.get(ROOT_URL)
browser.implicitly_wait(10)
search_input = browser.find_element(By.CLASS_NAME, 'input__control')
search_input.send_keys(query)
search_input.send_keys(Keys.RETURN)
browser.implicitly_wait(10)
result_list = browser.find_elements(By.CLASS_NAME, 'search-snippet-view')
results = len(result_list)

filename = f'{str(datetime.datetime.now()).split(".")[0]} - {query}.csv'.replace(':', '-').replace(':', '-')
with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Номер телефона', 'WhatsApp'])

while True:
    ActionChains(browser).move_to_element(result_list[-1]).perform()
    if results == len(browser.find_elements(By.CLASS_NAME, 'search-snippet-view')):
        ActionChains(browser).move_to_element(result_list[0]).perform()
        break
    result_list = browser.find_elements(By.CLASS_NAME, 'search-snippet-view')
    results = len(result_list)

for element in result_list:
    ActionChains(browser).move_to_element(element).perform()
    try:
        element.find_element(By.CLASS_NAME, 'search-business-snippet-view__title').click()
    except selenium.common.exceptions.NoSuchElementException:
        continue
    phone_number, whatsapp = parse_data(browser.page_source)
    if phone_number:
        phone_number = phone_number.strip()
    if whatsapp:
        whatsapp = whatsapp.strip()

    print(phone_number, whatsapp)

    result_set.add((phone_number, whatsapp))


with open(filename, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for row in result_set:
        writer.writerow(row)

browser.close()
browser.quit()
print('Парсинг завершен')
