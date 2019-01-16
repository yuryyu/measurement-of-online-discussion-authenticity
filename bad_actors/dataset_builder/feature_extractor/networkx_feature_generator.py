#  Created by YY at 29.11.18
#  Modified by Leah at 1/13/19
from __future__ import print_function

from dataset_builder.feature_extractor.base_feature_generator import BaseFeatureGenerator
from preprocessing_tools.abstract_controller import AbstractController
from commons.commons import *
import pandas as pd
import numpy as np
import networkx as nx
import sys
import logging
import time

'''
This class is responsible for generating features based on authors properties
Each author-feature pair will be written in the AuthorFeature table
'''

class NetworkxFeatureGenerator(AbstractController):
    """
    Example of enabling Temporal Feature Generator in config.ini file
    
    [NetworkxFeatureGenerator]    
    csv_file = ' '
    group_by = ['claim_id']
    source = ['source_author_guid']
    target = ['destination_author_guid']
    features_list = ['betweenness_centrality','closeness_centrality','communicability_centrality', 
                    'load_centrality','eigenvector_centrality', 'katz_centrality',    
                    'degree', 'density', 'average_clustering']
    
    """
    def __init__(self, db, **kwargs):
        AbstractController.__init__(self, db)
        self._features_list = self._config_parser.eval(self.__class__.__name__, "features_list")        
        self._csv_file = self._config_parser.eval(self.__class__.__name__, "csv_file")
        self._group_by = self._config_parser.eval(self.__class__.__name__, "group_by")
        self._source = self._config_parser.eval(self.__class__.__name__, "source")
        self._target = self._config_parser.eval(self.__class__.__name__, "target")                
        self._prefix = self.__class__.__name__

    def execute(self, window_start=None):                
        function_name = "extract_features_from_graph"
        start_time = time.time()
        info_msg = "execute started for " + function_name + " started at " + str(start_time)        
        logging.info(info_msg)        
        try:
            claim_features = []                
            if self._csv_file !=' ':
                logging.info('Getting existing author connections from csv file')                
                df = pd.read_csv(self._csv_file, names=['source_author_guid','destination_author_guid',
                                                        'connection_type','weight','claim_id','insertion_date'], low_memory=False)
            else:
                logging.info('Getting existing author connections with claim_id...')
                author_connections_with_claim_id = self._db.get_author_connections_with_claim_id()
                logging.info('Checking author connections for claim id...')
                author_connections_with_claim_id.extend(self._db.make_connections_with_claim_id()[0])
                logging.info(author_connections_with_claim_id[0])
                list_of_con_dicts = []
                for author_con in author_connections_with_claim_id:
                    connections_dict = {'source_author_guid': author_con.source_author_guid,
                                        'destination_author_guid': author_con.destination_author_guid,
                                        'connection_type': author_con.connection_type,
                                        'weight': author_con.weight,
                                        'claim_id': author_con.claim_id,
                                        'insertion_date': author_con.insertion_date}
                    list_of_con_dicts.append(connections_dict)
                df = pd.DataFrame(list_of_con_dicts)

            grps = df.groupby(self._group_by)              
            
            for cnt, grp in enumerate(grps):
                logging.info('Started ' +str(cnt)+ ' group from ' +str(len(grps)) +' groups')
                if nx.__version__[0] == '1':
                    G = nx.from_pandas_dataframe(grp[1], self._source[0], self._target[0])
                else:
                    G = nx.from_pandas_edgelist(grp[1], self._source[0], self._target[0])
                claim_ext_id = grp[0]
                #claim_id = self._db.claim_ext_id_to_claim_id(claim_ext_id)[0]
                claim_id =claim_ext_id
                if nx.__version__[0] > 1 and 'communicability_centrality' in self._features_list:
                    self._features_list.remove('communicability_centrality')
                for ftr, feature_name in enumerate(self._features_list):
                    logging.info('Started ' +str(ftr+1)+ ' feature from ' +str(len(self._features_list)) +' features')
                    attributes_dict = getattr(self, function_name)(G=G,ff=feature_name)
                    if len(attributes_dict)==1 and attributes_dict[feature_name] is not None:
                        attribute_name = "{0}_{1}".format(self._prefix, feature_name)
                        # next line add envelope for feature
                        claim_feature = BaseFeatureGenerator.create_author_feature(attribute_name, claim_id, attributes_dict[feature_name],
                                                                                self._window_start, self._window_end)
                        claim_features.append(claim_feature)
                        continue                        
                    
                    for sub_feature_name in ('min_','max_','median_','std_'):
                        attribute_value = attributes_dict[sub_feature_name+feature_name]                            
                        if attribute_value is not None:
                            attribute_name = "{0}_{1}".format(self._prefix, sub_feature_name+feature_name)
                            # next line add envelope for feature
                            claim_feature = BaseFeatureGenerator.create_author_feature(attribute_name, claim_id, attribute_value,
                                                                                    self._window_start, self._window_end)
                            claim_features.append(claim_feature)
        except:
            logging.info('Fail')
            print(sys.exc_info())
        stop_time = time.time()
        info_msg = "execute ended at " + str(stop_time)       
        logging.info(info_msg)    
        # used author_feature table
        self._db.add_author_features(claim_features)
        
        
    def cleanUp(self):
        pass
    
    def extract_features_from_graph(self,G,ff):    
        ret={}
        try:
            if ff == 'degree':
                res =G.degree().values()
            elif ff == 'effective_eccentricity':
                paths = nx.shortest_path_length(G)
                res = []
                for p in paths:
                    sorted_shortest_paths = sorted([l for l in p[1].values()])
                    effective_eccentricity = sorted_shortest_paths[int(len(sorted_shortest_paths) * 0.9)]
                    res.append(effective_eccentricity)
            elif ff in ['density', 'average_clustering', 'number_of_nodes', 'number_of_edges',
                        'number_connected_components']:
                res = eval('nx.'+ff+'(G)')
                return {ff:res}
            elif ff == 'fraction_of_end_points':
                degrees = nx.degree(G)
                end_points = [l[1] for l in degrees if l[1] == 1]
                res = float(len(end_points)) / nx.number_of_nodes(G)
                return {ff: res}
            elif ff in ['adjacency_spectrum']:
                res = eval('nx.'+ff+'(G)')
                ret.update({'min_' + ff: float(min(res))})
                ret.update({'max_' + ff: float(max(res))})
                ret.update({'median_' + ff: float(np.median(res))})
                ret.update({'std_' + ff: float(np.std(res))})
                return ret
            elif ff == 'trace':
                eigenvalues = nx.adjacency_spectrum(G)
                res = np.real(sum(eigenvalues))
                return {ff: res}
            elif ff == 'energy':
                eigenvalues = nx.adjacency_spectrum(G)
                res = sum([np.real(i) ** 2 for i in eigenvalues])
                return {ff: res}
            elif ff == 'number_of_eigenvalues':
                eigenvalues = nx.adjacency_spectrum(G)
                res = len(set(eigenvalues))
                return {ff: res}
            elif ff == 'two_hops_away_neighbors':
                res = []
                for node in nx.nodes(G):
                    paths = nx.single_source_shortest_path_length(G, node, cutoff=3)
                    res.append(len([d for d in paths.values() if d == 2]))
                print(res)
            elif ff == 'two_or_less_hops_away_neighbors':
                res = []
                for node in nx.nodes(G):
                    paths = nx.single_source_shortest_path_length(G, node, cutoff=3)
                    res.append(len(paths))
                print(res)
            elif ff == 'number_of_triangles':
                res = sum(nx.triangles(G).values()) / 3
                return {ff: res}
            elif ff == 'fraction_of_triangles':
                res = sum(nx.triangles(G).values()) / 3
                res = float(res) / nx.number_of_nodes(G)
                return {ff: res}
            else:
                res = eval('nx.'+ff+'(G).values()')
        except (AttributeError, nx.NetworkXError, TypeError) as e:
            print(e)
            res = [-1]    
        ret.update({'min_'+ff:min(res)})
        ret.update({'max_'+ff:max(res)})
        ret.update({'median_'+ff:np.median(res)})
        ret.update({'std_'+ff:np.std(res)})    
        return ret
    