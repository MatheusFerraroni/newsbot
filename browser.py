import abc
from RPA.Browser.Selenium import Selenium
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from selenium.webdriver.support.ui import WebDriverWait
import os
import logging
from typing import List, Dict
import requests
from PIL import Image
from io import BytesIO


class Browser():
    url = None
    lib = None
    delay = 1
    search_phrase = None
    category = None
    month_limit = date.today().replace(day=1)
    wait = None
    default_wait_time = 10
    sep = ','
    not_found_msg = 'NOT FOUND'

    def __init__(self, search_phrase: str, category: str, months: int) -> None:
        logging.info('Starting Browser')
        self.start_time = int(datetime.now().timestamp())
        self.lib = Selenium()
        self.wait = WebDriverWait(self.lib, self.default_wait_time)
        self.search_phrase = search_phrase
        self.category = category
        if months > 1:
            months -= 1
            self.month_limit = self.month_limit - relativedelta(months=months)
        self.lib.open_available_browser(self.url)
        logging.info('Creating Browser Complete')

    def goto(self, url: str) -> None:
        logging.info(f'Loading URL: {url}')
        self.lib.go_to(url)
        logging.info('Loading URL: Complete')

    def start_flow(self) -> None:
        logging.info('Flow: Starting')
        self.search()
        self.select_category()
        self.pre_get_content()
        all_contents = []
        while True:
            try:
                has_more, contents = self.get_content()
                all_contents += contents
                if not has_more:
                    break
                self.next_page()
            except Exception as e:
                logging.info(f'Stopping get content due to: {e}')
                break
        all_contents = self.download_media(all_contents)
        self.save_content(all_contents)
        self.lib.close_browser()
        logging.info('Flow: Complete')

    def download_media(self, contents: List[Dict]) -> List[Dict]:
        logging.info('Downloading Media: Start')
        for i in range(len(contents)):
            if contents[i]['img_src']:
                response = requests.get(contents[i]['img_src'])
                if response.status_code == 200:
                    contents[i]['img_data'] = Image.open(
                        BytesIO(response.content)
                    )
                else:
                    contents[i]['img_data'] = False
            else:
                contents[i]['img_data'] = False
        logging.info('Downloading Media: Complete')
        return contents

    def save_content(self, contents: List[Dict]) -> None:
        logging.info('Saving Content: Starting')
        output_folder = './output'
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)

        site_name = self.get_site_name()
        output_folder = f'{output_folder}/{site_name}'
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)

        output_folder = f'{output_folder}/{self.start_time}'
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)

        f_name = 'data.csv'
        output_file = f'{output_folder}/{f_name}'

        with open(output_file, 'w') as file:
            file.write('idx,item_title,item_desc,item_image_desc')
            file.write(',item_date,img_file\n')
            for idx, content in enumerate(contents):
                if content['img_data']:
                    content['img_data'].save(f'{output_folder}/{idx}.jpg')
                file.write(f'{idx}{self.sep}')
                file.write("'" + content['item_title'] + "'")
                file.write(self.sep)
                file.write("'" + content['item_desc'] + "'")
                file.write(self.sep)
                file.write("'" + content['item_image_desc'] + "'")
                file.write(self.sep)
                file.write("'")
                file.write(content['item_date'].strftime('%Y-%m-%d'))
                file.write("'")
                file.write(self.sep)
                file.write("'")
                file.write(f'{idx}.jpg')
                file.write("'")
                file.write('\n')
        logging.info('Saving Content: Complete')

    def should_stop_get_content(self, checking_date: date) -> bool:
        return checking_date < self.month_limit

    def next_page(self) -> None:
        logging.info('Next page: Calling')
        self._next_page()
        logging.info('Next Page: Complete')

    def search(self) -> None:
        logging.info('Search: Calling')
        self._search()
        logging.info('Search: Complete')

    def pre_get_content(self) -> None:
        logging.info('Pre Get Content: Calling')
        self._pre_get_content()
        logging.info('Pre Get Content: Complete')

    def select_category(self) -> None:
        logging.info('Select Category: Calling')
        self._select_category()
        logging.info('Select Category: Complete')

    def get_content(self) -> List[Dict]:
        logging.info('Get Content: Calling')
        return self._get_content()
        logging.info('Get Content: Complete')

    def _pre_get_content(self) -> None:
        pass

    @abc.abstractmethod
    def _next_page(self) -> None:
        pass

    @abc.abstractmethod
    def get_site_name(self) -> str:
        pass

    @abc.abstractmethod
    def _search(self) -> None:
        pass

    @abc.abstractmethod
    def _select_category(self) -> None:
        pass

    @abc.abstractmethod
    def _get_content(self) -> List[Dict]:
        pass
