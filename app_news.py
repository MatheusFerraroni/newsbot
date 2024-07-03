from browser import Browser
from typing import List, Dict
import logging
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
import time

class AppNewsBrowser(Browser):
    url = 'https://apnews.com/'
    unoder_limit = 10

    def get_site_name(self) -> str:
        return 'ApNews'

    def _search(self) -> None:
        try:
            ad = self.lib.find_element('class:proper-ad-unit')
            self.lib.driver.execute_script('arguments[0].remove();', ad)
        except Exception as _:
            pass
        try:
            overlay_exit = self.lib.find_element('class:fancybox-close')
            overlay_exit.click()
        except Exception as _:
            pass
        search_button = self.lib.find_element(
            'class:SearchOverlay-search-button'
        )
        search_button.click()

        search_input = self.lib.find_element(
            'class:SearchOverlay-search-input'
        )
        search_input.send_keys(self.search_phrase)
        search_input.send_keys(Keys.RETURN)

    def _pre_get_content(self) -> None:
        span_total_regs = self.lib.find_element(
            'class:SearchResultsModule-count-desktop'
        )

        select_sort = self.lib.find_element('class:Select-input')
        select_sort = Select(select_sort)
        select_sort.select_by_value('3')

        self.lib.wait_until_element_is_visible(
            'class:SearchResultsModule-results'
        )
        div_result = self.lib.find_element('class:SearchResultsModule-results')
        div_to_wait = 'PageList-items-item'
        self.wait.until(
            lambda driver:
                len(div_result.find_elements(By.CLASS_NAME, div_to_wait)) > 0
        )

    def _select_category(self) -> None:
        original_content = self.lib.find_element(
            'class:SearchResultsModule-ajax'
        )
        original_content = original_content.text
        self.lib.wait_until_element_is_visible('class:SearchFilter-heading')
        cat_btn = self.lib.find_element('class:SearchFilter-heading')
        cat_btn.click()

        cat_div = self.lib.find_element('class:SearchFilter-items-wrapper')
        items = cat_div.find_elements(By.CLASS_NAME, 'SearchFilter-items-item')
        for item in items:
            word, counter = item.text.split('\n')
            if word == self.category:
                item_input = item.find_element(By.TAG_NAME, 'input')
                item_input.click()
                break

        ajax_result_div = self.lib.find_element(
            'class:SearchResultsModule-ajax'
        )
        self.wait.until(
            lambda driver: ajax_result_div.text != original_content
        )
        self.wait.until(lambda driver: len(ajax_result_div.text) > 0)

    def wait_load_content(self) -> bool:
        checks = 3
        while checks > 0:
            try:
                search_results = self.lib.find_element(
                    'class:SearchResultsModule-results'
                )
                items = search_results.find_elements(
                    By.CLASS_NAME,
                    'PageList-items-item'
                )
                for _, item in enumerate(items):
                    item.find_element(
                        By.CLASS_NAME,
                        'PagePromoContentIcons-text'
                    ).text
                break
            except Exception as _:
                checks -= 1
        return checks > 0

    def _get_content(self) -> List[Dict]:
        time.sleep(1)
        results = []

        self.wait.until(lambda driver: self.wait_load_content())
        self.lib.wait_until_element_is_visible(
            'class:SearchResultsModule-results'
        )
        self.lib.wait_until_element_is_visible(
            'class:PageList-items-item'
        )

        search_results = self.lib.find_element(
            'class:SearchResultsModule-results'
        )
        items = search_results.find_elements(
            By.CLASS_NAME,
            'PageList-items-item'
        )

        for idx, item in enumerate(items):
            item_title = item.find_element(
                By.CLASS_NAME,
                'PagePromoContentIcons-text'
            )
            item_title = item_title.text

        if len(items) == 0:
            raise Exception('No content found')

        unodered_content_counter = self.unoder_limit
        for idx, item in enumerate(items):
            logging.info(f'{idx}/{len(items)} - {item}')

            item_title = item.find_element(
                By.CLASS_NAME,
                'PagePromoContentIcons-text'
            )
            logging.info(f'Getting: {item_title}')
            item_title = item_title.text

            item_desc = item.find_element(
                By.CLASS_NAME,
                'PagePromoContentIcons-text'
            )
            item_desc = item_desc.text

            item_date = item.find_element(
                By.CLASS_NAME,
                'Timestamp-template'
            )
            item_date = item_date.text
            try:
                item_image = item.find_element(
                    By.CLASS_NAME,
                    'PagePromo-media'
                )
                item_image_link = item_image.find_element(
                    By.CLASS_NAME,
                    'Link'
                )
                item_image_desc = item_image_link.get_attribute('aria-label')

            except Exception as _:
                item_image_desc = self.not_found_msg

            try:
                item_img_src = item.find_element(By.TAG_NAME, 'img')
                item_img_src = item_img_src.get_attribute('src')
            except Exception as e:
                item_img_src = False

            if 'hours ago' in item_date:
                item_date = datetime.now().date().strftime("%B %d, %Y")
            elif ',' not in item_date:
                current_year = datetime.now().year
                item_date = f'{item_date}, {current_year}'
            item_date = datetime.strptime(item_date, '%B %d, %Y').date()

            should_stop = self.should_stop_get_content(item_date)
            if should_stop:
                unodered_content_counter = unodered_content_counter - 1
                logging.debug(f'Out of date range {item_date}')
                logging.debug(f'Counter value: {unodered_content_counter}')
                if unodered_content_counter == 0:
                    return False, results
            else:
                logging.debug('Reset unodered counter')
                unodered_content_counter = self.unoder_limit

            if not should_stop:
                results.append({
                    'item_title': item_title,
                    'item_desc': item_desc,
                    'item_image_desc': item_image_desc,
                    'item_date': item_date,
                    'img_src': item_img_src
                })

        return True, results

    def _next_page(self) -> None:
        btn_next_page = None
        try:
            btn_next_page = self.lib.find_element('class:Pagination-nextPage')
            btn_next_page.click()
        except Exception as _:
            raise Exception('Next page button not found')
