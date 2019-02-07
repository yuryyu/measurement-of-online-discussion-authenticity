#  Created by Asaf at 24/1/2019
#  Lst Modified by Asaf at 24/1/2019
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
import itertools
from collections import defaultdict
from commons import consts
import re

try:
    from gensim import *
    # Notice: bag_of_words_model, using 'dictionary.doc2bow' function.

except:
    print("WARNING! gensim is not available! This module is not usable.")

from operator import itemgetter

from DB.schema_definition import *

'''
This class is responsible for generating features based on claim's posts properties
Each post-feature pair will be written in the AuthorFeature table
'''


class CooperationTopicFeatureGenerator(AbstractController):
    """
    Example of enabling CooperationTopic Feature Generator in config.ini file
    
    [CooperationTopicFeatureGenerator]
    number_of_topics=10
    num_of_terms_in_topic = 12
    stopword_file = lib/eng_stopwords.txt
    stem_language = ENG     
    features_list = ['topic_jaccard_distance_claim_min', 'topic_jaccard_distance_claim_max', 'topic_jaccard_distance_claim_std_dev', 't_avg', 'topic_jaccard_distance_claim_skewness', 'topic_jaccard_distance_claim_kurtosis']
        
    """
    def __init__(self, db, **kwargs):
        AbstractController.__init__(self, db)
        self._features_list = self._config_parser.eval(self.__class__.__name__, "features_list")
        self._author_count_features_list = self._config_parser.eval(self.__class__.__name__, "author_count_features_list")
        self._prefix = self.__class__.__name__
        self._num_of_terms_in_topic = self._config_parser.eval(self.__class__.__name__, "num_of_terms_in_topic")
        self.num_topics = self._config_parser.eval(self.__class__.__name__, "number_of_topics")
        self.stopword_file = self._config_parser.get(self.__class__.__name__, "stopword_file")
        self.stemlanguage = self._config_parser.get(self.__class__.__name__, "stem_language")
        self.topics = []
        self.topic = None
        self.post_id_to_topic_id = None
        self.topic_id_to_topics = {}
        # self.model = None
        self.dictionary = None
        self.corpus = None

    def execute(self, window_start=None):
        # Logger setup.
        start_time = time.time()
        info_msg = "execute started for Cooperation topic feature generator started at " + str(start_time)
        logging.info(info_msg)
        claims = self._db.get_claims()
        logging.info("Cooperation execute window_start %s" % self._window_start)

        try:

            # Claims => for each claim, get Posts. => for all posts, create Id to post words dictionary
            # includes stamming, stopwords. => 'calculate_topics' creates the bacg of words.

            claim_features = []
            posts_dict = self._db.get_claim_id_posts_dict()

            for cnt, claim in enumerate(claims):

                claim_id = claim.claim_id
                logging.info('Started ' + str(cnt+1) + ' claim from ' + str(len(claims)) + ' claims')
                posts_list = posts_dict[claim_id]

                if len(posts_list) == 0:
                    logging.info('The resulted list is empty for claim: ' + str(claim_id))
                    continue

                post_id_to_words = self._create_post_id_to_content_words(posts_list)
                post_id_to_strings_no_urls = self._create_post_id_to_strings_no_urls(posts_list)
                authors_counter_dic1 = self.calculate_topics_similarity(post_id_to_words)
                authors_counter_dic2 = self.calculate_topics_exact_match(post_id_to_strings_no_urls)

                for ftr, feature_name in enumerate(self._features_list):
                    logging.info('Started ' + str(ftr+1) + ' feature from ' + str(len(self._features_list)) + ' features')

                    try:
                        attribute_value1 = float(getattr(self, feature_name)(authors_counter_dic1))
                        attribute_value2 = float(getattr(self, feature_name)(authors_counter_dic2))
                    except:
                        attribute_value1 = -1.0
                        attribute_value2 = -1.0
                        print('Fail in extraction: ' + feature_name)

                    if attribute_value1 is not None and attribute_value2 is not None:
                        attribute_name1 = "{0}_{1}".format(self._prefix, feature_name)
                        attribute_name2 = "{0}_{1}".format(self._prefix, "exact_match_" + feature_name)

                        # next line add envelope for feature
                        claim_feature1 = BaseFeatureGenerator.create_author_feature(attribute_name1, claim_id, attribute_value1,
                                                                                self._window_start, self._window_end)
                        claim_feature2 = BaseFeatureGenerator.create_author_feature(attribute_name2, claim_id, attribute_value2,
                                                                                    self._window_start, self._window_end)
                        claim_features.append(claim_feature1)
                        claim_features.append(claim_feature2)
                        print('Appended: ' + attribute_name1)
                        print('Appended: ' + attribute_name2)

                for ftr, feature_name in enumerate(self._author_count_features_list):
                    logging.info('Started ' + str(ftr+1) + ' feature from ' + str(len(self._author_count_features_list)) + ' features')
                    attribute_name1 = "{0}_{1}".format(self._prefix, feature_name)
                    attribute_name2 = "{0}_{1}".format(self._prefix, "exact_match_" + feature_name)
                    for author_id in authors_counter_dic1:
                        attribute_value1 = authors_counter_dic1[author_id]
                        attribute_value2 = authors_counter_dic2[author_id]
                        if attribute_value1 is not None and attribute_value2 is not None:
                            author_feature1 = BaseFeatureGenerator.create_author_feature(attribute_name1, author_id, attribute_value1,
                                                                                    self._window_start, self._window_end)
                            author_feature2 = BaseFeatureGenerator.create_author_feature(attribute_name2, author_id, attribute_value2,
                                                                                        self._window_start, self._window_end)
                            claim_features.append(author_feature1)
                            claim_features.append(author_feature2)

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
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
                post_id_to_ngrams[post.post_id] = calc_ngrams(words, 1, 1)
        return post_id_to_ngrams

    def _create_post_id_to_strings_no_urls(self, curr_posts):
        post_id_to_sentences = {}
        for doc_id, post in enumerate(curr_posts):
            if post.content is not None:
                words = clean_content_to_set_of_words(self.stopword_file, post.content, self.stemlanguage)
                words = ' '.join(words)
                words = re.sub(r'^https?:\/\/.*[\r\n]*', '', words, flags=re.MULTILINE) # Remove urls.
                post_id_to_sentences[post.post_id] = words
        return post_id_to_sentences


    def calculate_topics_similarity(self, post_id_to_words):
        words = post_id_to_words.values()
        self.dictionary = corpora.Dictionary(words)

        author_cooperation_counter_dict = defaultdict(int)

        # Iterates over all post_id and words pairs combinations only once.
        for post_id1, post_id2 in itertools.combinations(post_id_to_words, 2):
            first_author_id = self._db.get_post_by_id(post_id1).author_guid
            second_author_id = self._db.get_post_by_id(post_id1).author_guid
            j_score = jaccard_index(post_id_to_words[post_id1], post_id_to_words[post_id2])

            # Checks similarity.
            if j_score >= consts.COOPERATION_FEATURE.JACCARD_THRESHOLD:
                author_cooperation_counter_dict[first_author_id] += 1
                author_cooperation_counter_dict[second_author_id] += 1
                print("Matched >= 0.9")
            else:
                print("Didn't matched: " + str(j_score))
            print("Similarity - current claim author count: " + str(author_cooperation_counter_dict))
        return author_cooperation_counter_dict

    def calculate_topics_exact_match(self, post_id_to_strings):
        words = post_id_to_strings.values()
        self.dictionary = corpora.Dictionary(words)

        author_cooperation_counter_dict = defaultdict(int)

        # Iterates over all post_id and words pairs combinations only once.
        for post_id1, post_id2 in itertools.combinations(post_id_to_strings, 2):
            first_author_id = self._db.get_post_by_id(post_id1).author_guid
            second_author_id = self._db.get_post_by_id(post_id1).author_guid

            # Checks similarity.
            if post_id_to_strings[post_id1] == post_id_to_strings[post_id2]:
                author_cooperation_counter_dict[first_author_id] += 1
                author_cooperation_counter_dict[second_author_id] += 1
                print("Exact match.")

            print("Exact match - current claim author count: " + str(author_cooperation_counter_dict))
        return author_cooperation_counter_dict

    """ Aggregated features from list """
    # topic_jaccard_distance_claim_avg
    def t_avg(self, ll):
        return sum(ll)/len(ll)

    # topic_jaccard_distance_claim_std_dev
    def t_std_dev(self, ll):
        return np.std(ll)

    # topic_jaccard_distance_claim_min
    def t_min(self, ll):
        return min(ll)

    # topic_jaccard_distance_claim_max
    def t_max(self, ll):
        return max(ll)
    # topic_jaccard_distance_claim_skewness
    def t_skewness(self, ll):
        return skew(ll)

    # topic_jaccard_distance_claim_kurtosis
    def t_kurtosis(self, ll):
        return kurtosis(ll)


