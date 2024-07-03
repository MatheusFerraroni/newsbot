from robocorp.tasks import task
from latimes import LaTimesBrowser
from app_news import AppNewsBrowser
from robocorp import workitems
import logging


@task
def task_latimes():
    logging.basicConfig(
        level=logging.INFO, filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.info('Starting')

    items = workitems.inputs.current
    search_phrase = items.payload['phrase']
    months = items.payload['months']
    category = items.payload['category']

    site = LaTimesBrowser(
        search_phrase=search_phrase,
        category=category,
        months=months
    )
    site.start_flow()


@task
def task_appnews():
    logging.basicConfig(
        level=logging.INFO, filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.info('Starting')

    items = workitems.inputs.current
    search_phrase = items.payload['phrase']
    months = items.payload['months']
    category = items.payload['category']

    site = AppNewsBrowser(
        search_phrase=search_phrase,
        category=category,
        months=months
    )
    site.start_flow()
