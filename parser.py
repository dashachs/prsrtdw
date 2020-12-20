from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from psycopg2 import OperationalError
import psycopg2
import time
from natsort import natsorted
import db
import func


def execute_parser_orders():
    print("Parsing...")

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])


    # start chrome browser
    browser = webdriver.Chrome('chromedriver.exe', options=options)

    #open tenderweek's buyers
    link_of_buyers_main_page = 'https://www.tenderweek.com/company/buyers/'
    list_of_buyers = []

    # print("Collecting information about buyers")
    # func.open_and_parse_main_page_of_buyers(browser, link_of_buyers_main_page, list_of_buyers)
    # list_of_buyers = [func.parse_buyer_from_page(browser, buyer) for buyer in list_of_buyers]

    # open tenders page and parse tender
    print("Collecting information about lots")
    link = 'https://www.tenderweek.com/'
    list_of_lots = []
    func.open_and_parse_main_page_of_lots(browser, link, list_of_lots)
    func.print_lots(list_of_lots)

    # close browser
    browser.quit()

    # database input
    # while True:
    #     try:
    #         con = psycopg2.connect(database="tenderbox_test", user="denis", password="denis", host="84.54.118.76",
    #                                port="5432")
    #     except OperationalError:
    #         print("Failed to connect to the server. connection...")
    #     else:
    #         print("Database was opened successfully")
    #         break
    #
    #
    #
    # close DB
    # con.close()


    # print("Parsed successfully")

    #
    # db.get_for_everything(con, list_of_lots)
    # bidding_lots_table = db.get_bidding_lots_table(con)

    # sorting lots
    # list_of_lots = natsorted(list_of_lots, key=lambda lot: lot.number)

    # adding to DB
    # for lot in list_of_lots:
    #     if not db.in_table(lot.number, lot.source_url, bidding_lots_table):
    #         db.save_lot(con, lot)

    # find expired lots
    # db.find_expired_lots(con)

    # print("Database is up-to-date")


    # clear list of lots
    # list_of_lots.clear()
    # bidding_lots_table.clear()


# while True:
#     try:
execute_parser_orders()  # except TimeoutException:  #         print("TIMEOUT_EXCEPTION")
#     except WebDriverException:
#         print("WEB_DRIVER_EXCEPTION")
#     except:
#         print("ERROR")
#     finally:
# # setting repeating time
# timerTime = 90
# print("\n~~~~~~~~~~~~~~~~~~~~~\n"
#       "Parser will start again in", timerTime, "seconds"
#                                                "\n~~~~~~~~~~~~~~~~~~~~~\n")
# time.sleep(timerTime)
