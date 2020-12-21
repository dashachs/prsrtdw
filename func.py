import time
from selenium.common.exceptions import NoSuchElementException
import lot


def to_cut_string(text, length=255):
    for i in range(length - 5, 0, -1):
        if text[i] == '.' or text[i] == ';':
            text = text[0:i + 1] + '..'
            return text


def open_and_parse_main_page_of_buyers(browser, link, list_of_buyers):
    browser.get(link)
    if "login" in browser.current_url:
        authorize(browser)
    page_text = "?page="
    page_count = 1
    # parsing from each page until next page is empty
    while True:
        link_of_page = link + page_text + str(page_count)
        browser.get(link_of_page)
        # checking if it's empty page
        buyers = browser.find_elements_by_xpath("//div[@class='short-buyer row']/div/h3/a[1]")
        if len(buyers) == 0:
            break
        # transform
        for i in range(len(buyers)):
            buyers[i] = dict(name=buyers[i].text.strip(), link=buyers[i].get_attribute('href'))
        list_of_buyers.extend(buyers)
        page_count += 1


def parse_buyer_from_page(browser, buyer):
    browser.get(buyer['link'])
    info = browser.find_elements_by_xpath("//div[@class='row company-info']/div/*")
    info = [i.text for i in info]
    info = info[-1].replace('\n\n', '\n').split('\n')
    info = [i.split(':') for i in info]
    info = [i[-1].strip() for i in info]
    buyer['email'] = info[0]
    buyer['phone'] = info[1]
    buyer['fax'] = info[2]
    buyer['site'] = info[3]
    buyer['address'] = info[4]
    buyer['country'] = info[5]
    return buyer


def open_and_parse_main_page_of_lots(browser, link, list_of_lots):
    page_text = "?page="
    page_count = 1
    # parsing from each page until next page is empty
    while True:
        link_of_page = link + page_text + str(page_count)
        browser.get(link_of_page)
        # number_of_tenders = len(browser.find_elements_by_xpath("//div[@class='short-item col-sm-100']"))
        list_of_names = browser.find_elements_by_xpath(
            "//div[@class='short-item col-sm-100']/div[@class='col-md-70 col-sm-100']/h3/a")
        list_of_start_dates = browser.find_elements_by_xpath(
            "//div[@class='short-item col-sm-100']/div[@class='dates col-md-30 col-md-offset-0 col-sm-40 "
            "col-sm-offset-20']/div[contains(text(), 'Опубликовано')]")
        list_of_end_dates = browser.find_elements_by_xpath(
            "//div[@class='short-item col-sm-100']/div[@class='dates col-md-30 col-md-offset-0 col-sm-40 "
            "col-sm-offset-20']/div[contains(text(), 'Истекает')]")
        if len(list_of_names) == 0:
            break
        for i in range(len(list_of_names)):
            size = len(list_of_lots)
            list_of_lots.append(lot.Lot())
            list_of_lots[size].name = list_of_names[i].text.strip()
            list_of_lots[size].source_url = list_of_names[i].get_attribute('href').strip()
            list_of_lots[size].number = get_number_from_url(list_of_lots[size].source_url).strip()
            list_of_lots[size].started_at = reformat_date(list_of_start_dates[i].text).strip()
            list_of_lots[size].ended_at = reformat_date(list_of_end_dates[i].text).strip()
        page_count += 1


def parse_tender_lot(browser, current_tender):
    browser.get(current_tender.source_url)
    # giving time to process the redirect
    redirect_time = 1
    time.sleep(redirect_time)
    current_url = browser.current_url
    # authorizing if was redirected and pretending to wait
    if "login?back" in current_url:
        authorize(browser)
        time.sleep(2)

    get_category_country_subject(browser, current_tender)
    try:
        files = browser.find_elements_by_xpath(
            "//div[@class='content-wrapper']/div[@class='tender-full']/div[@class='tender_text_tab active']/div["
            "@class='files']/a")
        current_tender.attached_file = ""
        for file in files:
            current_tender.attached_file = current_tender.attached_file + file.get_attribute('href') + "; "
        current_tender.attached_file = current_tender.attached_file[:-2]
    except NoSuchElementException:
        current_tender.attached_file = None
    if current_tender.attached_file.replace(' ', '') == "":
        current_tender.attached_file = None
    get_description(browser, current_tender)
    get_email(browser, current_tender)
    get_phone(browser, current_tender)
    current_tender.type = 'tender'


def get_description(browser, current_tender):
    text = browser.find_elements_by_xpath("//div[@class='tender-full']/div[@class='tender_text_tab active']/div["
                                          "@class='text']/*")
    res = ""
    for i in text:
        if i.tag_name == 'p':
            res += i.text
        elif i.tag_name == 'table':
            res += str(i.get_attribute("outerHTML"))
        res += '\n'
    current_tender.description_long = res
    for i in text:
        if i.tag_name == 'p':
            current_tender.description_short = i.text
            break


def get_email(browser, current_tender):
    text = browser.find_element_by_xpath("//div[@class='content-wrapper']/div[@class='tender-full']").text
    temp_for_split = text.split('@')
    temp_for_email = ''
    if len(temp_for_split) > 1:
        temp_for_letters = temp_for_split[0]
        for i in range(len(temp_for_letters)):
            num = len(temp_for_letters) - i - 1
            if temp_for_letters[num] == ' ' or temp_for_letters[num] == '>' or temp_for_letters[num] == ':' or \
                    temp_for_letters[num] == '<' or temp_for_letters[num] == '&' or temp_for_letters[num] == '"' or \
                    temp_for_letters[num] == '\n':
                break
            temp_for_email = temp_for_letters[num] + temp_for_email
        temp_for_email += '@'
        temp_for_letters = temp_for_split[1]
        for i in range(len(temp_for_letters)):
            if temp_for_letters[i] == ' ' or temp_for_letters[i] == ',' or temp_for_letters[i] == '>' or \
                    temp_for_letters[i] == ';' or temp_for_letters[i] == ':' or temp_for_letters[i] == '<' or \
                    temp_for_letters[i] == '&' or temp_for_letters[i] == '"' or temp_for_letters[i] == '\n':
                break
            temp_for_email = temp_for_email + temp_for_letters[i]
        if temp_for_email[-1] == '.':
            temp_for_email = temp_for_email[:-1]
        temp_for_split.clear()
        current_tender.email2 = temp_for_email.strip()


def get_phone(browser, current_tender):
    text = browser.find_element_by_xpath("//div[@class='content-wrapper']/div[@class='tender-full']").text
    numbers = []
    char = " +-()\n"
    for i in char:
        text = text.replace(i, "")
    text = list(text)
    cnt = 0
    number = ""
    for symbol in text:
        if symbol.isdecimal():
            cnt += 1
            number += symbol
        elif not symbol.isdecimal() and (cnt == 12 or (cnt == 9 and (number[0] == 9 or number[0] == 7))):
            numbers.append(number)
            cnt = 0
            number = ""
        else:
            cnt = 0
            number = ""
    if len(numbers) > 0:
        current_tender.phone2 = numbers[0].strip()
    else:
        text = browser.find_elements_by_xpath("//div[@class='tender-full']/div[@class='tender_text_tab active']/div["
                                              "@class='text']/*")
        temp_for_phone = None
        for i in text:
            if i.tag_name == 'p':
                if "тел." in i.text.lower() or "тел:" in i.text.lower() or "телефон" in i.text.lower():
                    temp_for_phone = i.text.lower()
                    break
        if temp_for_phone is not None:
            temp_for_phone_split = 0
            if "тел." in temp_for_phone:
                temp_for_phone_split = temp_for_phone.split("тел.")
            elif "тел:" in temp_for_phone:
                temp_for_phone_split = temp_for_phone.split("тел:")
            elif "телефон" in temp_for_phone:
                temp_for_phone_split = temp_for_phone.split("телефон")
            if len(temp_for_phone_split) > 1:
                temp_for_phone = temp_for_phone_split[1]
                temp_for_phone = temp_for_phone.replace('\n', '')
                replace_values = 'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя.,;:/@'
                for value in replace_values:
                    temp_for_phone = temp_for_phone.replace(value, '')
                while "  " in temp_for_phone:
                    temp_for_phone = temp_for_phone.replace("  ", " ")
                digits = "0123456789"
                temp_for_phone = list(temp_for_phone)
                for i in range(len(temp_for_phone) - 1, -1, -1):
                    if temp_for_phone[i] in digits:
                        break
                    else:
                        del temp_for_phone[i]
                temp_for_phone = "".join(temp_for_phone)
                temp_for_phone = temp_for_phone.replace(" ", "", 1)
                temp_for_phone = (temp_for_phone, None)[temp_for_phone == ""]
        current_tender.phone2 = temp_for_phone


def get_category_country_subject(browser, current_tender):
    temp_for_three = browser.find_element_by_xpath(
        "//div[@class='content-wrapper']/div[@class='tender-full']/div[@class='info']").text
    list_for_info = temp_for_three.replace("\n", ":").replace(": ", ":").split(":")
    for i in range(len(list_for_info)):
        if i != len(list_for_info) - 1:
            if "Категория" in list_for_info[i]:
                current_tender.category = list_for_info[i + 1].strip()
            if "Закупщик" in list_for_info[i]:
                current_tender.subject = list_for_info[i + 1].strip()
            if "Страна" in list_for_info[i]:
                current_tender.country = list_for_info[i + 1].strip()
    list_for_info.clear()


def authorize(browser):
    # authorizing if was redirected and pretending to wait
    # https://codeby.net/threads/avtorizacija-na-sajte-python.69741/
    email_text = "jamshidartykov87@yandex.ru"
    password_text = "tender1week7"
    login = browser.find_element_by_xpath(
        "//form/div[@class='form register']/div[@class='form-row']/input[@name='email']")
    password = browser.find_element_by_xpath(
        "//form/div[@class='form register']/div[@class='form-row']/input[@name='password']")
    login.send_keys(email_text)
    time.sleep(2)
    password.send_keys(password_text)
    time.sleep(1)
    button = browser.find_element_by_xpath(
        "//form/div[@class='form register']/div[@class='form-row']/button[@type='submit']")
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

def merge_lots_and_buyers(list_of_lots, list_of_buyers):
    for i in range(len(list_of_lots)):
        for buyer in list_of_buyers:
            if list_of_lots[i].subject == buyer['name']:
                list_of_lots[i].phone = buyer['phone']
                list_of_lots[i].email = buyer['email']
                list_of_lots[i].email = buyer['site']
                list_of_lots[i].subject_address = buyer['address']
                break



def print_lots(list_of_tenders):
    temp_count_for_print = 1
    for tender in list_of_tenders:
        print("#", temp_count_for_print, "\n  number\n   ", tender.number, "\n  name\n   ", tender.name,
              "\n  source_url\n   ", tender.source_url, "\n  started_at\n   ", tender.started_at, "\n  ended_at\n   ",
              tender.ended_at, "\n  category\n   ", tender.category, "\n  country\n   ", tender.country,
              "\n  subject\n   ", tender.subject, "\n  attached_file\n   ", tender.attached_file,
              "\n  description_short\n   ", tender.description_short, "\n  email2\n   ", tender.email2,
              "\n  phone2\n   ", tender.phone2,  # "\n  number\n   ", tender.number,
              # "\n  number\n   ", tender.number,
              # "\n  number\n   ", tender.number,
              # "\n  number\n   ", tender.number,
              "\n ============================\n")
        temp_count_for_print += 1
