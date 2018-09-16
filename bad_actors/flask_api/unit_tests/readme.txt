https://github.com/layercake1/measurement-of-online-discussion-authenticity/tree/test/bad_actors/configuration

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
