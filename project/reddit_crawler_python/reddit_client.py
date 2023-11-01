import requests
import logging
import time
from datetime import datetime, timedelta

# client id - _GpFjBtOXm8fys150GVlHg
# secret - 26OQ4qGAbZMiVw3xv1AYD9ahj_YJyg

''' Client class - the reddit client that will make the calls to the API '''
class Client:
    BASE_API_URL = "https://oauth.reddit.com"
    access_token = ""
    rate_limit_remaining = 600
    
    ''' Retrieve the array of up to 1000 most recent posts from the given subreddit '''
    def get_subreddit(self, subreddit_name, num_posts):

        all_posts = []
        after = None
        while True:
            response = self.execute(f'{self.BASE_API_URL}/r/{subreddit_name}/new.json', num_posts, after=after)
            if response.status_code != 200:
                break

            data = response.json()
            posts = data['data']['children']

            all_posts.extend(posts)

            after = data['data']['after']

            if after is None:
                break

        return all_posts

    ''' From the list of posts, extract and return the post ids '''
    def get_post_ids(self, subreddit_name, num_posts):
        posts = self.get_subreddit(subreddit_name, num_posts)
        post_ids = [post['data']['name'][3:] for post in posts]
        return post_ids

    ''' Given a subreddit name and post id, retrieve the post '''
    def get_post(self, subreddit_name, post_id):
        post = self.execute(f'{self.BASE_API_URL}/r/{subreddit_name}/comments/{post_id}.json')
        return post.json()

    ''' Given a subreddit name and post id, retrieve the comments of the post '''
    def get_comments(self, subreddit_name, post_id):
        response = self.execute(f'{self.BASE_API_URL}/r/{subreddit_name}/comments/{post_id}.json')
        comments_data = response.json()
        comments_list = comments_data[1]['data']['children']
        return comments_list

    ''' The code that is actually making the API call, done using OAuth connection '''
    def execute(self, url, limit=10, after=None):
        params = {
                'limit': limit,
                'after': after
        }
        headers = {"Authorization": f"bearer {self.access_token}", "User-Agent": "team_brandon_app:v1.0.0 by /u/TEAM_BRANDON;"}
        if self.rate_limit_remaining <= 5:
            print(f'almost exceeding: {self.rate_limit_remaining}')
            time.sleep(60)
        response = requests.get(url, headers=headers, params=params)
        self.rate_limit_remaining = float(response.headers.get('X-Ratelimit-Remaining', -1))

        if response.status_code == 429:
            self.setup_OAuth()
            response = requests.get(url, headers=headers, params=params)
        return response

    ''' Establishing the initial OAuth connection, will be called again if token expires for some reason '''
    def setup_OAuth(self):
        print('setting up OAuth')
        client_auth = requests.auth.HTTPBasicAuth('_GpFjBtOXm8fys150GVlHg', '26OQ4qGAbZMiVw3xv1AYD9ahj_YJyg')
        post_data = {"grant_type": "password", "username": "TEAM_BRANDON", "password": "fuckthe2a"}
        headers = {"User-Agent": "team_brandon_app:v1.0.0 by /u/TEAM_BRANDON;"}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
        token_json = response.json()
        self.access_token = token_json["access_token"]
        return
