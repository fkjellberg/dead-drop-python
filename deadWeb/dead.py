from datetime import datetime
import os
from flask import Flask, render_template, send_from_directory, request, Response, jsonify
from pymongo import MongoClient
import uniqid


class DropHandler:

    client = None

    def __init__(self, db):
        self.client = db.dead
        pass

    def get_timed_key(self):
        drop_id = uniqid.uniqid()
        
        self.client.formKeys.insert_one({"key": drop_id,"created": datetime.now()})
        return drop_id

    def pickup(self, drop_id):
        cursor = self.client.drop.find({"key" :drop_id})
        tmp_data = []
        for document in cursor:
            tmp_data = document
            cursor = self.client.drop.remove({"key" :id})
            break

        if tmp_data:

            #handle old drops without createdDate
            if "createdDate" in tmp_data:
                # Do not return drops > 24 hours old
                time_delta = datetime.now()  - tmp_data["createdDate"]

                if time_delta.days > 1:
                    print("too old, retunring None")
                    return []

            return tmp_data["data"]

        return []

    def drop(self, data):
        key = uniqid.uniqid()
        self.client.drop.insert_one({"key" :key, "data":data, "createdDate":datetime.now()})
        return key



HANDLER = DropHandler(MongoClient())

APP = Flask(__name__)

@app.route("/")
def index():
    """ just return the index template"""
    return render_template('index.htm', timedKey=handler.get_timed_key())

@app.route('/images/<path:path>')
def send_images(path):
    """load images from drive path"""
    return send_from_directory('images', path)

@app.route('/js/<path:path>')
def send_js(path):
    """load js from drive path"""
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    """load css from drive path"""
    return send_from_directory('css', path)


@app.route("/drop", methods = ['POST'])
def drop():
    """ok, looks alright"""
    key = handler.drop(request.form["data"])
    return jsonify(id=key)

@app.route("/pickup/<drop_id>")
def pickup_drop_index(drop_id):
    """Load the pickup HTML"""
    return render_template('index.htm', id=drop_id)


@app.route("/getdrop.php?id=<drop_id>")
@app.route("/drop/<drop_id>")
def pickup_drop_json(drop_id):
    """Actually get the drop from the DB"""
    return_data = handler.pickup(drop_id)
    return  Response(return_data, mimetype='application/json')
