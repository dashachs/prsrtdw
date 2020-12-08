import copy
import time

from selenium.common.exceptions import WebDriverException, NoSuchElementException
import lot


def to_cut_string(text, length=255):
    for i in range(length - 5, 0, -1):
        if text[i] == '.' or text[i] == ';':
            text = text[0:i + 1] + '..'
            return text


def open_and_parse_page(browser, link, list_of_tenders):
    page_text = "?page="
    page_count = 1
    # parsing from each page until next page is empty
    while True:
        temp_for_link_text = link + page_text + str(page_count)
        browser.get(temp_for_link_text)
        # checking if it's empty page
        try:
            browser.find_element_by_xpath("//*[contains(text(), 'По данному запросу результатов нет')]")
            break
        except NoSuchElementException:
            parse_tenders_from_page(browser, list_of_tenders, temp_for_link_text)
            page_count += 1

    for tender in list_of_tenders:
        parse_tender_lot(browser, tender, list_of_tenders)
    print_lots(list_of_tenders)


def parse_tenders_from_page(browser, list_of_tenders, temp_for_link_text):
    # parsing from page
    browser.get(temp_for_link_text)
    number_of_tenders = len(browser.find_elements_by_xpath("//div[@class='short-item col-sm-100']"))
    list_of_names = browser.find_elements_by_xpath(
        "//div[@class='short-item col-sm-100']/div[@class='col-md-70 col-sm-100']/h3/a")
    list_of_start_dates = browser.find_elements_by_xpath(
        "//div[@class='short-item col-sm-100']/div[@class='dates col-md-30 col-md-offset-0 col-sm-40 col-sm-offset-20']/div[1]")
    list_of_end_dates = browser.find_elements_by_xpath(
        "//div[@class='short-item col-sm-100']/div[@class='dates col-md-30 col-md-offset-0 col-sm-40 col-sm-offset-20']/div[2]")
    for i in range(len(list_of_names)):
        size = len(list_of_tenders)
        list_of_tenders.append(lot.Lot())
        list_of_tenders[size].name = list_of_names[i].text
        list_of_tenders[size].source_url = list_of_names[i].get_attribute('href')
        list_of_tenders[size].number = get_number_from_url(list_of_tenders[size].source_url)
        list_of_tenders[size].started_at = reformat_date(list_of_start_dates[i].text)
        list_of_tenders[size].ended_at = reformat_date(list_of_end_dates[i].text)


def parse_tender_lot(browser, current_tender, list_of_tenders):
    browser.get(current_tender.source_url)
    # giving time to process the redirect
    redirect_time = 1
    time.sleep(redirect_time)
    current_url = browser.current_url
    # authorizing if was redirected and pretending to wait
    if "login?back" in current_url:
        authorize(browser)
        time.sleep(2)
    temp_for_three = browser.find_element_by_xpath(
        "//div[@class='content-wrapper']/div[@class='tender-full']/div[@class='info']").text
    get_category_country_subject(temp_for_three, current_tender)
    try:
        files = browser.find_elements_by_xpath(
            "//div[@class='content-wrapper']/div[@class='tender-full']/div[@class='tender_text_tab active']/div[@class='files']/a")
        current_tender.attached_file = ""
        for file in files:
            current_tender.attached_file = current_tender.attached_file + file.get_attribute('href') + "; "
        current_tender.attached_file = current_tender.attached_file[:-2]
    except NoSuchElementException:
        current_tender.attached_file = None


def get_category_country_subject(temp_for_three, current_tender):
    list_for_info = temp_for_three.replace("\n", ":").replace(": ", ":").split(":")
    for i in range(len(list_for_info)):
        if i != len(list_for_info) - 1:
            if "Категория" in list_for_info[i]:
                current_tender.category = list_for_info[i + 1]
            if "Закупщик" in list_for_info[i]:
                current_tender.subject = list_for_info[i + 1]
            if "Страна" in list_for_info[i]:
                current_tender.country = list_for_info[i + 1]
    list_for_info.clear()


def authorize(browser):
    # authorizing if was redirected and pretending to wait
    # https://codeby.net/threads/avtorizacija-na-sajte-python.69741/
    email_text = "jamshidartykov87@yandex.ru"
    password_text = "tender1week7"
    login = browser.find_element_by_xpath("//form/div[@class='form register']/div[@class='form-row']/input[@name='email']")
    password = browser.find_element_by_xpath("//form/div[@class='form register']/div[@class='form-row']/input[@name='password']")
    login.send_keys(email_text)
    time.sleep(2)
    password.send_keys(password_text)
    time.sleep(1)
    button = browser.find_element_by_xpath("//form/div[@class='form register']/div[@class='form-row']/button[@type='submit']")
    button.click()


def get_number_from_url(source_url):
    number = source_url.split('-')
    return number[1]


def reformat_date(date):
    symbols = ",.-"
    date = date.replace('Опубликовано:', '').replace('Истекает:', '').replace(' ', '').replace(symbols, "/")
    day_month_year = date.split('/')
    date = (((((day_month_year[2] + '-') + day_month_year[1]) + '-') + day_month_year[0]) + ' ')
    day_month_year.clear()
    return date


def print_lots(list_of_tenders):
    temp_count_for_print = 1
    for tender in list_of_tenders:
        print("#", temp_count_for_print,
              "\n  number\n   ", tender.number,
              "\n  name\n   ", tender.name,
              "\n  source_url\n   ", tender.source_url,
              "\n  started_at\n   ", tender.started_at,
              "\n  ended_at\n   ", tender.ended_at,
              "\n  category\n   ", tender.category,
              "\n  country\n   ", tender.country,
              "\n  subject\n   ", tender.subject,
              "\n  attached_file\n   ", tender.attached_file,
              # "\n  number\n   ", tender.number,
              # "\n  number\n   ", tender.number,
              # "\n  number\n   ", tender.number,
              # "\n  number\n   ", tender.number,
              "\n ============================\n")
        temp_count_for_print += 1
