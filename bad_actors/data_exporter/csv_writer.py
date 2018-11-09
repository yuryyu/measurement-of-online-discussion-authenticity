from __future__ import print_function
import logging
import csv

'''
This class is responsible reading the features from some table, transforming the data
into the following structure: author_osn_id, author_screen_name, prediction, probability
and finally writing this data into a CSV file
'''

class Csv_writer():
    def __init__(self, db, table):
        self._db = db
        self._table = table

    def setUp(self):
        pass

    def write_author_features_to_csv(self, output_filename):        
        logging.info("Start writing CSV file")
        header = ['author_osn_id', 'author_screen_name', 'prediction', 'probability']    
        
        with open(output_filename, 'w') as csvfile:
            data_file = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            data_file.writerow(header)
            data_file.writerow(['123434','CoraJRamos','negative','0.87'])
        
        logging.info("Finished writing CSV file")
        
        