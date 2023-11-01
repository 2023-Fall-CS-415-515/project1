#!/usr/bin/sh

sqlx database create
sqlx migrate run

python /reddit_app/init_reddit.py

wait-for-it.sh postgres:5432 -- python /reddit_app/reddit_crawler.py &

tail -f /dev/null