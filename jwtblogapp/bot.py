from faker import Faker
from random import randint, choice
import requests
from threading import Thread


class BlogBot:
    """
    Represent a blog bot with a randomly generated number of users with their credentials and post text.
    Uses faker package for it.
    """

    def __init__(self, api_url, number_of_users=None, max_posts_per_user=None, max_likes_per_user=None):
        """
        Initialize instance of class

        :param number_of_users: Gets the number of users to generate
        :param max_posts_per_user: Gets the maximal number of posts per user to generate
        :param max_likes_per_user: Gets the maximal number of likes per user to generate
        """
        self.api_url = api_url
        self.number_of_users = number_of_users
        self.max_posts_per_user = max_posts_per_user
        self.max_likes_per_user = max_likes_per_user
        # instantiate Faker with locales
        # self.fake = Faker(['ru_RU', 'uk_UA', 'en_GB'])
        self.fake = Faker(['ru_RU'])

    def bot_logic(self):
        """
        Bot logic
        """
        # loop of random number of users
        for _ in range(self.number_of_users):
            # assign fake credentials
            username, password = self.fake.email(), self.fake.password(length=7, special_chars=False,
                                                                       digits=True, upper_case=True,
                                                                       lower_case=True)
            # send post request to API signup endpoint and create the new user and obtain the token
            payload = {'username': username, 'password': password}
            requests.post(f'{self.api_url}/api/signup', json=payload)
            # send post request to API login endpoint and and obtain the token
            response = requests.post(f'{self.api_url}/api/login', json=payload)
            token = response.json()['token']
            headers = {'Authorization': f'Bearer {token}'}
            # loop of random number of posts
            for _ in range(randint(1, self.max_posts_per_user)):
                # assign fake text
                post_text = self.fake.text(max_nb_chars=200, ext_word_list=None)
                # send post
                payload = {'post_text': post_text}
                requests.post(f'{self.api_url}/api/posts', headers=headers, json=payload)
            # loop of random number of likes
            for _ in range(randint(1, self.max_likes_per_user)):
                # get possible post's ids
                response = requests.get(f'{self.api_url}/api/posts', headers=headers)
                posts = response.json()['posts']
                post_ids = [post['post_id'] for post in posts]
                # randomly assign post id
                payload = {'post_id': choice(post_ids), 'like': 1}
                # send like rating
                requests.post(f'{self.api_url}/api/rating', headers=headers, json=payload)
            # logout user
            requests.post(f'{self.api_url}/api/logout', headers=headers)

    def background_run(self):
        """
        Run the bot logic background in thread
        """
        # instantiate Thread class with bot_logic method
        thread = Thread(target=self.bot_logic, daemon=False)
        # start the thread
        thread.start()


if __name__ == '__main__':
    ...
