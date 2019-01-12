#  Created by YY at 1/2/2019
#  Modified by YY at 1/12/19
from __future__ import print_function

from dataset_builder.feature_extractor.base_feature_generator import BaseFeatureGenerator
from preprocessing_tools.abstract_controller import AbstractController
from commons.commons import *
import numpy as np
import datetime
from dateutil import parser
import logging
import time
from scipy.stats import skew, kurtosis
from copy import deepcopy

'''
This class is responsible for generating features based on authors and posts temporal properties
Each author-feature and post-feature pair will be written in the AuthorFeature table
'''

class TemporalFeatureGenerator(AbstractController):
    """
    Example of enabling Temporal Feature Generator in config.ini file
    
    [TemporalFeatureGenerator]
    # data source 
    source_list=['posts', 'authors'] 
    # temporal features list 
    features_list = ['t_min', 't_max', 't_std_dev', 't_avg', 't_skewness', 't_kurtosis']
    # sample time list in minutes - choose/create needed from example
    delta_time = ['30','60','24*60','24*60*7','24*60*30','24*60*365']
    
    """
    def __init__(self, db, **kwargs):
        AbstractController.__init__(self, db)
        self._source_list = self._config_parser.eval(self.__class__.__name__, "source_list")
        self._features_list = self._config_parser.eval(self.__class__.__name__, "features_list")
        self._delta_time = self._config_parser.eval(self.__class__.__name__, "delta_time")        
        self._prefix = self.__class__.__name__

    def execute(self, window_start=None):
        function_name = 'extract_temporal_features'
        start_time = time.time()
        info_msg = "execute started for " + function_name + " started at " + str(start_time)
        logging.info(info_msg)
        claims = self._db.get_claims()        
        try:
            claim_features = []           
            today_datetime = datetime.datetime.now()            
            posts_dict=self._db.get_claim_id_posts_dict()            
            for cnt,claim in enumerate(claims):
                claim_id = claim.claim_id
                logging.info('Started ' +str(cnt+1)+ ' claim from ' +str(len(claims)) +' claims')                
                for source in self._source_list:                   
                    # define authors,posts per claim
                    if source=='authors':
                        s_list = self._db.get_claim_authors(claim_id)
                    elif source=='posts': 
                        s_list=posts_dict[claim_id]
                    if len(s_list)==0:
                        logging.info('The resulted list is empty for claim:'+str(claim_id))
                        continue                                                      
                    ll=[]
                    for s in s_list:
                        try:
                            if source=='authors':
                                created_at = s[43]
                            elif source=='posts':
                                created_at = s.created_at                                     
                            if created_at is not None:                                                            
                                creation_date = parser.parse(created_at)
                                delta =int(divmod((today_datetime - creation_date).total_seconds(),60)[0])
                                ll.append(delta)
                            else:
                                logging.info('Can not be created feature for ' +created_at)
                        except:
                            logging.info('Can not be parsed created_at, probably None value' )
                            pass                      
                    # normalization
                    m=min(ll)
                    lls = [i-m for i in ll]
                    #sorting in ascending 
                    lls.sort()
                    #init start stop indexes 
                    st_ind=0
                    stop_ind=1     
                    for delta in self._delta_time:
                        for idx, val in enumerate(lls[st_ind:]):
                            if val<=eval(delta):
                                stop_ind=idx
                        llsn=deepcopy(lls[st_ind:stop_ind])
                        st_ind=stop_ind                                                
                        for ftr,feature_name in enumerate(self._features_list):
                            logging.info('Started ' +str(ftr+1)+ ' feature from ' +str(len(self._features_list)) +' features')                            
                            try:
                                attribute_value = getattr(self, feature_name)(llsn)
                            except:
                                attribute_value = 0
                                print('Fail in extraction: '+feature_name) 
                            if attribute_value is not None:
                                attribute_name = "{0}_{1}_{2}_{3}".format(self._prefix, source, str(eval(delta)), feature_name)
                                # next line add envelope for feature
                                claim_feature = BaseFeatureGenerator.create_author_feature(attribute_name, claim_id, attribute_value,
                                                                                        self._window_start, self._window_end)
                                claim_features.append(claim_feature)
                                print('Appended: '+attribute_name)                        
        except:
            logging.error('Failed in extraction process!')
        stop_time = time.time()
        info_msg = "execute ended at " + str(stop_time)        
        logging.info(info_msg)       
        self._db.add_author_features(claim_features)        
        
    def cleanUp(self):
        pass   
    
    """ Temporal features from time delta list """
    def t_avg(self, ll):                    
        return sum(ll)/len(ll)

    def t_std_dev(self, ll):          
        return np.std(ll)

    def t_min(self, ll):           
        return min(ll)        
    
    def t_max(self, ll):           
        return max(ll)
  
    def t_skewness(self, ll):           
        return skew(ll)        
    
    def t_kurtosis(self, ll):           
        return kurtosis(ll)
    
    
  