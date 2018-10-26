from configuration.config_class import getConfig
import logging
import csv
import json
import requests

api_url = 'http://{}:5000'.format(getConfig().get('API', 'IP'))
add_data_url = api_url + '/api/v1/campaigns/add_data/'
add_campaign_url = api_url + '/api/v1/campaigns/new_campaign/'


def post_csv(url):
    response = requests.get(url)
    assert response.status_code == requests.codes.ok
    text = response.iter_lines()
    reader = csv.reader(text, delimiter=',')
    columns = next(reader)
    posts_dict = {'tweets': []}
    failed_count = 0
    succeeded_count = 0
    blank_rows_count = 0
    for row in reader:
        if not ''.join(row).strip():
            blank_rows_count += 1
            continue
        try:
            original_dict = dict(zip(columns, row))
            new_dict = {}
            new_dict['campaign_id'] = int(original_dict.pop('campaign_id'))
            new_dict['tweet_ID'] = original_dict.pop('tweetId')
            new_dict['parent_tweet_ID'] = original_dict['parentTweet']
            new_dict['url'] = original_dict.pop('postUrl')
            new_dict['user_id'] = original_dict.pop('userId')
            new_dict['author'] = original_dict.pop('name')
            new_dict['text'] = original_dict.pop('title')
            new_dict['date'] = original_dict.pop('DATE')
            new_dict['retweets'] = 0
            extra_fields = original_dict
            posts_dict['tweets'].append(new_dict)
            succeeded_count += 1
        except ValueError as e:
            logging.warn(e)
            failed_count += 1
    headers = {'content-type': 'application/json'}
    logging.info('{} rows parsed successfully'.format(succeeded_count))
    logging.info('{} rows failed'.format(failed_count))
    logging.info('{} blank row'.format(blank_rows_count))
    try:
        r = requests.post(add_data_url, data=json.dumps(posts_dict), headers=headers)
        logging.info('Data successfully posted to server')
        logging.info('Response from server -  {}'.format(r.text))
    except requests.exceptions.RequestException as e:
        logging.warn(e)