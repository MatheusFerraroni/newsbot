from browser import Browser
from typing import List, Dict
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime


class LaTimesBrowser(Browser):
    url = 'https://www.latimes.com/'

    def get_site_name(self) -> str:
        return 'latimes'

    def _search(self) -> None:
        search_button = self.lib.find_element(
            'xpath:/html/body/ps-header/header/div[2]/button'
        )
        search_button.click()

        search_input = self.lib.find_element('name:q')
        search_input.send_keys(self.search_phrase)
        search_input.send_keys(Keys.RETURN)

    def _pre_get_content(self) -> None:
        sort_div = self.lib.find_element('class:search-results-module-sorts')
        sort_select = sort_div.find_element(By.CLASS_NAME, 'select-input')
        select_sort = Select(sort_select)
        select_sort.select_by_value('1')

    def check_div_change(self, a: str, b: str) -> bool:
        return self.lib.find_element(a).text != b

    def _select_category(self) -> None:
        # pdb.set_trace()
        div_check = 'class:search-results-module-results-menu'
        self.lib.wait_until_element_is_visible(div_check)
        original_text = self.lib.find_element(div_check).text
        self.lib.wait_until_element_is_visible(
            'class:see-all-text'
        )
        btn_see_all = self.lib.find_element('class:see-all-text')
        btn_see_all.click()

        category_list = btn_see_all = self.lib.find_element(
            'class:search-filter-menu'
        )
        items = category_list.find_elements(
            By.CLASS_NAME,
            'search-filter-input'
        )

        for item in items:
            word, counter = item.text.split('\n')
            print(word)
            if word == self.category:
                item_input = item.find_element(
                    By.CLASS_NAME,
                    'checkbox-input-element'
                )
                item_input.click()
                break

        retry = 3
        while retry > 0:
            try:
                self.lib.wait_until_element_is_visible(div_check)
                self.wait.until(lambda driver:
                                self.check_div_change(div_check, original_text)
                                )
                div_results_pagination = self.lib.find_element(
                    'class:search-results-module-results-menu'
                )
                self.wait.until(lambda driver:
                                len(div_results_pagination.text) > 0
                                )
                retry = 0
            except Exception as e:
                retry -= 1

    def _get_content(self) -> List[Dict]:
        results = []

        self.lib.wait_until_element_is_visible(
            'class:search-results-module-wrapper'
        )
        self.lib.wait_until_element_is_visible(
            'class:search-results-module-main'
        )
        self.lib.wait_until_element_is_visible(
            'class:search-results-module-results-menu'
        )

        div_results_pagination = self.lib.find_element(
            'class:search-results-module-results-menu'
        )
        self.wait.until(lambda driver: len(div_results_pagination.text) > 0)

        div_contents = self.lib.find_element(
            'class:search-results-module-results-menu'
        )
        items = div_contents.find_elements(By.TAG_NAME, 'li')

        for idx, item in enumerate(items):
            logging.info(f'{idx}/{len(items)} - {item}')
            _, item_title, item_desc, item_date = item.text.split('\n')
            logging.info(f'Getting: {item_title}')
            img = item.find_element(By.TAG_NAME, 'img')
            item_image_desc = img.get_attribute('alt')
            img_src = img.get_attribute('src')

            if item_date[0:5] == 'Jan. ':
                item_date = 'January ' + item_date[5:]
            if item_date[0:5] == 'Feb. ':
                item_date = 'February ' + item_date[5:]
            elif item_date[0:5] == 'Oct. ':
                item_date = 'October ' + item_date[5:]
            elif item_date[0:5] == 'Nov. ':
                item_date = 'November ' + item_date[5:]
            elif item_date[0:5] == 'Sept.':
                item_date = 'September' + item_date[5:]
            elif item_date[0:5] == 'Aug. ':
                item_date = 'August ' + item_date[5:]
            elif item_date[0:5] == 'Dec. ':
                item_date = 'December ' + item_date[5:]
            item_date = datetime.strptime(item_date, '%B %d, %Y').date()

            should_stop = self.should_stop_get_content(item_date)
            if should_stop:
                return False, results

            results.append({
                'item_title': item_title,
                'item_desc': item_desc,
                'item_image_desc': item_image_desc,
                'item_date': item_date,
                'img_src': img_src
            })

        return True, results

    def _next_page(self) -> None:
        btn_next_page = None
        try:
            btn_next_page = self.lib.find_element(
                'class:search-results-module-next-page'
            )
            btn_next_page.click()
        except Exception as _:
            raise Exception('Next page button not found')
