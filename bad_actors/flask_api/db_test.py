

import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging.config

# setup
project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.info('Setting up API...')

''' DB Init Part '''
import sqlite3
from_scrach = False
db_path_file = '{}\\data\\input\\database.db'.format(project_folder)
# Delete database file if it exists - case new installation
if os.path.exists(db_path_file) and from_scrach :
    os.remove(db_path_file)
    
    os.rename(db_path_file, db_path_file.replace(".db", "BACKUP{}.db".format(datetime.datetime.now())))
    conn = sqlite3.connect(db_path_file)
    print "Database created successfully"    
    #TODO if tables doesn't exist - create 
    #conn.execute('DELETE TABLE compaigns_list')
    #conn.execute('DELETE TABLE compaigns_data')
    # TODO - take table headers from csv or some external source - not hard coded
    conn.execute('CREATE TABLE campaigns_list (campaign_id INTEGER PRIMARY KEY, title TEXT, timestamp DATETIME, status TEXT, score FLOAT)')
    conn.execute('CREATE TABLE campaigns_data (campaign_id INTEGER, tweet_ID TEXT, parent_tweet_ID, url TEXT, author TEXT, text TEXT, data DATA, retweets INTEGER)')
    logging.info("Tables created successfully")
    conn.close()
    logging.info("Init DB is done")
else:
    conn = sqlite3.connect(db_path_file)
    print "Database opened successfully"
    conn.close()
    print "DB check is done"
import random
print random.random()


try:          
    with sqlite3.connect(db_path_file) as con:
        cur = con.cursor()              
        cur.execute("select * from campaigns_list where campaign_id={}".format(4))    
        campaign = cur.fetchall();
        if len(campaign) == 0:
        
            print "Record unsuccessfully updated"
        
except:
    con.rollback()
    print "Error in insert operation"                   
finally:           
    con.close()
            
print "Done"            
            
            
            
            
            
            