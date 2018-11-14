from __future__ import print_function
import logging
import csv
import random
import numpy

'''
This class is responsible reading the features from some table, transforming the data
into the following structure: author_osn_id, author_screen_name, prediction, probability
and finally writing this data into a CSV file
'''

class Csv_writer():
    def __init__(self, db, table):
        self.db = db
        self.table = table

    def setUp(self):
        pass

    def write_to_csv(self, output_filename, campaign_id):        
        logging.info("Start writing CSV file")
        header = ['author_osn_id', 'author_screen_name', 'prediction', 'probability']          
        campaign = self.db.get_from_table(self.table, campaign_id)           
        logging.info("Record "+str(campaign_id)+" successfully read:")            
        logging.info(campaign[0])
        logging.info('length is '+str(len(campaign)))        
        
        with open(output_filename, 'w') as csvfile:
            data_file = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            data_file.writerow(header)
            sscore=[]
            for ff in range(0,len(campaign)):                        
                score=random.random()                
                data_file.writerow([campaign[ff][4],campaign[ff][3].split('/')[1],'negative',"{0:.2f}".format(score)])
                sscore.append(score)
        logging.info("Finished writing CSV file")
        fake_news_score=float("{0:.2f}".format(numpy.mean(sscore)))        
        return fake_news_score
        