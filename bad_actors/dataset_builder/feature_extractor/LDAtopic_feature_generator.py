#  Created by YY at 1/2/2019
#  Modified by YY at 1/12/19
from __future__ import print_function

from dataset_builder.feature_extractor.base_feature_generator import BaseFeatureGenerator
from preprocessing_tools.abstract_controller import AbstractController
from commons.commons import *
import numpy as np
# import datetime
# from dateutil import parser
import logging
import time
from scipy.stats import skew, kurtosis
# from copy import deepcopy

try:
    from gensim import *

    lda_model = models.ldamodel
except:
    print("WARNING! gensim is not available! This module is not usable.")

from operator import itemgetter

from DB.schema_definition import *

'''
This class is responsible for generating features based on claim's posts properties
Each post-feature pair will be written in the AuthorFeature table
'''

class LDATopicFeatureGenerator(AbstractController):
    """
    Example of enabling LDATopic Feature Generator in config.ini file
    
    [LDATopicFeatureGenerator]
    number_of_topics=10
    num_of_terms_in_topic = 12
    stopword_file = lib/eng_stopwords.txt
    stem_language = ENG     
    features_list = ['t_min', 't_max', 't_std_dev', 't_avg', 't_skewness', 't_kurtosis']
        
    """
    def __init__(self, db, **kwargs):
        AbstractController.__init__(self, db)        
        self._features_list = self._config_parser.eval(self.__class__.__name__, "features_list")              
        self._prefix = self.__class__.__name__        
        self._num_of_terms_in_topic = self._config_parser.eval(self.__class__.__name__, "num_of_terms_in_topic")
        self.num_topics = self._config_parser.eval(self.__class__.__name__, "number_of_topics")
        self.stopword_file = self._config_parser.get(self.__class__.__name__, "stopword_file")
        self.stemlanguage = self._config_parser.get(self.__class__.__name__, "stem_language")
        self.topics = []
        self.topic = None
        self.post_id_to_topic_id = None
        self.topic_id_to_topics = {}
        self.model = None
        self.dictionary = None
        self.corpus = None

    def execute(self, window_start=None):        
        start_time = time.time()
        info_msg = "execute started for LDA topic feature generator started at " + str(start_time)
        logging.info(info_msg)
        claims = self._db.get_claims()      
        logging.info("LDATopicModel execute window_start %s" % self._window_start)        
        
        try:
            claim_features = []
            posts_dict=self._db.get_claim_id_posts_dict()            
            for cnt,claim in enumerate(claims):
                claim_id = claim.claim_id
                logging.info('Started ' +str(cnt+1)+ ' claim from ' +str(len(claims)) +' claims')                
                s_list=posts_dict[claim_id]
                if len(s_list)==0:
                    logging.info('The resulted list is empty for claim:'+str(claim_id))
                    continue
                post_id_to_words = self._create_post_id_to_content_words(s_list)
                self.calculate_topics(post_id_to_words)                                                                      
                ll=self.calculate_topics(post_id_to_words)                                                                            
                for ftr,feature_name in enumerate(self._features_list):
                    logging.info('Started ' +str(ftr+1)+ ' feature from ' +str(len(self._features_list)) +' features')                            
                    try:
                        attribute_value = float(getattr(self, feature_name)(ll))
                    except:
                        attribute_value = -1.0
                        print('Fail in extraction: '+feature_name) 
                    if attribute_value is not None:
                        attribute_name = "{0}_{1}".format(self._prefix, feature_name)
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
    
    def _create_post_id_to_content_words(self, curr_posts):        
        post_id_to_ngrams = {}
        for doc_id, post in enumerate(curr_posts):
            if post.content is not None:
                words = clean_content_to_set_of_words(self.stopword_file, post.content, self.stemlanguage)
                words = ' '.join(words)
                post_id_to_ngrams[doc_id] = calc_ngrams(words, 1, 1)
        return post_id_to_ngrams

    def calculate_topics(self, post_id_to_words):
        words = post_id_to_words.values()
        self.dictionary = corpora.Dictionary(words)
        self.corpus = [self.dictionary.doc2bow(content_words) for content_words in words]
        self.model = lda_model.LdaModel(self.corpus, num_topics=self.num_topics)
        self.topic_id_to_topics = {}
        self.topics = []
        self.post_to_topic_id = {}
        post_topic_max = []
        for post_id in post_id_to_words:
            content_words = post_id_to_words[post_id]
            bow = self.dictionary.doc2bow(content_words)
            topic_id_to_probability = self.model.get_document_topics(bow)
            self.post_to_topic_id[post_id] = {probability[0]: probability[1] for probability in topic_id_to_probability}
            max_topic_probability = max(topic_id_to_probability, key=lambda item: item[1])            
            post_topic_max.append(max_topic_probability[1])
        return post_topic_max
    
    """ Aggregated features from list """
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
    
    
  