import copy

from selenium.common.exceptions import WebDriverException, NoSuchElementException
import lot


def to_cut_string(text, length=255):
    for i in range(length - 5, 0, -1):
        if text[i] == '.' or text[i] == ';':
            text = text[0:i + 1] + '..'
            return text


def open_and_parse_page(browser, link, list_of_tenders):
    browser.get(link)
    temp_for_link_text = link
    # getting number of pages


def parse_tenders_from_page(browser, list_of_tenders, tempForLinkText):
    # making all elements visible



def parse_tender_lot(browser, current_tender, list_of_tenders):
    browser.get(current_tender.source_url)




# def print_lots(list_of_tenders):
#     temp_count_for_print = 1
#     for tender in list_of_tenders:
#         print("#", temp_count_for_print,
#
#               "\n ============================\n")
#         temp_count_for_print += 1
