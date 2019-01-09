#  Created by YY at 2/1/2011
from __future__ import print_function

from dataset_builder.feature_extractor.base_feature_generator import BaseFeatureGenerator
from preprocessing_tools.abstract_controller import AbstractController
from commons.commons import *
# import pandas as pd
import numpy as np
import datetime
from dateutil import parser
import logging
import time

'''
This class is responsible for generating features based on authors and posts temporal properties
Each author-feature and post-feature pair will be written in the AuthorFeature table
'''

class TemporalFeatureGenerator(AbstractController):

    def __init__(self, db, **kwargs):
        AbstractController.__init__(self, db)
        self._features_list = self._config_parser.eval(self.__class__.__name__, "features_list")        
        self._prefix = self.__class__.__name__

    def execute(self, window_start=None):
        function_name = 'extract_temporal_features'
        start_time = time.time()
        info_msg = "execute started for " + function_name + " started at " + str(start_time)        
        print (info_msg)
        logging.info(info_msg)
        claims = self._db.get_claims()        
        try:
            claim_features = []            
            cnt=1
            for claim in claims:
                logging.info('Started ' +str(cnt)+ ' claim from ' +str(len(claims)) +' claims')
                print('Started ' +str(cnt)+ ' claim from ' +str(len(claims)) +' claims')
                cnt+=1
                claim_id = claim.claim_id
                # define authors,posts per claim
                authors = self._db.get_claim_authors(claim_id)
                posts_dict=self._db.get_claim_id_posts_dict()
                posts=posts_dict[claim_id]
                # create temporal data table per claim (pandas data frame)
                # post_guid, author_guid, year, month, day, hour, minute, second
                
                ftr=1
                for feature_name in self._features_list:
                    logging.info('Started ' +str(ftr)+ ' feature from ' +str(len(self._features_list)) +' features')
                    print('Started ' +str(ftr)+ ' feature from ' +str(len(self._features_list)) +' features')
                    ftr+=1
                    attribute_value = getattr(self, feature_name)(claim=claim,authors=authors,posts=posts) 
                    if attribute_value is not None:
                        attribute_name = "{0}_{1}".format(self._prefix, feature_name)
                        # next line add envelope for feature
                        claim_feature = BaseFeatureGenerator.create_author_feature(attribute_name, claim_id, attribute_value,
                                                                                self._window_start, self._window_end)
                        claim_features.append(claim_feature)
        except:
            print('Fail')
        stop_time = time.time()
        info_msg = "execute ended at " + str(stop_time)        
        print (info_msg)
        logging.info(info_msg)     
        # used author_feature table - due to next use
        self._db.add_author_features(claim_features)
        # regular use:   
        #self._db.add_claim_features(claim_features)
        
    def cleanUp(self):
        pass    
    #a=[2, 8, 0, 4, 1, 9, 9, 0]
    #scipy.stats.kurtosis(a, axis=0, fisher=True, bias=True)
    #from scipy.stats import skew
    #skew([1, 2, 3, 4, 5])
    #skew([2, 8, 0, 4, 1, 9, 9, 0])
    
    """ Author temporal properties """
    def avg_account_age(self, **kwargs):
        rez=10
        try:
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=0
                auth_cnt=0                
                for author in authors:
                    created_at = author.created_at
                    if created_at is not None:
                        auth_cnt+=1
                        account_creation_date = parser.parse(created_at).date()
                        today_date = datetime.date.today()
                        delta = today_date - account_creation_date
                        avg_num+= delta.days                   
                rez=avg_num/auth_cnt    
        except: pass            
        return rez

    def std_dev_account_age(self, **kwargs):
        rez=11
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    created_at = author.created_at
                    if created_at is not None:                        
                        account_creation_date = parser.parse(created_at).date()
                        today_date = datetime.date.today()
                        delta = today_date - account_creation_date
                        avg_num.append(delta.days)                             
                rez= np.std(avg_num)            
        except: pass            
        return rez

    def min_account_age(self, **kwargs):
        rez=12
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    created_at = author.created_at
                    if created_at is not None:                        
                        account_creation_date = parser.parse(created_at).date()
                        today_date = datetime.date.today()
                        delta = today_date - account_creation_date
                        avg_num.append(delta.days)             
                rez= min(avg_num)            
        except: pass            
        return rez 
    
    def max_account_age(self, **kwargs):
        rez=13
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    created_at = author.created_at
                    if created_at is not None:                        
                        account_creation_date = parser.parse(created_at).date()
                        today_date = datetime.date.today()
                        delta = today_date - account_creation_date
                        avg_num.append(delta.days)          
                rez= max(avg_num)            
        except: pass            
        return rez 
    
    
    
    """ Posts temporal properties """
    def avg_posts_age(self, **kwargs):
        rez=10
        try:
            if 'posts' in kwargs.keys():
                posts = kwargs['posts']
                avg_num=0
                post_cnt=0                
                for post in posts:
                    created_at = post.created_at
                    if created_at is not None:
                        post_cnt+=1
                        post_creation_date = parser.parse(created_at).date()
                        post_creation_time = parser.parse(created_at).time()
                        today_date = datetime.date.today()
                        delta = today_date - post_creation_date
                        avg_num+= delta.days                   
                rez=avg_num/post_cnt    
        except: pass            
        return rez

    def std_dev_posts_age(self, **kwargs):
        rez=11
        try:           
            if 'posts' in kwargs.keys():
                posts = kwargs['posts']
                avg_num=[]                              
                for post in posts:
                    created_at = post.created_at
                    if created_at is not None:                        
                        post_creation_date = parser.parse(created_at).date()
                        today_date = datetime.date.today()
                        delta = today_date - post_creation_date
                        avg_num.append(delta.days)                             
                rez= np.std(avg_num)            
        except: pass            
        return rez

    def min_posts_age(self, **kwargs):
        rez=12
        try:           
            if 'posts' in kwargs.keys():
                posts = kwargs['posts']
                avg_num=[]                               
                for post in posts:
                    created_at = post.created_at
                    if created_at is not None:                        
                        post_creation_date = parser.parse(created_at).date()
                        today_date = datetime.date.today()
                        delta = today_date - post_creation_date
                        avg_num.append(delta.days)              
                rez= min(avg_num)            
        except: pass            
        return rez 
    
    def max_posts_age(self, **kwargs):
        rez=13
        try:           
            if 'posts' in kwargs.keys():
                posts = kwargs['posts']
                avg_num=[]                               
                for post in posts:
                    created_at = post.created_at
                    if created_at is not None:                        
                        post_creation_date = parser.parse(created_at).date()
                        today_date = datetime.date.today()
                        delta = today_date - post_creation_date
                        avg_num.append(delta.days)
                rez= max(avg_num)            
        except: pass            
        return rez 

    