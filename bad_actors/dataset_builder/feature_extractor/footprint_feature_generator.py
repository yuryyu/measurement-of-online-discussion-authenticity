from dataset_builder.feature_extractor.base_feature_generator import BaseFeatureGenerator
from commons.commons import *
import pandas as pd
import numpy as np


'''
This class is responsible for generating features based on authors properties
Each author-feature pair will be written in the AuthorFeature table
'''

class FootprintFeatureGenerator(BaseFeatureGenerator):
 
    def cleanUp(self):
        pass    

    def avg_num_of_followers(self, **kwargs):
        if 'author' in kwargs.keys():
            author = kwargs['author']
            return author.followers_count
        else:
            raise Exception('Author object was not passed as parameter')


    def avg_num_of_friends(self, **kwargs):
        if 'author' in kwargs.keys():
            author = kwargs['author']
            return author.friends_count
        else:
            raise Exception('Author object was not passed as parameter')

    def friends_followers_ratio(self, **kwargs):
        if 'author' in kwargs.keys():
            author = kwargs['author']
            friends_count = author.friends_count
            followers_count = author.followers_count

            if friends_count > 0 and followers_count > 0:
                return float(friends_count) / float(followers_count)
            else:
                return 0.0
        else:
            raise Exception('Author object was not passed as parameter')
    
    
    def std_num_of_followers(self, **kwargs):
        if 'author' in kwargs.keys():
            author = kwargs['author']
            friends_count = author.friends_count
            followers_count = author.followers_count

            if friends_count > 0 and followers_count > 0:
                return float(friends_count) / float(followers_count)
            else:
                return 0.0
        else:
            raise Exception('Author object was not passed as parameter')
    
    def std_num_of_friends(self, **kwargs):
        if 'author' in kwargs.keys():
            author = kwargs['author']
            friends_count = author.friends_count
            followers_count = author.followers_count

            if friends_count > 0 and followers_count > 0:
                return pd.rolling_std(friends_count, 25, min_periods=1)
            else:
                return 0.0
        else:
            raise Exception('Author object was not passed as parameter')
        
    def std_frends_followers_ratio(self, **kwargs):
        if 'author' in kwargs.keys():
            author = kwargs['author']
            friends_count = author.friends_count
            followers_count = author.followers_count

            if friends_count > 0 and followers_count > 0:
                return np.std(float(friends_count) / float(followers_count))
            else:
                return 0.0
        else:
            raise Exception('Author object was not passed as parameter')
    
    