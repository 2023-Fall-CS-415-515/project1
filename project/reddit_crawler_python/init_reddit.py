import logging
import time
import faktory
import reddit_client
from datetime import datetime, timedelta
from faktory import Worker
from dotenv import load_dotenv
import os

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S')

load_dotenv()
# I believe that the faktory client might automatically use this environment
# variable if no connection information is provided; you should check docs.
FAKTORY_URL = os.environ.get('FAKTORY_URL')

with faktory.connection(faktory=FAKTORY_URL) as client:
    
    run_at_gundeals = datetime.utcnow() + timedelta(minutes=5)
    run_at_guns = datetime.utcnow() + timedelta(minutes=65)
    run_at_progun = datetime.utcnow() + timedelta(minutes=125)
    run_at_gunpolitics = datetime.utcnow() + timedelta(minutes=185)
    run_at_gundeals = run_at_gundeals.isoformat()[:-7] + "Z"
    run_at_guns = run_at_guns.isoformat()[:-7] + "Z"
    run_at_progun = run_at_progun.isoformat()[:-7] + "Z"
    run_at_gunpolitics = run_at_gunpolitics.isoformat()[:-7] + "Z"
    logging.info(f'run_at_gundeals: {run_at_gundeals}')
    logging.info(f'run_at_guns: {run_at_guns}')
    logging.info(f'run_at_progun: {run_at_progun}')
    logging.info(f'run_at_gunpolitics: {run_at_gunpolitics}')
    
    client.queue("crawl-subreddit", args=('gundeals',), queue="crawl-subreddits", reserve_for=3600, at=run_at_gundeals)
    client.queue("crawl-subreddit", args=('guns',), queue="crawl-subreddits", reserve_for=3600, at=run_at_guns)
    client.queue("crawl-subreddit", args=('progun',), queue="crawl-subreddits", reserve_for=3600, at=run_at_progun)
    client.queue("crawl-subreddit", args=('gunpolitics',), queue="crawl-subreddits", reserve_for=3600, at=run_at_gunpolitics)

