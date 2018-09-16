from flask import Flask, jsonify, abort, make_response, request
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging.config
from validate_json import validate_json
from configuration.config_class import getConfig

#sys.argv.append('configuration/config_api.ini')

# setup
logging.config.fileConfig(getConfig().get("DEFAULT", "Logger_conf_file"))
logging.info('Setting up API...')
app = Flask(__name__)
try:
    sys.path.append(os.environ['HOME'])
except KeyError:
    logging.warn("Can't find environment variable 'HOME'")


# test-data because the api is not yet connected to a database
campaigns = [
    {'campaign_id': 100, 'keywords': ['test', 'testing'], 'status': 'finished prediction', 'fake_news_score': 0.5},
    {'campaign_id': 101, 'keywords': ['hello world'], 'status': 'finished prediction', 'fake_news_score': 0.9}
]


#run the API
@app.route('/api/v1/analyze')
def run_api():    
    project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run_command_ex='{}\\python_run.bat'.format(project_folder)      
    try:
        os.system(run_command_ex)
    except:
        logging.warn('Unable to run run.py')


# add campaign to database
@app.route('/api/v1/campaigns/add', methods=['POST'])
def add_campaign():
    if not request.json:
        abort(400)
    if not validate_json(request.json):
        abort(400)
    campaign = {
        'campaign_id': campaigns[-1]['campaign_id'] + 1,
        'url': request.json['url'],
        'author': request.json['author'],
        'text': request.json['text'],
        'date': request.json['date'],
        'retweets': []
    }
    for retweet in request.json['retweets']:
        rt = {
            'url': retweet['url'],
            'date': retweet['date'],
            'text': retweet['text'],
            'author': retweet['author']
        }
        campaign['retweets'].append(rt)
    campaigns.append(campaign)
    return jsonify({'campaign_id': campaign['campaign_id']})


# check campaign status
@app.route('/api/v1/campaigns/<int:campaign_id>/status', methods=['GET'])
def check_status(campaign_id):
    campaign = [campaign for campaign in campaigns if campaign['campaign_id'] == campaign_id]
    if len(campaign) == 0:
        abort(404)
    return jsonify({'status': campaign[0]['status'], 'fake_news_score': campaign[0]['fake_news_score']})


# error handlers
@app.errorhandler(400)
def invalid_input(error):
    return make_response(jsonify({'error': 'Invalid input, object invalid'}))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(409)
def object_exists(error):
    return make_response(jsonify({'error': 'Item already exists'}))


@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'Internal error'}), 500)


if __name__ == '__main__':
    app.run(debug=True)