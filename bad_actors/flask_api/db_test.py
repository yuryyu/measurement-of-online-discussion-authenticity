

import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging.config

# setup
project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path_file = '{}\\data\\input\\Leadspotting_twitter_database.db'.format(project_folder)
logging.info('Setting up API...')

''' DB Init Part '''
import sqlite3


import subprocess
 
       
        
run_command_ex='"{}\\prediction_run.bat"'.format(project_folder)        
subprocess.call(run_command_ex)
print "Prediction started"
# csvfile='\\\\localhost\\C$\\Installation\\campaigns2.csv'
# 
# 
# url="https://s3.us-east-2.amazonaws.com/vigeolabs/campaigns2.csv"
# 
# 
# #import urllib
# # csvfile1 = urllib.URLopener()
# # csvfile1.retrieve(url, csvfile)
# 
# # import csv
# # with open(csvfile, 'rb') as csvfile:
# #     csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
# #     data_list=list(csvreader)
# #     header_line=list(data_list[0])
# #     print(header_line)
#     
# try:          
#     with sqlite3.connect(db_path_file) as con:
# #         cur = con.cursor()
#         
#         import pandas
#         
#         df = pandas.read_csv(csvfile, encoding="windows-1252", quotechar='"', delimiter=',')
#         df.to_sql("campaigns_data", con, if_exists='append', index=False) 
#         print "ss in insert operation" 
# #         for ll in range(1,len(data_list)) :            
# #             cur.execute("INSERT INTO campaigns_data (campaign_id, tweet_ID, parent_tweet_ID, url, author, text, date, retweets ) VALUES (?,?,?,?,?,?,?,?)",
# #                         (int(data_list[ll][0]),# (int(request.json['campaign_id']),
# #                         data_list[ll][1],# request.json['tweet_ID'],
# #                         data_list[ll][2],# request.json['parent_tweet_ID'],
# #                         data_list[ll][3],# request.json['url'],
# #                         data_list[ll][4],# request.json['author'],
# #                         data_list[ll][5],# request.json['text'],
# #                         data_list[ll][6],# request.json['date'],
# #                         int(data_list[ll][7])))# int(request.json['retweets'])))                             
# #             con.commit()
#         
#             #logging.info("Records successfully added")
# 
# 
# 
# 
# 
# 
# # try:          
# #     with sqlite3.connect(db_path_file) as con:
# #         cur = con.cursor()              
# #         cur.execute("select * from campaigns_list where campaign_id={}".format(4))    
# #         campaign = cur.fetchall();
# #         if len(campaign) == 0:
# #         
# #             print "Record unsuccessfully updated"
#         
# except:
#     con.rollback()
#     print "Error in insert operation"                   
# finally:           
#     con.close()
#             
print "Done"            
            
            
            
            
            
            