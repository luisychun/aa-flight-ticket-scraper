from selenium.webdriver import Chrome
import pandas as pd
from bs4 import BeautifulSoup
import time
import csv
from csv import DictWriter
import os
from datetime import datetime, timedelta
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def get_current_date():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    # insert current date time
    date_list = list()
    date_list.append(dt_string)
    return date_list[0]


def write_to_csv(ticket_price_dict):
    departure_time_key = []
    price_values = []
    num_of_slots = 10
    fields_name = ["Request On", "Departure - Destination", "Departure Date"]
    file_name = "Tickets.csv"

    for i in range(num_of_slots):
        fields_name.append("Slot "+str(i+1))

    try:
        if os.path.isfile('Tickets.csv') is False:            
            init_set = {
                fields_name[0]: "",
                fields_name[1]: "",
                fields_name[2]: ""
            }

            for i in range(num_of_slots):
                init_set.update({ "Slot "+str(i+1) : [] })

            map_to_csv = pd.DataFrame.from_dict(
                init_set)
            map_to_csv.to_csv(file_name, index=False)

            for keys, values in ticket_price_dict.items():
                departure_time_key.append(keys)
                price_values.append(values[0])
            with open(filename, 'a+', newline='') as write_obj:
                dict_writer = DictWriter(write_obj, fieldnames=fields_name)
                dict_writer.writerow(ticket_price_dict)
                print('CSV file created.')
        else:
            for keys, values in ticket_price_dict.items():
                departure_time_key.append(keys)
                price_values.append(values[0])
            with open(filename, 'a+', newline='') as write_obj:
                dict_writer = DictWriter(write_obj, fieldnames=fields_name)
                dict_writer.writerow(ticket_price_dict)
                print('CSV file updated.')
    except Exception as e:
        raise e


def input_request():
    input_list = []
    is_date_valid = False

    departure = input("Departure code: ").upper()
    input_list.append(departure)
    destination = input("Destination code: ").upper()
    input_list.append(destination)
    while not is_date_valid:
        departure_date = input("Departure date in Y-M-D format: ")
        is_date_valid = validate_date(departure_date)
        if(is_date_valid):
            break
    input_list.append(departure_date)
    return input_list


def validate_date(input_date):
    convert_date = datetime.strptime(input_date, '%Y-%m-%d')
    current_date = datetime.now()
    if(current_date > convert_date):
        print('Date is invalid. Please try again.')
        return False
    else:
        return True


def main():

    # get input from user
    input_response = input_request()    

    driver = webdriver.Chrome(ChromeDriverManager().install())

    # URL = 'https://www.airasia.com/select/en/gb/JHB/PEN/2020-04-30/N/1/0/0/O/N/MYR/ST'

    format_url = 'https://www.airasia.com/select/en/gb/' + \
        input_response[0]+'/'+input_response[1]+'/' + \
        input_response[2]+'/N/1/0/0/O/N/MYR/ST'

    driver.get(format_url)

    # execute script to scroll down the page
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    # sleep for 30s
    time.sleep(10)

    # ticket price list
    price_elements = []
    departure_time_list = []
    departure_time_map_price = {}    
    count = 0

    departure_time_map_price["Request On"] = get_current_date()    
    departure_time_map_price["Departure - Destination"] = input_response[0] + ' - ' + input_response[1]
    departure_time_map_price["Departure Date"] = input_response[2]

    content_wrapper = driver.find_elements_by_class_name('section-content')

    for content in content_wrapper:
        amount = content.find_element_by_class_name('fare-amount')
        price_elements.append(amount.text)
        departure_time = driver.find_elements_by_id(
            'departing-time-desc-0-'+str(count))
        departure_time_list.append(departure_time[0].text)
        count += 1
        price_list = list()
        price_list.append(departure_time[0].text + " - " + " RM "+amount.text)
        departure_time_map_price["Slot "+str(count)] = price_list[0]

    driver.quit()

    if not price_elements:
        print("Requested URL is invalid. Please check.")
    else:
        write_to_csv(departure_time_map_price)

    # print(departure_time_map_price)


main()
