'''
Retweet_cascade_builder
Builds retweet cascade graphs
uses tweepy API.

##################################################################################
IMPORTANT: CURRENTLY LIMITED TO 15 REQUESTS PER MINUTE BY TWITTER API, DOESN'T WORK
###################################################################################

Functions:
*get_root_tweets: gets all root tweets in a campaign.
 Parameters: campaign_id
 returns: list of tuples (tweet_id, date, user_id)

*build_retweet_cascade_graph: builds cascade graph for all retweets of a root node.
 Parameters: campaign_id, root_node
 returns: netwrkx graph of retweet cascade
'''

import networkx as nx
import sqlite3
import os
import logging.config
import sys
import datetime
import matplotlib.pyplot as plt
import tweepy
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configuration.config_class import getConfig


consumer_key = getConfig().get('tweepy_API', 'consumer_key')
consumer_secret = getConfig().get('tweepy_API', 'consumer_secret')
access_token = getConfig().get('tweepy_API', 'access_token')
access_token_secret = getConfig().get('tweepy_API', 'access_token_secret')

#setup
project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path_file = '{}\\data\\input\\database.db'.format(project_folder)
logging.config.fileConfig(getConfig().get("DEFAULT", "Logger_conf_file"))
logging.info('Connecting to Twitter API...')
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def get_root_tweets(campaign_id):
    try:
        logging.info('Getting root tweets for campaign {} from database.'.format(campaign_id))
        with sqlite3.connect(db_path_file) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            command = "SELECT tweet_ID, date, user_id from campaigns_data " \
                      "WHERE campaign_id = {} AND parent_tweet_ID = '0'".format(campaign_id)
            cur.execute(command)
            root_tweets = cur.fetchall()
            if len(root_tweets) > 0:
                logging.info('{} root tweets found for campaign {}'.format(len(root_tweets), campaign_id))
            else:
                logging.warn('No root tweets found for campaign {}'.format(campaign_id))
    except:
        con.rollback()
        logging.error("Error in data read operation")
    con.close()
    return root_tweets


def get_all_retweets(campaign_id, parent_tweet_id):
    try:
        with sqlite3.connect(db_path_file) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            command = "SELECT tweet_ID, date, user_id from campaigns_data WHERE campaign_id = '{}' " \
                      "AND parent_tweet_ID = '{}' ORDER BY date(date) ASC".format(campaign_id, parent_tweet_id)
            cur.execute(command)
            retweets = cur.fetchall()
            logging.info('{} retweets found for root tweet'.format(len(retweets)))
    except sqlite3.Error as e:
        con.rollback()
        logging.warn(e)
    con.close()
    return retweets


def could_have_retweeted(parent_tweet, tweet):
    try:
        tmp_friendship = api.show_friendship(source_id=parent_tweet[2], target_id=tweet[2])
        if tmp_friendship[0].followed_by:
            pt_time = datetime.datetime.strptime(parent_tweet[1], "%Y-%m-%d %H:%M:%S")
            t_time = datetime.datetime.strptime(tweet[1], "%Y-%m-%d %H:%M:%S")
            if pt_time < t_time:
                return True
        return False
    except tweepy.TweepError as e:
        logging.warn(e)
        return False



def loop_through_parent_tweets(tweet, possible_retweeted):
    for parent_tweet in possible_retweeted:
        if could_have_retweeted(parent_tweet, tweet):
            return parent_tweet


def loop_through_tweets_list(tweets_list, possible_retweeted, G):
    changed = False
    for tweet in tweets_list:
        parent_tweet = loop_through_parent_tweets(tweet, possible_retweeted)
        if parent_tweet:
            G.add_edge(parent_tweet[0], tweet[0])
            possible_retweeted.append(tweet)
            tweets_list.remove(tweet)
            changed = True
    return changed


def build_retweet_cascade_graph(campaign_id, root_node):
    possible_retweeted = [root_node]
    logging.info('Building graph...')
    G = nx.DiGraph()
    G.add_node(root_node[0])
    tweets_list = get_all_retweets(campaign_id, root_node[0])
    changed = True
    count = 0
    while changed:
        if not loop_through_tweets_list(tweets_list, possible_retweeted, G):
            changed = False
        print count
        count += 1
    logging.info('Added {} tweets to graph'.format(len(possible_retweeted)))
    return G
'''
    plt.figure(figsize=(12, 10))
    nx.draw(G, arrows=True, with_labels=True, nodesize=1)
    plt.show()
'''


