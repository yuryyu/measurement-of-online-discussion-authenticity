from unittest import TestCase
from configuration.config_class import getConfig
import os
from flask_api.flask_api3 import FlaskAPI
from DB.schema_definition import *
import json
#from flask_api.flask_api3 import
import tempfile
import sys



class TestFlaskAPI(TestCase):
    def setUp(self):
        self.config = getConfig()
        self.api = FlaskAPI()
        self.api.setUp()
        self.app = self.api.app.test_client()
        self.campaign_id_1 = 1
        self.campaign_id_2 = 20
        self.friends_csv_path = self.config.eval('FlaskAPI', 'path_to_friends_csv')
        self.followers_csv_path = self.config.eval('FlaskAPI', 'path_to_followers_csv')
        self.campaigns_csv_path = self.config.eval('FlaskAPI', 'path_to_campaigns_csv')

    def tearDown(self):
        self.api._db.session.close()
        self.api._db.deleteDB()

    def check_post_good(self, url, dic, r):
        response = self.app.post(url, json=dic)
        if r not in response.data:
            print response.data
        assert response.status_code == 200
        assert r in response.data

    def check_post_bad(self, url, dic, code, r):
        response = self.app.post(url, json=dic)
        print response.status_code
        assert response.status_code == code
        assert r in response.data

    def check_get_good(self, url, r):
        response = self.app.get(url)
        assert response.status_code == 200
        assert r in response.data

    def check_get_bad(self, url, code, r):
        response = self.app.get(url)
        assert response.status_code == code
        assert r in response.data

    def test_flow(self):
        #Dicts to post to flask API
        campaign_json = {
            "campaign_id": self.campaign_id_1,
            "csv_friends": self.friends_csv_path,
            "csv_followers": self.followers_csv_path,
            "csv_url": self.campaigns_csv_path
        }
        campaign_json_bad_id = {
            "campaign_id": "test",
            "csv_friends": self.friends_csv_path,
            "csv_followers": self.followers_csv_path,
            "csv_url": self.campaigns_csv_path
        }
        campaign_json_bad_url = {
            "campaign_id": self.campaign_id_2,
            "csv_friends": self.friends_csv_path,
            "csv_followers": self.followers_csv_path,
            "csv_url": self.friends_csv_path
        }
        list_json = {"campaign_id": self.campaign_id_1,
                     "title": "Test campaign 5",
                     "category": "Politics",
                     "class": "False",
                     "date": "06-09-18",
                     "csv_url": self.campaigns_csv_path,
                     "csv_friends": self.friends_csv_path,
                     "csv_followers": self.followers_csv_path}
        list_json_bad_id = {"campaign_id": 'test',
                     "title": "Test campaign 5",
                     "category": "Politics",
                     "class": "False",
                     "date": "06-09-18",
                     "csv_url": self.campaigns_csv_path,
                     "csv_friends": self.friends_csv_path,
                     "csv_followers": self.followers_csv_path}
        list_json_bad_url = {"campaign_id": self.campaign_id_1,
                     "title": "Test campaign 5",
                     "category": "Politics",
                     "class": "False",
                     "date": "06-09-18",
                     "csv_url": self.followers_csv_path,
                     "csv_friends": self.friends_csv_path,
                     "csv_followers": self.followers_csv_path}
        data_json = {
            "campaign_id": self.campaign_id_1,
            "tweet_id": "190",
            "parent_tweet_id": "1",
            "url": "www.bbc.co.uk",
            "author_id": "2",
            "text": "Hello World",
            "date": "11/09/1999",
            "retweets": 1,
            "post_favorites": 0,
            "author_followers": 0,
            "author_friends": 2
        }
        data_json_bad_id = {
            "campaign_id": self.campaign_id_2,
            "tweet_id": "190",
            "parent_tweet_id": "1",
            "url": "www.bbc.co.uk",
            "author_id": "2",
            "text": "Hello World",
            "date": "11/09/1999",
            "retweets": 1,
            "post_favorites": 0,
            "author_followers": 0,
            "author_friends": 2
        }
        data_json_missing_fields = {
            "campaign_id": self.campaign_id_1,
            "tweet_id": "190",
            "parent_tweet_id": "1",
            "url": "www.bbc.co.uk",
            "retweets": 1,
            "post_favorites": 0,
            "author_followers": 0,
            "author_friends": 2
        }

        #check good requests
        self.check_post_good('/api/v1/campaigns/add_campaign/', campaign_json, 'Added data for campaign_id')
        self.check_post_good('/api/v1/campaigns/add2list/', list_json, 'Added to campaigns table campaign_id')
        self.check_post_good('/api/v1/campaigns/add_data/', data_json, 'Added data to campaigns_data table campaign_id')
        self.check_get_good('/api/v1/run_analyze/{}'.format(self.campaign_id_1), 'Analyzer started for campaign_id: ')
        self.check_get_good('/api/v1/campaigns/{}/status'.format(self.campaign_id_1), 'Campaign Title')
        self.check_get_good('/api/v1/campaigns/{}/labeling'.format(self.campaign_id_1), "Labeling_csv")

        #check bad requests
        self.check_post_bad('/api/v1/campaigns/add_campaign/', campaign_json, 409, 'Item already exists')
        self.check_post_bad('/api/v1/campaigns/add_campaign/', campaign_json_bad_id, 406, 'Data can not be stored in DB')
        self.check_post_bad('/api/v1/campaigns/add_campaign/', campaign_json_bad_url, 406, 'Data can not be stored in DB')
        self.check_post_bad('/api/v1/campaigns/add2list/', list_json_bad_id, 400, 'Invalid input, object invalid')
        self.check_post_bad('/api/v1/campaigns/add2list/', list_json_bad_url, 406, 'Data can not be stored in DB')
        self.check_post_bad('/api/v1/campaigns/add_data/', data_json_bad_id, 410, 'Campaign does not exist')
        self.check_post_bad('/api/v1/campaigns/add_data/', data_json_missing_fields, 400, 'Invalid input, object invalid')
        self.check_get_bad('/api/v1/run_analyze/{}'.format(self.campaign_id_2), 410, 'Campaign does not exist')
        self.check_get_bad('/api/v1/campaigns/{}/status'.format(self.campaign_id_2), 410, 'Campaign does not exist')
        self.check_get_bad('/api/v1/campaigns/{}/labeling'.format(self.campaign_id_2), 410, 'Campaign does not exist')

        #check data in DB
        assert len(self.api._db.get_campaign_by_id(self.campaign_id_1)) > 0
        assert len(self.api._db.get_campaign_by_id(self.campaign_id_2)) == 0
        assert len(self.api._db.session.query(AuthorFriend).all()) > 0
        assert len(self.api._db.session.query(AuthorFollower).all()) > 0

