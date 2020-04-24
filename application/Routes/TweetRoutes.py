from flask import request, jsonify
from flask import current_app as app
from ..Models.Tweet import db, Tweet
from ..helper.encoder import AlchemyEncoder
from ..helper.TweetClassifier import TweetClassifier
import json
import tweepy
import numpy
from os import environ, path
from dotenv import load_dotenv
import datetime
from datetime import timezone
from flask_cors import cross_origin

basedir = path.abspath(path.dirname(path.dirname(path.dirname(__file__))))
load_dotenv(path.join(basedir, '.env'))

@cross_origin()
@app.route('/tweet/all', methods=['GET'])
def selectAllTweet():
    hashtag = "#"+request.args.get("hashtag")
    page = request.args.get("page")
    result = Tweet.query.filter_by(search_val=hashtag).paginate(int(page),20,False).items
    return json.dumps(result, cls=AlchemyEncoder)

@cross_origin()
@app.route('/tweet/count', methods=['GET'])
def countTweet():
    hashtag = "#"+request.args.get("hashtag")
    count = Tweet.query.filter_by(search_val=hashtag).count()
    return json.dumps({"count":count})

@cross_origin()
@app.route('/tweet/detail', methods=['GET'])
def selectSingleTweet():
    id = request.args.get("id")
    result = Tweet.query.get(id)
    return json.dumps(result, cls=AlchemyEncoder)

@cross_origin()
@app.route('/tweet/sentiment', methods=['GET'])
def sentimentCount():
    hashtag = "#"+request.args.get("hashtag")
    sql = db.text('SELECT classification_result AS label, COUNT(`classification_result`) AS result FROM tweet WHERE search_val="'+hashtag+'" GROUP BY(classification_result)')
    result = db.engine.execute(sql)
    result_json = jsonify({'result': [dict(row) for row in result]})
    return result_json

@cross_origin()
@app.route('/tweet/crawl', methods=['POST'])
def crawlTweet():
    classifier = TweetClassifier()
    hashtag = request.get_json()['hashtag']
    hashtag = "#"+hashtag
    tweetsPerQry = 100
    maxTweets = 300#1000000
    authentication = tweepy.OAuthHandler(environ.get("CONSUMER_KEY"), environ.get("CONSUMER_SECRET"))
    authentication.set_access_token(environ.get("ACCESS_TOKEN"), environ.get("ACCESS_SECRET"))
    api = tweepy.API(authentication, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    maxId = -1
    tweetCount = 0
    while tweetCount < maxTweets:
        if(maxId <= 0):
            newTweets = api.search(q=hashtag, count=tweetsPerQry, result_type="recent", tweet_mode="extended")
        else:
            newTweets = api.search(q=hashtag, count=tweetsPerQry, max_id=str(maxId - 1), result_type="recent", tweet_mode="extended")

        if not newTweets:
            return json.dumps("Finish")
            break
    
        val = []
        for tweet in newTweets:
            id = tweet.id
            id = str(id)
            created_at = tweet.created_at
            local_created_at = created_at.replace(tzinfo=timezone.utc).astimezone(tz=None)
            text = tweet.full_text.encode('utf-8')
            feeds_image = None
            feeds_video = None
            feeds_link = 'https://twitter.com/_/status/'+id
            source = tweet.source
            in_reply_to_status_id = tweet.in_reply_to_status_id_str
            in_reply_to_user_id = tweet.in_reply_to_user_id_str
            in_reply_to_screen_name = tweet.in_reply_to_screen_name
            user_name = tweet.user.name
            user_screen_name = tweet.user.screen_name
            user_location = tweet.user.location
            user_url = tweet.user.url
            user_description = tweet.user.description
            user_verified_str = tweet.user.verified
            user_verified = 0
            if user_verified_str == True:
                user_verified = 1
            user_followers_count = tweet.user.followers_count
            user_friends_count = tweet.user.friends_count
            user_listed_count = tweet.user.listed_count
            user_favourites_count = tweet.user.favourites_count
            user_created_at = tweet.user.created_at
            user_id = tweet.user.id
            user_profile_image_url_https = tweet.user.profile_image_url_https
            if tweet.coordinates == True:
                coordinates_lat = tweet.coordinates.coordinates[0]
                coordinates_lon = tweet.coordinates.coordinates[1]
            else:
                coordinates_lat = None
                coordinates_lon = None
                        
            if tweet.place == True:
                place_country = tweet.place.country
                place_country_code = tweet.place.country_code
                place_full_name = tweet.place.full_name
                place_id = tweet.place.id
                place_type = tweet.place.type
            else:
                place_country = None
                place_country_code = None
                place_full_name = None
                place_id = None
                place_type = None

            if tweet.is_quote_status == True:
                quoted_status_id = tweet.quoted_status_id
                quote_count = 0
            else:
                quoted_status_id = None
                quote_count = 0
                retweeted_status = None
            try:
                reply_count = tweet.reply_count
            except:
                reply_count = 0
            retweet_count = tweet.retweet_count
            favorite_count = tweet.favorite_count
            retweeted_txt = tweet.retweeted
            entities = str(tweet.entities)
            retweeted = 0
            if retweeted_txt == True:
                retweeeted = 1
            lang = tweet.lang

            textPreprocess = classifier.preProcess(text)
            classification_result = classifier.predict([textPreprocess]) 
            classification_result = int(classification_result)
            
            new_data = Tweet(
                search_val=hashtag,
                classification_result=classification_result,
                created_at=local_created_at,
                tweet_id=id,
                text=text,
                source=source,
                in_reply_to_status_id=in_reply_to_status_id,
                in_reply_to_user_id=in_reply_to_user_id,
                in_reply_to_screen_name=in_reply_to_screen_name,
                user_name=user_name,
                user_screen_name=user_screen_name,
                user_location=user_location,
                user_url=user_url,
                user_description=user_description,
                user_verified=user_verified,
                user_followers_count=user_followers_count,
                user_friends_count=user_friends_count,
                user_listed_count=user_listed_count,
                user_favourites_count=user_favourites_count,
                user_created_at=user_created_at,
                user_id=user_id,
                user_profile_image_url_https=user_profile_image_url_https,
                coordinates_lat=coordinates_lat,
                coordinates_lon=coordinates_lon,
                place_country=place_country,
                place_country_code=place_country_code,
                place_full_name=place_full_name,
                place_id=place_id,
                place_type=place_type,
                quoted_status_id=quoted_status_id,
                retweeted_status=retweeted_status,
                quote_count=quote_count,
                reply_count=reply_count,
                retweet_count=retweet_count,
                favorite_count=favorite_count,
                retweeted=retweeted,
                entities=entities,
                lang=lang,
                feeds_link=feeds_link,
                feeds_video=feeds_video,
                feeds_image=feeds_image
            )
            db.session.add(new_data)
            db.session.commit() 
            print(str(id)+":"+str(text)+"\n\n")
        tweetCount += len(newTweets)
        maxId = newTweets[-1].id
    return json.dumps({"status":1})

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

