

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

csvfile='\\\\localhost\\C$\\Installation\\csv_file1.csv'

url="http://www.rba.gov.au/statistics/tables/csv/f17-yields.csv"

import urllib
# csvfile1 = urllib.URLopener()
# csvfile1.retrieve(url, csvfile)

# import csv
# with open(csvfile, 'rb') as csvfile:
#     csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#     data_list=list(csvreader)
#     header_line=list(data_list[0])
#     print(header_line)
    
try:          
    with sqlite3.connect(db_path_file) as con:
#         cur = con.cursor()
        
        import pandas
        df = pandas.read_csv(url)
        df.to_sql("campaigns_data", con, if_exists='append', index=False) 
#         for ll in range(1,len(data_list)) :            
#             cur.execute("INSERT INTO campaigns_data (campaign_id, tweet_ID, parent_tweet_ID, url, author, text, date, retweets ) VALUES (?,?,?,?,?,?,?,?)",
#                         (int(data_list[ll][0]),# (int(request.json['campaign_id']),
#                         data_list[ll][1],# request.json['tweet_ID'],
#                         data_list[ll][2],# request.json['parent_tweet_ID'],
#                         data_list[ll][3],# request.json['url'],
#                         data_list[ll][4],# request.json['author'],
#                         data_list[ll][5],# request.json['text'],
#                         data_list[ll][6],# request.json['date'],
#                         int(data_list[ll][7])))# int(request.json['retweets'])))                             
#             con.commit()
        
            #logging.info("Records successfully added")



# try:          
#     with sqlite3.connect(db_path_file) as con:
#         cur = con.cursor()              
#         cur.execute("select * from campaigns_list where campaign_id={}".format(4))    
#         campaign = cur.fetchall();
#         if len(campaign) == 0:
#         
#             print "Record unsuccessfully updated"
        
except:
    con.rollback()
    print "Error in insert operation"                   
finally:           
    con.close()
            
print "Done"            
            
            
            
            
            
            