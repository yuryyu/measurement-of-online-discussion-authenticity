from flask import Flask, jsonify, abort, make_response, request, Response
import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging.config
from configuration.config_class import getConfig
import urllib
import pandas
import threading

import time
#import gzip

# setup
project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.config.fileConfig(getConfig().get("DEFAULT", "Logger_conf_file"))
logging.info('Setting up API...')
app = Flask(__name__)

''' DB Init Part '''
import sqlite3
from_scrach = True
back_up = False
db_path_file = '{}\\data\\input\\Leadspotting_twitter_database.db'.format(project_folder)
db_table1_campaigns      = "campaigns"
db_table2_campaigns_data = "campaigns_data"
db_table3                = "author_friend"  
db_table4                = "author_follower"
db_path_file_BU = db_path_file.replace(".db", "BACKUP{}.db".format(datetime.datetime.now()).replace(':',"-").replace(" ","-"))

if os.path.exists(db_path_file) and back_up :
    os.rename(db_path_file, db_path_file_BU )
    logging.info("For existing DB made backup: " +db_path_file_BU)

if from_scrach :
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


def check_campaignID(campaign_id):    
    try:          
        with sqlite3.connect(db_path_file) as con:
            con.row_factory = sqlite3.Row            
            cur = con.cursor()
            cur.execute("select * from "+db_table1_campaigns+" where campaign_id={}".format(campaign_id))    
            campaign = cur.fetchall();
            if len(campaign) == 0:                
                logging.info("Record for campaign_id not found!")                
                con.close()
                return False
            logging.info("Record for campaign_id successfully read")
    except:
        logging.error("Error in campaign_id read operation")                    
        con.close()
        return False
    return True

def dwnload_csv_db(db_path_file, db_table, scv_url):
    sts=0
    try:          
        with sqlite3.connect(db_path_file) as con:            
            if scv_url != '':
                logging.info("Adding csv file")           
#                 df = pandas.read_csv(scv_url, encoding="windows-1252", quotechar='"', delimiter=',')
                df = pandas.read_csv(scv_url, encoding='utf-8', quotechar='"', delimiter=',')      
                logging.info("Reading csv file") 
                df.to_sql(db_table, con, if_exists='append', index=False)
                logging.info("Added data from csv file")
            else:
                sts=406 # invalid scv url or empty                                  
    except:       
        con.close()
        logging.info("Error in scv download or insert to DB operation")
        sts=401 # invalid scv url or file format                    
    finally:           
        con.close() 
    return sts

def run_function(campaign_id):              
    run_command_ex='"{}\\prediction.py configuration\config_prediction.ini {}"'.format(project_folder,campaign_id)       
    logging.info("Prediction started for campaign "+str(campaign_id))           
    os.system(run_command_ex)
    logging.info("Prediction ended for campaign "+str(campaign_id))

def ifexist(request,field):
    try:
        request.json[field]
        return True
    except:
        pass
        return False 
    
def update_claim_id(db_table,claim_id):    
    
    try:          
        with sqlite3.connect(db_path_file) as con:
            logging.info("Start Update table ")
            con.row_factory = sqlite3.Row            
            cur = con.cursor()
            cur.execute("UPDATE "+db_table+" SET claim_id="+str(claim_id))                           
            logging.info("Update table is succesfully")
            
    except:
        logging.error("Error in table update operation")                    
        
    
def dld_csv_with_check(request):
    
    rez=dwnload_csv_db(db_path_file, db_table2_campaigns_data, request.json['csv_url'])
    logging.info("Rez 1 for "+str(rez))
    if rez>0:
        return rez          
    
    if ifexist(request,'csv_url_friends'):
        
        rez=dwnload_csv_db(db_path_file, db_table3, request.json['csv_url_friends'])
        logging.info("Rez 2 for "+str(rez))
        if rez>0:            
            delete_table(db_table2_campaigns_data)
            return rez
        else:
            update_claim_id(db_table3,request.json['campaign_id'])
                         
             
    if ifexist(request,'csv_url_followers'):
        rez=dwnload_csv_db(db_path_file, db_table4, request.json['csv_url_followers'])
        logging.info("Rez 3 for "+str(rez))
        if rez>0:            
            delete_table(db_table2_campaigns_data)
            delete_table(db_table3)
            return rez
        else:
            update_claim_id(db_table4,request.json['campaign_id'])
             
    return 0
    
          
        
# add campaign from csv to campaings_list table and in database 
@app.route('/api/v1/campaigns/add_campaign/', methods=['POST'])
def add_campaign():
    if not request.json: abort(400)    
    if request.method == 'POST':
        # check if campaign id exist
        if not check_campaignID(request.json['campaign_id']):
            logging.info("Campaign does not exist")
            # add data to campaign_data table
            rez=dld_csv_with_check(request)
            if rez>0: abort(rez)
        # add data to campaigns table
        try:          
            with sqlite3.connect(db_path_file) as con:
                cur = con.cursor()              
                cur.execute("INSERT INTO "+db_table1_campaigns+" (campaign_id, title, category, campaign_class, campaign_date, insertion_date, status, fake_news_score) VALUES (?,?,?,?,?,?,?,?)",
                            (int(request.json['campaign_id']),'Unknown','Unknown','Unknown','Unknown',"{}".format(datetime.datetime.now()),'Init',0.5))                              
                con.commit()                    
                logging.info("Campaign successfully added!")                
        except:                
            logging.info("Error in add new campaign")       
        finally:           
            con.close()               
    return jsonify({'Added data for campaign_id': request.json['campaign_id']})

# add campaign to campaings_list table in database 
@app.route('/api/v1/campaigns/add2list/', methods=['POST'])
def add2list():
    if not request.json:
        abort(400)          
    if request.method == 'POST':       
        rez=dld_csv_with_check(request)
        if rez>0: abort(rez)      
        try:          
            with sqlite3.connect(db_path_file) as con:
                cur = con.cursor()              
                cur.execute("INSERT INTO "+db_table1_campaigns+" (campaign_id, title, category, campaign_class, campaign_date, insertion_date, status, fake_news_score) VALUES (?,?,?,?,?,?,?,?)",
                            (int(request.json['campaign_id']),request.json['title'],request.json['category'],request.json['class'],request.json['date'],
                            "{}".format(datetime.datetime.now()),'Init',0.5))                              
                con.commit()
                logging.info("Record successfully added")            
        except:
            con.rollback()
            logging.info("Error in insert operation")
            abort(409)                    
        finally:           
            con.close()                   
    return jsonify({'Added to campaigns table campaign_id': request.json['campaign_id']})

# add campaign data to campaings_data table in database 
@app.route('/api/v1/campaigns/add_data/', methods=['POST'])
def add_data():
    if not request.json:
        abort(400)
    if request.method == 'POST':    
        if not check_campaignID(request.json['campaign_id']):
            logging.error("Error in check campaign id")
            abort(410)                
        logging.info(request.json)        
        if request.method == 'POST':
            try:          
                with sqlite3.connect(db_path_file) as con:
                    cur = con.cursor()              
                    cur.execute("INSERT INTO "+db_table2_campaigns_data+" (campaign_id, tweet_id, parent_tweet_id, url, author_id, text, date, retweets, post_favorites, author_followers, author_friends) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                                (int(request.json['campaign_id']),request.json['tweet_id'],request.json['parent_tweet_id'],
                                 request.json['url'],request.json['author_id'],request.json['text'],request.json['date'],
                                 int(request.json['retweets']),int(request.json['post_favorites']),int(request.json['author_followers']),
                                 int(request.json['author_friends'])))
                                                 
                    con.commit()
                    logging.info("Record successfully added")
            except:
                con.rollback()
                logging.info("error in insert operation2")
                abort(400)        
            finally:           
                con.close()    
    return jsonify({'Added data to campaigns_data table campaign_id': request.json['campaign_id']})

#run Analyzer
@app.route('/api/v1/run_analyze/<int:campaign_id>')
def run_analyze(campaign_id):
    if not check_campaignID(campaign_id):
        logging.error("Error in data read operation")
        abort(410)         
    try:        
        prediction_run_thread = threading.Thread(target=run_function, name="Thread-1", args=[campaign_id])
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
@app.route('/api/v1/campaigns/<int:campaign_id>/status', methods=['GET'])
def check_status(campaign_id):
    if not check_campaignID(campaign_id):
        logging.error("Error in check campaign_id")
        abort(410)       
    try:          
        with sqlite3.connect(db_path_file) as con:
            con.row_factory = sqlite3.Row            
            cur = con.cursor()
            cur.execute("select * from "+db_table1_campaigns+" where campaign_id={}".format(campaign_id))    
            campaign = cur.fetchall();            
            logging.info("Record "+str(campaign_id)+" successfully read")            
    except:       
        logging.error("Error check status read operation")              
        con.close()                
    return jsonify({'Campaign ID': campaign[0]['campaign_id'],'Campaign Title': campaign[0]['title'],                    
                    'Status': campaign[0]['status']})

# check campaign status
@app.route('/api/v1/campaigns/<int:campaign_id>/labeling', methods=['GET'])
def labeling(campaign_id):
    if not check_campaignID(campaign_id):
        logging.error("Error 1in data read operation")
        abort(410)       
    try:          
        with sqlite3.connect(db_path_file) as con:
            con.row_factory = sqlite3.Row            
            cur = con.cursor()
            cur.execute("select * from "+db_table1_campaigns+" where campaign_id={}".format(campaign_id))    
            campaign = cur.fetchall();            
            logging.info("Record "+str(campaign_id)+" successfully read")            
    except:       
        logging.error("Error check status read operation")              
        con.close()                
    return jsonify({'Campaign ID': campaign[0]['campaign_id'],'Campaign Title': campaign[0]['title'],
                    'Category': campaign[0]['category'],'Class': campaign[0]['campaign_class'], 'Campaign date': campaign[0]['campaign_date'],
                    'Insertion date': campaign[0]['insertion_date'], 'Fake_news_score': campaign[0]['fake_news_score'],
                    "Labeling_csv": "intelici.net:5000/output/authors_labeling_"+str(campaign[0]['campaign_id'])+".csv"})


# this takes the file name and returns if exists, otherwise notifies it is not yet done
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




''' Handlers Part   '''
# error handlers
@app.errorhandler(400)
def invalid_input(error):
    return make_response(jsonify({'error': 'Invalid input, object invalid'}),400)

@app.errorhandler(401)
def invalid_csv(error):
    return make_response(jsonify({'error': 'Invalid scv url or file format'}),401)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found!'}), 404)

@app.errorhandler(409)
def object_exists(error):
    return make_response(jsonify({'error': 'Item already exists'}),409)

@app.errorhandler(410)
def campaign_non_exists(error):
    return make_response(jsonify({'error': 'Campaign does not exist'}),410)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'Internal analyzer error'}), 500)

@app.errorhandler(501)
def thread_error(error):
    return make_response(jsonify({'error': 'Previos analyzer run is not ended'}), 501)

@app.errorhandler(406)
def csv_warning(error):
    return make_response(jsonify({'warning': 'Invalid scv url or empty'}), 406)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')