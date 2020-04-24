import re
from nltk.tokenize import word_tokenize
from string import punctuation
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from string import punctuation
import pickle
from os import path
current_dir = path.abspath(path.dirname(__file__))
model_pipeline = path.join(current_dir, 'model_pipeline.pkl')

class TweetClassifier:
    def __init__(self):
        self.classify = pickle.load(open(model_pipeline, "rb"))

    def preProcess(self, tweet):
        ps = PorterStemmer()
        negation_list = ["arent","isnt","dont","doesnt","not","cant","couldnt", "werent",
                 "wont","didnt","never","nothing","nowhere","noone","none"
                "hasnt","hadnt","shouldnt","wouldnt","aint"]
        tweet = tweet.decode('utf-8').lower()
        tweet = re.sub('n[^A-Za-z ]t','nt', tweet)
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '', tweet)
        tweet = re.sub('@[^\s]+', '', tweet)
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        tweet = word_tokenize(tweet)
        tweet_list = [];
        negate = False
        for word in tweet:
            word = ps.stem(word)
            if word in negation_list:
                negate = True
            elif negate is True and word in list(punctuation):
                negate = False
            
            if negate and word not in negation_list:
                word = "not_"+word
            else:
                pass
            word = re.sub('[^A-Za-z_ ]+', '', word)
            if len(word) > 2 and word not in stopwords.words('english'):
                tweet_list.append(word)
        tweet_set = set(tweet_list)
        return " ".join(tweet_set)

    def predict(self, tweet):
        result = self.classify.predict(tweet)[0]
        return result