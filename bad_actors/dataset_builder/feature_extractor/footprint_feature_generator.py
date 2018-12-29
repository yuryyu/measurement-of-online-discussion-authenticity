#  Created by YY at 27/11/2018
from __future__ import print_function

from dataset_builder.feature_extractor.base_feature_generator import BaseFeatureGenerator
from preprocessing_tools.abstract_controller import AbstractController
from commons.commons import *
# import pandas as pd
import numpy as np
import datetime
from dateutil import parser

'''
This class is responsible for generating features based on authors properties
Each author-feature pair will be written in the AuthorFeature table
'''

class FootprintFeatureGenerator(AbstractController):

    def __init__(self, db, **kwargs):
        AbstractController.__init__(self, db)
        self._features_list = self._config_parser.eval(self.__class__.__name__, "features_list")        
        self._prefix = self.__class__.__name__

    def execute(self, window_start=None):

        claims = self._db.get_claims()
        
        try:
            claim_features = []
            for feature_name in self._features_list:
                for claim in claims:
                    claim_id = claim.claim_id
                    # define authors per claim
                    authors = self._db.get_claim_authors(claim_id)
                    attribute_value = getattr(self, feature_name)(claim=claim,authors=authors) # entrance to method with "claim" param, return feature
                    if attribute_value is not None:
                        attribute_name = "{0}_{1}".format(self._prefix, feature_name)
                        # next line add envelope for feature
                        claim_feature = BaseFeatureGenerator.create_author_feature(attribute_name, claim_id, attribute_value,
                                                                                self._window_start, self._window_end)
                        claim_features.append(claim_feature)
        except:
            print('Fail')
        # used author_feature table - due to next use
        self._db.add_author_features(claim_features)
        # regular use:   
        #self._db.add_claim_features(claim_features)
        
    def cleanUp(self):
        pass    

    
    """ Author account properties """
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

    """ Followers """
    def avg_num_of_followers(self, **kwargs):
        rez=100
        try:
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=0                
                for author in authors:
                    avg_num+=author[9]
                rez=avg_num/len(authors)    
        except: pass            
        return rez
    
    def std_dev_num_of_followers(self, **kwargs):
        rez=101
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[9])           
                rez= np.std(avg_num)            
        except: pass            
        return rez 
    
    def min_num_of_followers(self, **kwargs):
        rez=102
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[9])           
                rez= min(avg_num)            
        except: pass            
        return rez 
    
    def max_num_of_followers(self, **kwargs):
        rez=103
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[9])           
                rez= max(avg_num)            
        except: pass            
        return rez 
    
    """ Friends """
    def avg_num_of_friends(self, **kwargs):
        rez=200
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=0                
                for author in authors:
                    avg_num+=author[11]
                rez= avg_num/len(authors)
        except: pass            
        return rez       

    def std_dev_num_of_friends(self, **kwargs):
        rez=201
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[11])           
                rez= np.std(avg_num)          
        except: pass            
        return rez
    
    def min_num_of_friends(self, **kwargs):
        rez=202
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[11])           
                rez= min(avg_num)          
        except: pass            
        return rez
    
    def max_num_of_friends(self, **kwargs):
        rez=203
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[11])           
                rez= max(avg_num)          
        except: pass            
        return rez
        
    """ Statuses """
    def avg_num_of_statuses(self, **kwargs):
        rez=300
        try:
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=0                
                for author in authors:
                    avg_num+=author[8]
                rez=avg_num/len(authors)    
        except: pass            
        return rez
    
    def std_dev_num_of_statuses(self, **kwargs):
        rez=301
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[8])           
                rez= np.std(avg_num)            
        except: pass            
        return rez 
    
    def min_num_of_statuses(self, **kwargs):
        rez=302
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[8])           
                rez= min(avg_num)            
        except: pass            
        return rez 
    
    def max_num_of_statuses(self, **kwargs):
        rez=303
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[8])           
                rez= max(avg_num)            
        except: pass            
        return rez 
    
    """ Favorites """
    def avg_num_of_favorites(self, **kwargs):
        rez=400
        try:
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=0                
                for author in authors:
                    avg_num+=author[10]
                rez=avg_num/len(authors)    
        except: pass            
        return rez
    
    def std_dev_num_of_favorites(self, **kwargs):
        rez=401
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[10])           
                rez= np.std(avg_num)            
        except: pass            
        return rez 
    
    def min_num_of_favorites(self, **kwargs):
        rez=402
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[10])           
                rez= min(avg_num)            
        except: pass            
        return rez 
    
    def max_num_of_favorites(self, **kwargs):
        rez=403
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[10])           
                rez= max(avg_num)            
        except: pass            
        return rez 
    
    
    """ Listed """
    def avg_num_of_listed_count(self, **kwargs):
        rez=500
        try:
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=0                
                for author in authors:
                    avg_num+=author[12]
                rez=avg_num/len(authors)    
        except: pass            
        return rez
    
    def std_dev_num_of_listed_count(self, **kwargs):
        rez=501
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[12])           
                rez= np.std(avg_num)            
        except: pass            
        return rez 
    
    def min_num_of_listed_count(self, **kwargs):
        rez=502
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[12])           
                rez= min(avg_num)            
        except: pass            
        return rez 
    
    def max_num_of_listed_count(self, **kwargs):
        rez=503
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[12])           
                rez= max(avg_num)            
        except: pass            
        return rez 
    
    
    """ Protected """
    def avg_num_of_protected(self, **kwargs):
        rez=600
        try:
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=0                
                for author in authors:
                    avg_num+=author[25]
                rez=avg_num/len(authors)    
        except: pass            
        return rez
    
    def std_dev_num_of_protected(self, **kwargs):
        rez=601
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[25])           
                rez= np.std(avg_num)            
        except: pass            
        return rez 
    
    def min_num_of_protected(self, **kwargs):
        rez=602
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[25])           
                rez= min(avg_num)            
        except: pass            
        return rez 
    
    def max_num_of_protected(self, **kwargs):
        rez=603
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[25])           
                rez= max(avg_num)            
        except: pass            
        return rez 
    
    
    """ Verified """
    def avg_num_of_verified(self, **kwargs):
        rez=700
        try:
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=0                
                for author in authors:
                    avg_num+=author[31]
                rez=avg_num/len(authors)    
        except: pass            
        return rez
    
    def std_dev_num_of_verified(self, **kwargs):
        rez=701
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[31])           
                rez= np.std(avg_num)            
        except: pass            
        return rez 
    
    def min_num_of_verified(self, **kwargs):
        rez=702
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[31])           
                rez= min(avg_num)            
        except: pass            
        return rez 
    
    def max_num_of_verified(self, **kwargs):
        rez=703
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(author[31])           
                rez= max(avg_num)            
        except: pass            
        return rez 
    
    """ Ratios """
    def avg_friends_followers_ratio(self, **kwargs):
        rez=0.802
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=0.0                
                for author in authors:
                    avg_num+=float(author[11])/float(max(author[9],1))           
                rez= avg_num/float(len(authors))
            
        except: pass            
        return rez        
        
    def std_dev_friends_followers_ratio(self, **kwargs):
        rez=0.805
        try:           
            if 'authors' in kwargs.keys():
                authors = kwargs['authors']
                avg_num=[]                
                for author in authors:
                    avg_num.append(float(author[11])/float(max(author[9],1)))           
                rez= np.std(avg_num)            
        except: pass            
        return rez 
    