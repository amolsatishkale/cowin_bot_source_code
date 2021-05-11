from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from pathlib import Path
from yaml import safe_load
from datetime import datetime, timedelta
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
    result = []
    for user_input in user_inputs:
        for valid_value in valid_values:
            if str(user_input).upper() in str(valid_value).upper():
                result.append(str(valid_value).upper())
    return result


if __name__ == '__main__':
    freeze_support()

    # read the linker.yaml file
    with open(str(Path.cwd() / 'linker.yaml')) as linker_file:
        linker = safe_load(linker_file)

    # read the config.yaml file
    with open(str(Path.cwd() / 'config.yaml')) as config_file:
        config = safe_load(config_file)

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(15)
    driver.get(linker['website_link'])

    while True:
        for pin in config:
            # search zip code
            search = driver.find_element_by_xpath(linker['search_bar'])
            search.send_keys(pin)

            # click on search button
            search_button = driver.find_element_by_xpath(linker['search_button'])
            search_button.click()

            # loop over all centers
            center_names = driver.find_elements_by_class_name('center-name-title')
            all_center_names = [center_name.text for center_name in center_names]

            # get valid center names
            valid_center_names = get_valid_center_names(user_inputs=config[pin], valid_values=all_center_names)

            for center in valid_center_names:
                center = str(center).upper()
                print(f"Center: {center} - {str(pin)} - ({datetime.now().strftime('%d-%m-%Y, %H:%M:%S')})")

                # loop over all slots
                slots = driver.find_elements_by_xpath(linker['slots'].format(center))

                for i in range(1, len(slots) + 1):
                    slot = driver.find_element_by_xpath(linker['slot'].format(center, i))
                    date = datetime.now() + timedelta(days=i - 1)
                    print(f"{date.strftime('%d-%m-%Y')} - Status: {slot.text}")
                    if slot.text != 'NA' and slot.text != 'Booked':
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
            driver.refresh()
    # driver.quit()
