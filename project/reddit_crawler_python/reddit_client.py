import requests
import logging
import time
from datetime import datetime, timedelta

# client id - _GpFjBtOXm8fys150GVlHg
# secret - 26OQ4qGAbZMiVw3xv1AYD9ahj_YJyg

class Client:
    BASE_API_URL = "https://oauth.reddit.com"
    #BASE_API_URL = "https://www.reddit.com"
    access_token = ""
    rate_limit_remaining = 600

    def get_subreddit(self, subreddit_name, num_posts):

        all_posts = []
        after = None
        while True:
            #print('new request')
            response = self.execute(f'{self.BASE_API_URL}/r/{subreddit_name}/new.json', num_posts, after=after)
            #time.sleep(10)
            if response.status_code != 200:
                break

            data = response.json()
            posts = data['data']['children']

            all_posts.extend(posts)

            after = data['data']['after']

            if after is None:
                break

        #print(response.json())
        
        #print(type(response.json()['data']['children']))
        '''
        count = 1
        for post in all_posts:
            created_utc = post['data']['created_utc']

            print(f'id: {count}, {datetime.utcfromtimestamp(created_utc)}')
            count += 1
        '''
        return all_posts
        
        '''
        # Print the titles of the fetched posts
        for post in posts:
            print(post['data']['selftext'])#['data']['title'])

        ten_hours_ago = time.time() - 36000
        recent_posts = [post for post in data['data']['children'] if post['data']['created_utc'] > ten_hours_ago]

        print(len(recent_posts))
        '''

    def get_post_ids(self, subreddit_name, num_posts):
        posts = self.get_subreddit(subreddit_name, num_posts)
        #print(posts)
        post_ids = [post['data']['name'][3:] for post in posts]
        #print(post_ids)
        return post_ids

    def get_post(self, subreddit_name, post_id):
        post = self.execute(f'{self.BASE_API_URL}/r/{subreddit_name}/comments/{post_id}.json')
        #print(post.json()[0]['data']['children'])
        #return post.json()[0]['data']['children']
        return post.json()

    def get_comments(self, subreddit_name, post_id):
        response = self.execute(f'{self.BASE_API_URL}/r/{subreddit_name}/comments/{post_id}.json')
        comments_data = response.json()
        
        #print(comments_data)
        comments_list = comments_data[1]['data']['children']
        #comments_text = [comment['data']['body'] for comment in comments_list]
        #print(comments_list)
        #print(comments_text)
        return comments_list


    def execute(self, url, limit=10, after=None):
        
        #time.sleep(1.5)
        #print(f'self access token: {self.access_token}')
        #refresh_token = token_data.get('refresh_token')
        params = {
                'limit': limit,
                'after': after
        }
        headers = {"Authorization": f"bearer {self.access_token}", "User-Agent": "team_brandon_app:v1.0.0 by /u/TEAM_BRANDON;"}
        #headers = {"User-Agent": "team_brandon_app:v1.0.0 by /u/TEAM_BRANDON;"}
        if self.rate_limit_remaining <= 5:
            print(f'almost exceeding: {self.rate_limit_remaining}')
            time.sleep(60)
        response = requests.get(url, headers=headers, params=params)
        self.rate_limit_remaining = float(response.headers.get('X-Ratelimit-Remaining', -1))

        #print(response)
        if response.status_code == 429:
            self.setup_OAuth()
            response = requests.get(url, headers=headers, params=params)
        return response

    def setup_OAuth(self):
        print('setting up OAuth')
        client_auth = requests.auth.HTTPBasicAuth('_GpFjBtOXm8fys150GVlHg', '26OQ4qGAbZMiVw3xv1AYD9ahj_YJyg')
        post_data = {"grant_type": "password", "username": "TEAM_BRANDON", "password": "fuckthe2a"}
        headers = {"User-Agent": "team_brandon_app:v1.0.0 by /u/TEAM_BRANDON;"}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
        token_json = response.json()
        self.access_token = token_json["access_token"]
        return


    '''
    def get_new_access_token(refresh_token):
        client_auth = requests.auth.HTTPBasicAuth('_GpFjBtOXm8fys150GVlHg', '26OQ4qGAbZMiVw3xv1AYD9ahj_YJyg')
        post_data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        headers = {"User-Agent": "YourBot/0.1"}
        response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
        return response.json()["access_token"]
    '''






#client = Client() 
#client.setup_OAuth()
#client.get_subreddit("gundeals", 100)
#client.get_post_ids("gundeals", 100)
#client.get_post("gunpolitics", "178fp87")
#client.get_comments("gundeals", "17a56yz")
