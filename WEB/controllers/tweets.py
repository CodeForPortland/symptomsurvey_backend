import json

from flask import request
from services import auth_service, tweets_service

JSON_CONTENT_TYPE = {'Content-Type': 'application/json'}

def add_routes(app):
  @app.route('/tweets/load', endpoint='load_tweets')
  def load_tweets():
    '''
    Load tweets. Retrieve 100 tweets by users located within a given radius of the given latitude/longitude. 
    The location is preferentially taking from the Geotagging API, but will fall back to their Twitter profile. 
    The parameter value is specified by " latitude,longitude,radius ", where radius units 
    must be specified as either " mi " (miles) or " km " (kilometers).
    ---
    responses:
      200:
        description: Successfully retrieved the tweets
        examples: 
          application/json: {"statuses": [{"created_at": "Sun Mar 31 18:32:35 +0000 2019","id": 1112422454528524300...example tweet elided}]}
      500:
        description: Server error occurred
    '''
    tweets = tweets_service.get_tweets_from_twitter()
    try:
      tweets_service.save_tweets(tweets["statuses"])
      return json.dumps(tweets), 200, {'Content-Type': 'application/json'}
    except Exception as ex:
      return json.dumps({'Exception': str(ex)}), 500, JSON_CONTENT_TYPE

  @app.route('/tweets', methods=['POST'])
  def searchTweets():
    body = request.get_json()
    search_text = body.get('search')
    tweets = tweets_service.get_tweets_from_db(search_text)
    return tweets, 200, JSON_CONTENT_TYPE

  @app.route('/tweets', methods=['GET'])
  def getTweets():
    return tweets_service.get_tweets_from_db(), 200, JSON_CONTENT_TYPE
