import pandas as pd
import sqlite3
import json

AUTHORS_PATH = r"C:\Users\Administrator\Documents\GitHub\measurement-of-online-discussion-authenticity\bad_actors\data\input\datasets\Leadspotting\author_connections.csv"
JSON_PATH = r"C:\Users\Administrator\Documents\GitHub\measurement-of-online-discussion-authenticity\bad_actors\data\input\datasets\Leadspotting\friendships.json"

DB_PATH = r"C:\Users\Administrator\Documents\GitHub\measurement-of-online-discussion-authenticity\bad_actors\data\input\TR1_twitter_293.db"

def extract_connections_from_csv(path = AUTHORS_PATH):
    
    df = pd.read_csv(path, encoding="windows-1252", quotechar='"', delimiter=',')                
    
    db_table = 'author_friend'               
    
    conn = sqlite3.connect(DB_PATH)
    
    df.to_sql(db_table, conn, if_exists='append', index=False)

def imp_json():    
    auth_cons = json.load(open(JSON_PATH))
    db = sqlite3.connect(DB_PATH)    
    query = "insert or ignore into temp_author_connections values (?,?,?,?,?)"
    con_types = ['follower', 'friend']
    c = db.cursor()
    for auth, data in auth_cons.iteritems():
        for con_type in con_types:            
            for con in data[con_type+'s_ids']:
                keys = (auth,str(con),con_type,0.0,'2018-12-27 00:00:00')               
                c.execute(query, keys)                
    db.commit()
    db.close()

if __name__ == "__main__":

    #extract_connections_from_csv(AUTHORS_PATH)
    imp_json()
    print('Done!')