# Created by aviade                   
# Time: 29/03/2016 16:01

import unittest

import sys

#sys.argv.append('configuration/config_test.ini')
sys.argv = ['', 'configuration/config_test.ini']

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
#
# from Twitter_API.unit_tests.twitter_api_requester_unittests import TestTwitterApiRequester
# from preprocessing_tools.unit_tests.xml_importer_unittests import TestXmlImporter
# from bad_actors_collector.unit_tests.bad_actor_collector_unittests import TestBadActorCollector
#from missing_data_complementor.unit_tests.test_missingDataComplementor import MissingDataComplementorTests
# from twitter_crawler.unittests.twitter_crawler_tests import TwitterCrawlerTests
# from dataset_builder.lda_topic_model_test import TestLDATopicModel

# from timeline_overlap_visualization.test_timelineOverlapVisualizationGenerator import TestTimelineOverlapVisualizationGenerator
# from DB.unit_tests.posts_unittests import TestPost
# from DB.unit_tests.authors_unittests import TestAuthor
# from dataset_builder.unit_tests.dataset_builder_unittests import DatasetBuilderTest
# from dataset_builder.unit_tests.feature_extractor_unittests import FeatureExtractorTest
#from preprocessing_tools.unit_tests.test_app_Importer import TestAppImporter
#from preprocessing_tools.unit_tests.test_rank_app_importer import TestRankAppImporter
#from preprocessing_tools.tsv_importer import TestCSVDataImport
#from preprocessing_tools.unit_tests.test_leadspotting_posts_importer import TestLeadspottingPostsImporter
#from preprocessing_tools.unit_tests.test_leadspotting_claim_details_importer import TestClaimDetailsImporter
# from dataset_builder.unit_tests.word_embedding_differential_unittests import Word_Embeddings_Differential_Feature_Generator_Unittests
# from dataset_builder.unit_tests.word_embeddings_comparison_feature_generator_unittests import Word_Embeddings_Comparison_Feature_Generator_Unittests
# from dataset_builder.unit_tests.glove_word_embedding_model_creator_unittest import GloveWordEmbeddingModelCreatorUnittest
# from dataset_builder.unit_tests.word_embeddings_feature_generator_unittests import Word_Embeddings_Feature_Generator_Unittests
# from dataset_builder.unit_tests.test_gensim_word_embeddings_model_trainer import TestGensimWordEmbeddingsModelTrainer
# from old_tweets_crawler.test_old_tweets_crawler import TestOldTweetsCrawler
# from dataset_builder.unit_tests.test_image_downloader import TestImageDownloader
# from topic_distribution_visualization.test_claim_to_topic_converter import TestClaimToTopicConverter
#from missing_data_complementor.unit_tests.test_AddAuthorConnectionClaimId import AddAuthorConnectionClaimIdTests
#from data_exporter.unittests.test_ranked_authors_exporter import TestRankedAuthorsExporter
#sys.argv[1] = 'configuration/cong_test_api'
from flask_api.unit_tests.test_flask_api import TestFlaskAPI

if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])
