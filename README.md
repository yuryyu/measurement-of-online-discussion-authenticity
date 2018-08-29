# Online Social Network Abuser Detection & Online Discussion Authenticity Detection Framework
Code used in the following papers.

If you are using this code for any research publication, or for preparing a technical report, you must cite the following paper as the source of the code.

Aviad Elyashar, Jorge Bendahan, and Rami Puzis. "Is the News Deceptive? Fake News Detection using Topic Authenticity"

BibTex:

@inproceedings{elyashar2017news,
 author={Elyashar, Aviad and Bendahan, Jorge and Puzis, Rami},
 title     = {Is the News Deceptive? Fake News Detection using Topic Authenticity},  
 booktitle = {The Seventh International Conference on Social Media Technologies, Communication, and Informatics},
 series = {SOTICS 2017},
 year = {2017},
 location = {Athens, Greece},
 pages     = {16--21},
 numpages={6}
 }

### Requirements
Python install packages log 

numpy                    - 1.15.1 
scikit-learn             - 0.19.2
networkx (+ decorator)   - 1.11  (4.3.0)
pandas                   - 0.22 (python-dateutil-2.7.3,pytz-2018.5)
sqlalchemy               - 1.2.11
nltk  (six)              - 3.3 (1.11.0)
scipy                    - 1.1.0
python-twitter           - 3.3
#simplejson - resolved in 3.3!
bs4                      - 0.0.1
pyquery                  - 1.4.0
matplotlib               - 2.2.3 
selenium                 - 3.14.0
praw                     - 6.0.0
gensim                   - 3.5.0 
sympy                    - 1.2
xgboost                  - 0.80
pillow                   - 5.2.0


Troubleshooting, if needed
h. If this Error apper “distributed 1.21.8 requires msgpack, which is not
installed.”
Install msgpack (pip install msgpack || conda install -c anaconda msgpack-python)
i. If this error apper “grin 1.2.1 requires argparse&gt;=1.1, which is not installed.”
Install argparse (pip install argparse)
