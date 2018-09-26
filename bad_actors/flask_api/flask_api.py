from flask import Flask, jsonify, abort, make_response, request
import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging.config
from validate_json import validate_json
from configuration.config_class import getConfig


# setup
project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.config.fileConfig(getConfig().get("DEFAULT", "Logger_conf_file"))
logging.info('Setting up API...')
app = Flask(__name__)

''' DB Init Part '''
import sqlite3
from_scrach = True
db_path_file = '{}\\data\\input\\database.db'.format(project_folder)
# Delete database file if it exists - case new installation
if os.path.exists(db_path_file) and from_scrach :
    os.remove(db_path_file)
    conn = sqlite3.connect(db_path_file)
    logging.info("Database created successfully")  
    # TODO - take table headers from csv or some external source - not hard coded
    conn.execute('CREATE TABLE campaigns_list (campaign_id INTEGER PRIMARY KEY, title TEXT, timestamp DATETIME, status TEXT, score FLOAT)')
    conn.execute('CREATE TABLE campaigns_data (campaign_id INTEGER, tweet_ID TEXT, parent_tweet_ID TEXT, url TEXT, author TEXT, text TEXT, date DATETIME, retweets INTEGER)')
    logging.info("Tables created successfully")
    conn.close()
    logging.info("Init DB is done!")
else:
    conn = sqlite3.connect(db_path_file)
    logging.info("Database opened successfully")
    conn.close()
    logging.info("DB check is done")

# add campaign to campaings_list table in database 
@app.route('/api/v1/campaigns/add2list/', methods=['POST'])
def add2list():
    if not request.json:
        abort(400)          
    if request.method == 'POST':
        try:          
            with sqlite3.connect(db_path_file) as con:
                cur = con.cursor()              
                cur.execute("INSERT INTO campaigns_list (campaign_id , title , timestamp , status , score ) VALUES (?,?,?,?,?)",
                            (int(request.json['campaign_id']),request.json['title'],
                            "{}".format(datetime.datetime.now()),'Init',0.5))                              
                con.commit()
                logging.info("Record successfully added")
        except:
            con.rollback()
            logging.info("Error in insert operation")
            abort(400)                    
        finally:           
            con.close()                   
    return jsonify({'Added to campaigns_list table campaign_id': request.json['campaign_id']})

# add campaign data to campaings_data table in database 
@app.route('/api/v1/campaigns/add_data/', methods=['POST'])
def add_data():
    if not request.json:
        abort(400)        
    logging.info(request.json)        
    if request.method == 'POST':
        try:          
            with sqlite3.connect(db_path_file) as con:
                cur = con.cursor()              
                cur.execute("INSERT INTO campaigns_data (campaign_id, tweet_ID, parent_tweet_ID, url, author, text, date, retweets ) VALUES (?,?,?,?,?,?,?,?)",
                            (int(request.json['campaign_id']),request.json['tweet_ID'],request.json['parent_tweet_ID'],
                             request.json['url'],request.json['author'],request.json['text'],request.json['date'],
                             int(request.json['retweets'])))                             
                con.commit()
                logging.info("Record successfully added")
        except:
            con.rollback()
            logging.info("error in insert operation")
            abort(400)        
        finally:           
            con.close()    
    return jsonify({'Added data to campaigns_data table campaign_id': request.json['campaign_id']})

#run Analyzer
@app.route('/api/v1/run_analyze/<int:campaign_id>')
def run_analyze(campaign_id):         
    try:
        #run_command_ex='{}\\python_run.bat {}'.format(project_folder,campaign_id) 
        #TODO - rebuild to function with return, update status in campaigns_list table 
        #os.system(run_command_ex)        
        print 'dummy..'
        import random        
        score=random.random()    
        #logging.error('Unable to run run.py')        
        with sqlite3.connect(db_path_file) as con:
            cur = con.cursor()              
            cur.execute("UPDATE campaigns_list SET timestamp='{}' , status='{}' , score='{}' WHERE campaign_id={};".format(datetime.datetime.now(),'Updated', score, campaign_id))                             
            con.commit()
            logging.info("Record successfully updated")
    except:
        con.rollback()
        logging.info("Error in update operation")
        abort(500)        
    finally:           
        con.close()      
    return jsonify({'Analyzer started for campaign_id: ': campaign_id})

# check campaign status
@app.route('/api/v1/campaigns/<int:campaign_id>/status', methods=['GET'])
def check_status(campaign_id):
    try:          
        with sqlite3.connect(db_path_file) as con:
            con.row_factory = sqlite3.Row            
            cur = con.cursor()
            cur.execute("select * from campaigns_list where campaign_id={}".format(campaign_id))    
            campaign = cur.fetchall();
            if len(campaign) == 0:
                abort(404)
            logging.info("Record successfully read")
    except:
        con.rollback()
        logging.error("Error in data read operation")    
    finally:           
        con.close()                          
    # TODO: request about status from campaigns_list table       
    return jsonify({'Campaign ID': campaign[0]['campaign_id'],'Campagn Title': campaign[0]['title'],'Data time stamp': campaign[0]['timestamp'],'Status': campaign[0]['status'], 'Fake_news_score': campaign[0]['score']})


''' Handlers Part   '''
# error handlers
@app.errorhandler(400)
def invalid_input(error):
    return make_response(jsonify({'error': 'Invalid input, object invalid'}),400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found!'}), 404)

@app.errorhandler(409)
def object_exists(error):
    return make_response(jsonify({'error': 'Item already exists'}),409)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'Internal error'}), 500)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')