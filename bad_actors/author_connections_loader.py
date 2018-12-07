import pandas as pd
import sqlite3

AUTHORS_PATH = r"C:\Users\Administrator\Documents\GitHub\measurement-of-online-discussion-authenticity\bad_actors\data\input\datasets\Leadspotting\author_connections.csv"
DB_PATH = r"C:\Users\Administrator\Documents\GitHub\measurement-of-online-discussion-authenticity\bad_actors\data\input\bad_actors_Fake_News_Twitter.db"

def extract_connections_from_csv(path = AUTHORS_PATH):
    
    df = pd.read_csv(path, encoding="windows-1252", quotechar='"', delimiter=',')                
    
    db_table = 'author_friend'               
    
    conn = sqlite3.connect(DB_PATH)
    
    df.to_sql(db_table, conn, if_exists='append', index=False)
   

if __name__ == "__main__":

    extract_connections_from_csv(AUTHORS_PATH)