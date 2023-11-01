import faktory
import logging
from faktory import Worker
from reddit_client import Client
from datetime import datetime, timedelta
import time
import psycopg2
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
FAKTORY_URL = os.environ.get('FAKTORY_URL')
client = Client()
client.setup_OAuth()

keywords = [
    '2a', 'self defense', 'murica', 'progun', 'constitutional right', 'patriot', 'maga', 'bubba', 'come and take them',
    'shall not be infringed'
]

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

def get_post_ids_from_subreddit(subreddit_data):
    post_ids = set()
    for post in subreddit_data:#["data"]["children"]:
        post_ids.add(post["data"]["id"])
    return post_ids


def crawl_post_and_comments(subreddit, post_id):
    #client = Client()
    #post_data = json.dumps(client.get_post(subreddit, post_id)[0]['data']['selftext'].lower())
    #logging.info(f'{post_id}')

    post = client.get_post(subreddit, post_id)
    post_data = post[0]['data']['children'][0]
    comment_data = post[1]['data']['children']

    post_title = post_data['data']['title']
    #logging.info(f'{post_title}')
    post_content = post_data['data']['selftext']
    created_utc = post_data['data']['created_utc']

    post_creation_date = datetime.utcfromtimestamp(created_utc)

    #post_data = client.get_post(subreddit, post_id)[0]['data']['selftext'].lower()

    #comment_data = client.get_comments(subreddit, post_id)


    # We really want to have a connection pool!
    # check psycopg docs!!

    conn = psycopg2.connect(
        dsn=DATABASE_URL
    )

    cur = conn.cursor()
    
    '''
    # we want to use named parameters; check psycopg2 docs.
    sql = "INSERT INTO posts (subreddit, post_id, data) VALUES (%s, %s, %s) RETURNING id"
    cur.execute(sql, (subreddit, post_id, post_data))

            
    # _commit_ our transaction so that it's actually persisted
    # to the db
    conn.commit()

    # it's often useful to know the id of the newly inserted
    # row. This is so you can launch other jobs that might
    # do additional processing.
    # e.g., to classify the toxicity of a post
    db_id = cur.fetchone()[0]
    logging.info(f'Inserted DB id: {db_id}')
    '''
    cur.execute("SELECT 1 FROM posts WHERE post_id = %s", (post_id,))
    if not cur.fetchone():
        if subreddit == "gundeals" or any(word in post_content.lower() for word in keywords):
            sql = "INSERT INTO posts (subreddit, post_id, title, created, data) VALUES (%s, %s, %s, %s, %s) RETURNING id"
            cur.execute(sql, (subreddit, post_id, post_title, post_creation_date, json.dumps(post_content)))

            # _commit_ our transaction so that it's actually persisted
            # to the db
            conn.commit()

            # it's often useful to know the id of the newly inserted
            # row. This is so you can launch other jobs that might
            # do additional processing.
            # e.g., to classify the toxicity of a post
            db_id = cur.fetchone()[0]
            logging.info(f'Inserted post into DB id: {db_id}')

    # process the comments
    for comment in comment_data:
        
        try:
            comment_text = comment['data']['body']
        except KeyError:
            logging.info('Deleted Comment')
            continue

        comment_id = comment['data']['id']
        cur.execute("SELECT 1 FROM comments WHERE comment_id = %s", (comment_id,))
        if not cur.fetchone():
            if subreddit == "gundeals" or any(word in comment_text.lower() for word in keywords):
                created_utc = comment['data']['created_utc']
                comment_creation_date = datetime.utcfromtimestamp(created_utc)
                sql = "INSERT INTO comments (subreddit, post_id, comment_id, created, data) VALUES (%s, %s, %s, %s, %s) RETURNING id"
                cur.execute(sql, (subreddit, post_id, comment_id, comment_creation_date, json.dumps(comment['data']['body'])))
                conn.commit()

                # it's often useful to know the id of the newly inserted
                # row. This is so you can launch other jobs that might
                # do additional processing.
                # e.g., to classify the toxicity of a post
                db_id = cur.fetchone()[0]
                logging.info(f'Inserted comment into DB id: {db_id}')

    
            
            
            



    # now we should clean up our db stuff
    cur.close()
    # again, we really want to be using a connection pool
    conn.close()

def crawl_subreddit(subreddit, old_post_ids=[]):
    #client = Client()
    subreddit_data = client.get_subreddit(subreddit, 100)
    new_post_ids = get_post_ids_from_subreddit(subreddit_data)
    #print(len(new_post_ids))

    #new_posts = find_new_posts(set(old_post_ids), new_post_ids)
    for new_post_id in new_post_ids:#s:
        with faktory.connection(FAKTORY_URL) as faktory_client:
            time.sleep(1.5)
            logging.info(f'Rate limit remaining: {client.rate_limit_remaining}')
            if client.rate_limit_remaining <= 5:
                logging.info(f'Almost exceeding rate limit: {client.rate_limit_remaining}')
                time.sleep(600)
            faktory_client.queue("crawl-post", args=(subreddit, new_post_id), queue="crawl-posts", reserve_for=60)

    # it takes 25 minutes (1500 seconds) for the latest 1000 posts to be crawled
    # since we are crawling 4 subreddits, we should make the offset every hour or so between each to make sure they don't overlap
    # run the jobs that have been offset every 4 hours
    run_at = datetime.utcnow() + timedelta(minutes=240)
    run_at = run_at.isoformat()[:-7] + "Z"
    logging.info(f'scheduling a new subreddit crawl to run at: {run_at}')
    
    
    with faktory.connection(FAKTORY_URL) as faktory_client:
        faktory_client.queue("crawl-subreddit", args=(subreddit, list(new_post_ids)), queue="crawl-subreddits", reserve_for=3600, at=run_at)
    

if __name__ == "__main__":
    w = Worker(faktory=FAKTORY_URL, queues=["crawl-subreddits", "crawl-posts"], concurrency=10, use_threads=True)
    w.register("crawl-subreddit", crawl_subreddit)
    w.register("crawl-post", crawl_post_and_comments)
    logging.info("running?")
    w.run()


