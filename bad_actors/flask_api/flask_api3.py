from flask import Flask, jsonify, abort, make_response, request, Response
import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging.config
import pandas
import urllib2
import json
import csv
import threading
from DB.schema_definition import *
from preprocessing_tools.abstract_executor import AbstractExecutor
import time
#import gzip


class FlaskAPI(AbstractExecutor):
    def __init__(self):
        self._db = DB()
        self._db.setUp()
        AbstractExecutor.__init__(self, self._db)
        logging.info('Setting up API...')
        self.app = Flask(__name__)
        self.campaigns_table = self._config_parser.eval(self.__class__.__name__, 'campaigns_table')
        self.campaigns_data_table = self._config_parser.eval(self.__class__.__name__, 'campaigns_data_table')
        self.friends_table = self._config_parser.eval(self.__class__.__name__, 'friends_table')
        self.followers_table = self._config_parser.eval(self.__class__.__name__, 'followers_table')
        self.encoding = self._config_parser.eval(self.__class__.__name__, 'encoding')
        self.csv_source_type = self._config_parser.eval(self.__class__.__name__, 'csv_source_type')
        self.add_routes()
        self.add_error_handlers()

    def execute(self, window_start=None):
        host = self._config_parser.eval(self.__class__.__name__, 'host')
        debug = self._config_parser.eval(self.__class__.__name__, 'debug')
        self.app.run(debug=debug, host=host)

    def check_campaignID(self, campaign_id):
        #campaign = self._db.get_campaign_by_id(campaign_id)
        try:
            campaign = self._db.get_campaign_by_id(campaign_id)
            #campaign = self._db.session.query(Campaign).filter(Campaign.campaign_id == campaign_id).all()
            if len(campaign) == 0:
                logging.info("Record for campaign_id not found!")
                return False
            logging.info("Record for campaign_id successfully read")
        except:
            logging.error("Error in campaign_id read operation")
            return False
        return True

    def download_csv(self, url):
        try:
            if self.csv_source_type == 'local':
                f = open(url, 'rb')
                return f
            if self.csv_source_type == 'url':
                data = urllib2.urlopen(url)
                return data
        except:
            logging.info('Download csv failed')
            abort(401)

    def add_campaigns_data_from_csv(self, f):
        try:
            reader = csv.DictReader(f)
            for row in reader:
                campaign_d = CampaignData()
                campaign_d.campaign_id = int(row['campaign_id'])
                campaign_d.tweet_id = unicode(row['tweet_id'])
                campaign_d.parent_tweet_id = unicode(row['parent_tweet_id'])
                campaign_d.author_id = unicode(row['author_id'])
                campaign_d.text = unicode(row['text'])
                campaign_d.date = unicode(row['date'])
                campaign_d.retweets = int(row['retweets'])
                campaign_d.post_favorites = int(row['post_favorites'])
                campaign_d.author_followers = int(row['author_followers'])
                campaign_d.author_friends = int(row['author_friends'])
                campaign_d.url = unicode(row['url'])
                self._db.add_campaign_data(campaign_d)
                #campaigns_data.append(campaign_d)
        except:
            logging.info('Insert to DB operation failed')
            abort(406)

    def add_friends_or_followers_from_csv(self, f, c_type):
        try:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                self._db.add_author_follower_or_friend(row, c_type)
        except:
            abort(406)

    def download_all_csvs(self, req):
        camp_file = self.download_csv(req.json['csv_url'])
        self.add_campaigns_data_from_csv(camp_file)

        if self.ifexist(req, 'csv_friends'):
            friends_file = self.download_csv(req.json['csv_friends'])
            self.add_friends_or_followers_from_csv(friends_file, 'author_friend')
            
        if self.ifexist(req, 'csv_followers'):
            friends_file = self.download_csv(req.json['csv_followers'])
            self.add_friends_or_followers_from_csv(friends_file, 'author_follower')

    def run_function(self, campaign_id):
        run_command_ex = '"' + self._config_parser.get(self.__class__.__name__, 'predictor_path') \
                         + self._config_parser.get(self.__class__.__name__, 'predictor_config_path') \
                         + str(campaign_id) + '"'
        logging.info("Prediction started for campaign " + str(campaign_id))
        os.system(run_command_ex)
        logging.info("Prediction ended for campaign " + str(campaign_id))

    def ifexist(self, req, field):
        try:
            req.json[field]
            return True
        except:
            pass
            return False

    def checkJson(self, s):
        try:
            json.loads(s)
            return True
        except:
            return False

    def add_routes(self):
        # add campaign from csv to campaings_list table and in database
        @self.app.route('/api/v1/campaigns/add_campaign/', methods=['POST'])
        def add_campaign():
            if not request.json:
                abort(400)
            #if not self.checkJson(request.json):
            #    abort(400)
            if request.method == 'POST':
                # check if campaign id exist
                if not self.check_campaignID(request.json['campaign_id']):
                    logging.info("Campaign does not exist, adding campaign")
                    # add data to campaign_data table
                    self.download_all_csvs(request)
                else:
                    abort(409)
                # add data to campaigns table
                try:
                    campaign = Campaign()
                    campaign.campaign_id = int(request.json['campaign_id'])
                    campaign.insertion_date = u"{}".format(datetime.datetime.now())
                    #campaign.insertion_date = '09-11-12'
                    campaign.status = 'Init'
                    campaign.fake_news_score = 0.5
                    self._db.add_campaign(campaign)
                    logging.info("Campaign successfully added!")
                except:
                    logging.info("Error in add new campaign")
                    abort(406)
            return jsonify({'Added data for campaign_id': request.json['campaign_id']})

        # add campaign to campaings_list table in database
        @self.app.route('/api/v1/campaigns/add2list/', methods=['POST'])
        def add2list():
            if not request.json:
                abort(400)
            if request.method == 'POST':
                self.download_all_csvs(request)
                try:
                    campaign = Campaign()
                    campaign.campaign_id = int(request.json['campaign_id'])
                    campaign.title = request.json['title']
                    campaign.category = request.json['category']
                    campaign.campaign_date = request.json['class']
                    campaign.campaign_date = request.json['date']
                    campaign.insertion_date = u"{}".format(datetime.datetime.now())
                    #campaign.insertion_date = '19-12-16'
                    campaign.status = 'Init'
                    campaign.fake_news_score = 0.5
                    self._db.add_campaign(campaign)
                    logging.info("Record successfully added")
                except:
                    logging.info("Error in insert operation")
                    abort(400)
            return jsonify({'Added to campaigns table campaign_id': request.json['campaign_id']})

        # add campaign data to campaings_data table in database
        @self.app.route('/api/v1/campaigns/add_data/', methods=['POST'])
        def add_data():
            if not request.json:
                abort(400)
            if request.method == 'POST':
                if not self.check_campaignID(request.json['campaign_id']):
                    logging.error("Error in check campaign id")
                    abort(410)
                logging.info(request.json)
                if request.method == 'POST':
                    try:
                        campaign_data = CampaignData()
                        campaign_data.campaign_id = int(request.json['campaign_id'])
                        campaign_data.tweet_id = request.json['tweet_id']
                        campaign_data.parent_tweet_id = request.json['parent_tweet_id']
                        campaign_data.url = request.json['url']
                        campaign_data.author_id = request.json['author_id']
                        campaign_data.text = request.json['text']
                        campaign_data.date = request.json['date']
                        campaign_data.retweets = int(request.json['retweets'])
                        campaign_data.post_favorites = int(request.json['post_favorites'])
                        campaign_data.author_followers = int(request.json['author_followers'])
                        campaign_data.author_friends = int(request.json['author_friends'])
                        self._db.add_campaign_data(campaign_data)
                        logging.info("Record successfully added")
                    except:
                        logging.info("error in insert operation2")
                        abort(400)
            return jsonify({'Added data to campaigns_data table campaign_id': request.json['campaign_id']})

        # run Analyzer
        @self.app.route('/api/v1/run_analyze/<int:campaign_id>')
        def run_analyze(campaign_id):
            if not self.check_campaignID(campaign_id):
                logging.error("Error in data read operation")
                abort(410)
            try:
                prediction_run_thread = threading.Thread(target=self.run_function, name="Thread-1", args=[campaign_id])
                # check for running and reject if running
                if not prediction_run_thread.isAlive():
                    logging.info("Prediction run started")
                    prediction_run_thread.start()
                else:
                    abort(500)
            except:
                logging.info("Error in Analyzer run operation")
                abort(500)
            return jsonify({'Analyzer started for campaign_id: ': campaign_id})

        # check campaign status
        @self.app.route('/api/v1/campaigns/<int:campaign_id>/status', methods=['GET'])
        def check_status(campaign_id):
            if not self.check_campaignID(campaign_id):
                logging.error("Error in check campaign_id")
                abort(410)
            try:
                campaign = self._db.get_campaign_by_id(campaign_id)[0]
                logging.info("Record " + str(campaign_id) + " successfully read")
            except:
                logging.error("Error check status read operation")
                abort(500)
            return jsonify({'Campaign ID': campaign.campaign_id, 'Campaign Title': campaign.title,
                            'Status': campaign.status})

        # check campaign status
        @self.app.route('/api/v1/campaigns/<int:campaign_id>/labeling', methods=['GET'])
        def labeling(campaign_id):
            if not self.check_campaignID(campaign_id):
                logging.error("Error 1in data read operation")
                abort(410)
            try:
                campaign = self._db.get_campaign_by_id(campaign_id)[0]
                logging.info("Record " + str(campaign_id) + " successfully read")
            except:
                logging.error("Error check status read operation")
            return jsonify({'Campaign ID': campaign.campaign_id, 'Campaign Title': campaign.title,
                            'Category': campaign.category, 'Class': campaign.campaign_class,
                            'Campaign date': campaign.campaign_date,
                            'Insertion date': campaign.insertion_date,
                            'Fake_news_score': campaign.fake_news_score,
                            "Labeling_csv": "intelici.net:5000/output/authors_labeling_" + str(
                            campaign.campaign_id) + ".csv"})

    def add_error_handlers(self):
        # error handlers
        @self.app.errorhandler(400)
        def invalid_input(error):
            return make_response(jsonify({'error': 'Invalid input, object invalid'}), 400)

        @self.app.errorhandler(401)
        def invalid_csv(error):
            return make_response(jsonify({'error': 'Invalid scv url or file empty, can not be downloaded'}), 401)

        @self.app.errorhandler(404)
        def not_found(error):
            return make_response(jsonify({'error': 'Not found!'}), 404)

        @self.app.errorhandler(406)
        def data_warning(error):
            return make_response(jsonify({'warning': 'Data can not be stored in DB'}), 406)

        @self.app.errorhandler(409)
        def object_exists(error):
            return make_response(jsonify({'error': 'Item already exists'}), 409)

        @self.app.errorhandler(410)
        def campaign_non_exists(error):
            return make_response(jsonify({'error': 'Campaign does not exist'}), 410)

        @self.app.errorhandler(500)
        def internal_error(error):
            return make_response(jsonify({'error': 'Internal analyzer error'}), 500)

        @self.app.errorhandler(501)
        def thread_error(error):
            return make_response(jsonify({'error': 'Previos analyzer run is not ended'}), 501)


if __name__ == '__main__':
    api = FlaskAPI()
    api.execute()



'''
db_path_file_BU = db_path_file.replace(".db", "BACKUP{}.db".format(datetime.datetime.now()).replace(':',"-").replace(" ","-"))

if os.path.exists(db_path_file) and back_up :
    os.rename(db_path_file, db_path_file_BU )
    logging.info("For existing DB made backup: " +db_path_file_BU)
'''
'''
if from_scratch:
    if os.path.exists(db_path_file):
        os.remove(db_path_file)
    run_command_ex='{}\\run.py configuration\config_leadspotting_init_DB.ini'.format(project_folder) 
    os.system(run_command_ex)    
    conn = sqlite3.connect(db_path_file)
    logging.info("Database created successfully")  
    conn.close()
    logging.info("Init DB is done!")
else:
    conn = sqlite3.connect(db_path_file)
    logging.info("Database opened successfully")
    conn.close()
    logging.info("DB check is done!")
'''
'''
def delete_table(table_name):    
    try:          
        with sqlite3.connect(db_path_file) as con:
            con.row_factory = sqlite3.Row            
            cur = con.cursor()
            cur.execute("delete from "+ table_name)    
            con.close()                
            logging.info("Deleted table succesfully")
            return True
    except:
        logging.error("Error in table deleting operation")                    
        con.close()
        return False
    return True
'''




# this takes the file name and returns if exists, otherwise notifies it is not yet done



'''
@app.route('/output/<name>')
def get_output_file(name):
    OUTPUT_DIR="\\\\localhost\\C$\\output\\"
    file_name = os.path.join(OUTPUT_DIR, name)
    logging.info(file_name)
    if not os.path.isfile(file_name):
        return jsonify({"message": "still processing"})
    # read without gzip.open to keep it compressed
    with open(file_name, 'rb') as f:
        resp = Response(f.read())
        #resp = make_response(f.read())
    logging.info("File successfully read")
    # set headers to tell encoding and to send as an attachment
    #resp.headers["Content-Encoding"] = 'gzip' - enable if you wont use gzip
    resp.headers["Content-Disposition"] = "attachment; filename={0}".format(name)
    resp.headers["Content-type"] = "text/csv"
    logging.info(resp)
    return resp
'''
