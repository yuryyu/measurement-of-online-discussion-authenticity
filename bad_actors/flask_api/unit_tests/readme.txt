links:
https://github.com/yuryyu/measurement-of-online-discussion-authenticity/tree/test/bad_actors/configuration
https://github.com/layercake1/measurement-of-online-discussion-authenticity/tree/test/bad_actors/configuration
https://realpython.com/flask-connexion-rest-api/#example-code
http://flask.pocoo.org/docs/1.0/patterns/sqlite3/
https://www.tutorialspoint.com/flask/flask_sqlite.htm
https://github.com/ronaldbradford/schema


https://editor.swagger.io/?url=https://raw.githubusercontent.com/tomgond/intelici_api/master/v4.api

For running server with Flask:

In cmd:
cd path_to_bad_actors
python flask_api\flask_api.py configuration\config_api.ini

For testing in web browser:
http://localhost:5000/api/v1/campaigns/100/status
or:
http://localhost:5000/api/v1/campaigns/101/status

For testing analyze:
http://localhost:5000/api/v1/analyze
