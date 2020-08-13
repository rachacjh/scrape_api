import flask
from flask import request
from pymongo import MongoClient
from bson import json_util, ObjectId
import json
from scrape import scrape_class
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=["GET"])
def home():
    return ("Welcome.")

@app.route('/nlp', methods=["GET"])
def getnlp():
    nlp = spacy.load('en_core_web_sm')
    client = MongoClient('mongodb://18.217.89.210:27017/')
    reviews = client.local.reviews
    product = reviews.find_one({"url":request.form['url']})
    product = json.loads(json_util.dumps(product))
    all_pairs = []
    final_pairs = []
    analyser = SentimentIntensityAnalyzer()
    for review in product['reviews']:
        filtered_pairs = []
        senti_original = analyser.polarity_scores(review)['compound']
        current_smallest_difference = 1
        doc = nlp(review)
        for i, token in enumerate(doc):
            if token.pos_ not in ('NOUN', 'PROPN'):
                continue
            for j in range(i+1, len(doc)):
                if doc[j].pos_ == 'ADJ':
                    score_difference = abs(analyser.polarity_scores(str(token) + " " + str(doc[j]))['compound'] - senti_original)
                    if score_difference > current_smallest_difference:
                        continue
                    else:
                        all_pairs.append((str(token),str(doc[j])))
                        if score_difference < current_smallest_difference:
                            current_smallest_difference = score_difference
                            if len(filtered_pairs) > 0:
                                filtered_pairs.pop()
                            filtered_pairs.append((str(token),str(doc[j])))
                    break
        final_pairs.extend(filtered_pairs)
    print(all_pairs)
    print(final_pairs)
    return json.loads(json.dumps({"response": "Found pairs",
                                  "final_pairs": json.dumps(dict(final_pairs)),
                                  "all_pairs": json.dumps(dict(all_pairs))
                                  }))

@app.route('/reviews', methods=["GET"])
def get_reviews():
    client = MongoClient('mongodb://18.217.89.210:27017/')
    reviews = client.local.reviews
    product = reviews.find_one({"url":request.form['url']})
    product = json.loads(json_util.dumps(product))
    return product

@app.route('/reviews', methods=["PUT"])
def put_reviews():
    client = MongoClient('mongod://18.217.89.210:27017/')
    reviews = client.local.reviews
    if reviews.find_one({'url':request.form['url']}) ==  None:
        return json.loads(json.dumps({"response": "No such product from url " + request.form['url'] + " can be found in the database. Use 'POST' instead."}))
    else:
        scraper = scrape_class(str(request.form['url']))
        scraped_dict = scraper.scrape_reviews()
        object_id = reviews.update({'url':request.form['url']},scraped_dict)
        print("Object id: ", object_id)
        product = reviews.find_one({"_id": ObjectId(object_id)})
        product = json.loads(json_util.dumps(product))
        return product

@app.route('/reviews', methods=["POST"])
def post_reviews():
    print(request.form['url'])
    client = MongoClient('mongodb://18.217.89.210:27017/')
    reviews = client.local.reviews
    if reviews.find_one({'url':request.form['url']}) ==  None:
        scraper = scrape_class(str(request.form['url']))
        scraped_dict = scraper.scrape_reviews()
        object_id = reviews.insert(scraped_dict)
        print("Object id: ",object_id)
        product = reviews.find_one({"_id": ObjectId(object_id)})
        product = json.loads(json_util.dumps(product))
        return product
    else:
        return json.loads(json.dumps({"response": "Product from url "+request.form['url']+" already has a record in the database."}))

@app.route('/reviews', methods=["DELETE"])
def delete_reviews():
    client = MongoClient('mongodb://18.217.89.210:27017/')
    reviews = client.local.reviews
    reviews.remove({"url":request.form['url']})
    return json.loads(json.dumps({"response": "Product from url "+request.form['url']+" has been deleted from the database."}))

if __name__ == "__main__":
    app.run()
