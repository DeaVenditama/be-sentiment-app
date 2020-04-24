from flask import request, render_template, make_response
from datetime import datetime as dt
from flask import current_app as app
from ..Models.Hashtag import db, Hashtag
from ..helper.encoder import AlchemyEncoder
from flask_cors import cross_origin
import json

@cross_origin()
@app.route('/hashtag/all', methods=['GET'])
def selectAllHashtag():
    result = Hashtag.query.all()
    return json.dumps(result, cls=AlchemyEncoder)

@cross_origin()
@app.route('/hashtag/insert', methods=['POST'])
def insertHashtag():
    hashtag = request.get_json()['hashtag']
    new_data = Hashtag(hashtag=hashtag)
    db.session.add(new_data)
    db.session.commit()
    return json.dumps({"status":1})
    

@cross_origin()
@app.route('/hashtag/delete', methods=['POST'])
def deleteHashtag():
    id = request.get_json()['id']
    hashtag = Hashtag.query.get(id)
    db.session.delete(hashtag)
    db.session.commit()
    return json.dumps({"status":1})


