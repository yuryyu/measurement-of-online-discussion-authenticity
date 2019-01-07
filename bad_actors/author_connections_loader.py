from __future__ import print_function
import pandas as pd
import json
import sqlite3

AUTHORS_PATH = r"E:\all_temp_author_connections.csv"
JSON_PATH = r"C:\Users\Developer_1\Documents\friendships.json"
AUTHORS_CSV_PATH = r"E:\authors_293_2.csv"
DB_PATH = r"E:\TR1_twitter_293(1).db"

def extract_connections_from_csv(path = AUTHORS_PATH):
    
    df = pd.read_csv(path, encoding="windows-1252", quotechar='"', delimiter=',')

    db_table = 'author_friend'               
    
    conn = sqlite3.connect(DB_PATH)
    
    df.to_sql(db_table, conn, if_exists='append', index=False)

def extract_connections_from_csv_in_chunks(path = AUTHORS_PATH):
    chunksize = 10000
    i = 0
    num_rows = pd.read_csv(path, encoding="windows-1252", quotechar='"', delimiter=',').shape[0]/chunksize
    for chunk in pd.read_csv(path, encoding="windows-1252", quotechar='"', delimiter=',', chunksize=chunksize):
        i += 1
        print('\rChunk [{}/{}]'.format(i, num_rows), end='')
        db_table = 'temp_author_connections_from_csv'
        conn = sqlite3.connect(DB_PATH)
        chunk.to_sql(db_table, conn, if_exists='append', index=False)
    conn.commit()
    print('\r')


def extract_authors_from_csv(path = AUTHORS_CSV_PATH):
    i = 0
    df = pd.read_csv(path, encoding="utf-8", quotechar='"', delimiter=',')
    num_rows = df.shape[0]
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = 'insert or ignore into authors values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?' \
            ',?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);'
    for row in df.itertuples():
        print('\rRow [{}/{}]'.format(i, num_rows), end='')
        i += 1
        cur.execute(query, row[1:])
    conn.commit()
    print('\r')

def temp_connections_from_csv_if_not_exist(path = AUTHORS_CSV_PATH):
    i = 0
    df = pd.read_csv(path, encoding="utf-8", quotechar='"', delimiter=',')
    num_rows = df.shape[0]
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = "insert or ignore into temp_author_connections values (?,?,?,?,?);"
    for row in df.itertuples():
        print('\rRow [{}/{}]'.format(i, num_rows), end='')
        i += 1
        cur.execute(query, row[1:])
    conn.commit()
    print('\r')

def imp_json():    
    auth_cons = json.load(open(JSON_PATH))
    db = sqlite3.connect(DB_PATH)    
    query = "insert or ignore into temp_author_connections values (?,?,?,?,?)"
    con_types = ['follower', 'friend']
    c = db.cursor()
    i = 0
    num_conns = len(auth_cons)
    for auth, data in auth_cons.iteritems():
        if i % 10 == 0:
            print('\rConnection [{}/{}]'.format(i, num_conns), end='')
        i += 1
        for con_type in con_types:            
            for con in data[con_type+'s_ids']:
                keys = (auth,str(con),con_type,0.0,'2018-12-27 00:00:00')               
                c.execute(query, keys)
    print('\r')
    db.commit()
    db.close()



if __name__ == "__main__":

    #extract_connections_from_csv_in_chunks(AUTHORS_PATH)
    #extract_authors_from_csv(AUTHORS_CSV_PATH)
    #imp_json()
    temp_connections_from_csv_if_not_exist(AUTHORS_PATH)
    print('Done!')