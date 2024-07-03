from app_news import AppNewsBrowser
from latimes import LaTimesBrowser
import logging
import pdb


def main():
    logging.basicConfig(
        level=logging.INFO, filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.info('Starting')

    search_phrase = 'brasil'
    months = 12

    category = 'STORIES'
    site = AppNewsBrowser(
        search_phrase=search_phrase,
        category=category,
        months=months
    )
    site.start_flow()

    category = 'World & Nation'
    site = LaTimesBrowser(
        search_phrase=search_phrase,
        category=category,
        months=months
    )

    site.start_flow()
    pdb.set_trace()


if __name__ == '__main__':
    main()
