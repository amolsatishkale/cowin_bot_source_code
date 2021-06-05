from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from pathlib import Path
from yaml import safe_load
import sys
import pygame
from multiprocessing import Process, freeze_support


def alarm():
    file = Path.cwd() / 'alert_voice.mp3'
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(str(file))

    while True:
        pygame.mixer.music.play()
        time.sleep(3)
        pygame.mixer.music.stop()
        time.sleep(1)


def get_valid_center_names(user_inputs, valid_values):
    # if user has not provided the center names, check all center names availability
    if user_inputs is None:
        result = []
        for item in valid_values:
            if item != '':
                result.append(item)
        return result

    # if user has provided specific center names, only check those
    else:
        result = []
        for user_input in user_inputs:
            for valid_value in valid_values:
                if str(user_input).upper() in str(valid_value).upper():
                    temp = str(valid_value).upper()
                    result.append(temp.replace(' PAID', ''))
        return result


if __name__ == '__main__':
    while True:
        try:
            freeze_support()

            # read the linker.yaml file
            with open(str(Path.cwd() / 'linker.yaml')) as linker_file:
                linker = safe_load(linker_file)

            # read the config.yaml file
            with open(str(Path.cwd() / 'config.yaml')) as config_file:
                config = safe_load(config_file)

            # create webdriver object
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.implicitly_wait(15)

            # navigate to webpage
            driver.get(linker['website_link'])

            while True:
                # iterate over pin codes in config.yaml file
                for pin in config['pin']:
                    # click on search by pin
                    search_by_pin_tab = driver.find_element_by_xpath(linker['search_by_pin_tab'])
                    search_by_pin_tab.click()

                    # search zip code
                    search = driver.find_element_by_xpath(linker['search_bar'])
                    search.send_keys(pin)

                    # click on search button
                    search_button = driver.find_element_by_xpath(linker['search_button'])
                    search_button.click()

                    # check filters if present in config.yaml file
                    if 'filter' in config:
                        for filter, flag in config['filter'].items():
                            if str(flag).strip().upper() == 'Y':
                                try:
                                    filter_checkbox = driver.find_element_by_xpath(linker[filter])
                                    filter_checkbox.click()
                                    print(f"Filter {filter} applied !")
                                except:
                                    print(f"some error in filter {filter}!")

                    # loop over 7 days until slots run out
                    slots_available = True

                    while slots_available:
                        # loop over all centers
                        center_names = driver.find_elements_by_class_name('center-name-title')
                        all_center_names = [center_name.text for center_name in center_names]

                        # get valid center names
                        valid_center_names = get_valid_center_names(user_inputs=config['pin'][pin], valid_values=all_center_names)
                        # find date range
                        date_slider_elements = driver.find_elements_by_xpath(linker['slider']['visible_elements'])
                        date_slider_elements_length = len(date_slider_elements)

                        # print date range
                        start_date_element = driver.find_element_by_xpath(linker['slider']['day'].format(1))
                        end_date_element = driver.find_element_by_xpath(
                            linker['slider']['day'].format(str(date_slider_elements_length)))
                        print(f"Date Range: {start_date_element.text} to {end_date_element.text}")

                        while True:
                            # check if error message visible (len == 2)
                            error = driver.find_elements_by_xpath(linker['error'])
                            if len(error) == 2:
                                slots_available = False
                                break

                            # check if slot rows visible (len(div) != 0)
                            slot_rows = driver.find_elements_by_xpath(linker['slot_rows'])
                            if len(slot_rows) != 0:
                                # print('break - slots found')
                                break

                        if not slots_available:
                            print('Slots not available!')
                            print()
                            break

                        for center in valid_center_names:
                            center = str(center).upper()
                            # print(f"Center: {center} - {str(pin)} - ({datetime.now().strftime('%d-%m-%Y, %H:%M:%S')})")
                            print(f"Center: {center} - {str(pin)}")

                            for i in range(1, date_slider_elements_length + 1):
                                # read date and year
                                slot_date_element = driver.find_element_by_xpath(linker['slider']['day'].format(i))
                                slot_date = slot_date_element.text

                                slots = driver.find_elements_by_xpath(linker['slots'].format(center, i))
                                # if length of slots is 3, slots are available
                                if len(slots) == 3:
                                    slot = driver.find_element_by_xpath(linker['available_slot'].format(center, i))
                                    slot_status = slot.text
                                # if length of slots is not 3, slots are not available
                                else:
                                    slot = driver.find_element_by_xpath(linker['na_booked_slot'].format(center, i))
                                    slot_status = slot.text

                                print(f"{str(slot_date)} - Status: {slot_status}")
                                if slot_status != 'NA' and slot_status != 'Booked':
                                    print('Slot Available!!!')
                                    # define alarm child process
                                    alarm_process = Process(target=alarm)
                                    alarm_process.start()
                                    time.sleep(5)
                                    input_value = input('Continue Monitoring For slots (Y/N)? : ')
                                    alarm_process.terminate()
                                    if str(input_value).upper() != 'Y':
                                        driver.quit()
                                        sys.exit()
                            print()

                        # click on next button, to check next 7 days
                        next_button = driver.find_element_by_xpath(linker['slider']['next_button'])
                        next_button.click()
                    driver.refresh()
                print('--------------------------------------')
                print()
        except Exception as error:
            try:
                print('---------------------')
                print('Error:', str(error))
                print('---------------------')
                driver.quit()
            except:
                pass


