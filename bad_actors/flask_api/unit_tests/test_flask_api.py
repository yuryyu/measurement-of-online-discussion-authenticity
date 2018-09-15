import unittest
import requests
import json
import sys
import os

sys.argv.append('configuration/config_api.ini')
os.environ['HOME'] = "C:\\Users\\yuzba\\Documents\\GitHub\\measurement-of-online-discussion-authenticity\\bad_actors"

from flask_api.validate_json import validate_json
from flask_api.flask_api import app


json_file = 'configuration/config_api.json'
with open(json_file, 'r') as f:
    json_config = json.load(f)
test_data = json_config['test_data']


class TestIntegrations(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_add_campaign(self):
        with app.app_context():
            response1 = self.app.post('http://localhost:5000/api/v1/campaigns/add', data=json.dumps(test_data[0]),
                                     headers={'Content-type': 'application/json'})
            response2 = self.app.post('http://localhost:5000/api/v1/campaigns/add', data=json.dumps(test_data[1]),
                                      headers={'Content-type': 'application/json'})
            response3 = self.app.post('http://localhost:5000/api/v1/campaigns/add', data=json.dumps(test_data[2]),
                                      headers={'Content-type': 'application/json'})
            assert response1.status_code == requests.codes.ok
            response_dict = json.loads(response1.data)
            assert isinstance(response_dict['campaign_id'], int)
            self.assertTrue(validate_json(test_data[0]))
            assert 'error' in json.loads(response2.data).keys()
            assert 'error' in json.loads(response3.data).keys()


    def test_query(self):
        with app.app_context():
            response = self.app.get('http://localhost:5000/api/v1/campaigns/{0}/status'.format('100'))
            response_dict = json.loads(response.data)
            assert response.status_code == requests.codes.ok
            assert isinstance(response_dict['status'], (str, unicode))
            assert isinstance(response_dict['fake_news_score'], (int, long, float, complex))
            bad_response = response = self.app.get('http://localhost:5000/api/v1/campaigns/{0}/status'.format('29999'))
            assert "error" in json.loads(bad_response.data).keys()

