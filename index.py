from flask import Flask, make_response, jsonify, request, render_template
from flask_cors import CORS
import time
from mongoengine import *
from datetime import datetime
import requests
from random import randint
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import json_util
import json

app = Flask("APP")
CORS(app)

uri = "mongodb+srv://user322:rosewall16@Cluster0.fcrlokx.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.valeriia_baz_db

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/users", methods=['GET'])
def users():  
    collection = db.User
    
    json_docs = [json.loads(json_util.dumps(doc)) for doc in collection.find()]

    return json.dumps(json_docs)

@app.route("/login", methods=['POST'])
def login():
    psrds = db.UserPassword
    users = db.User

    data = request.get_json()
    login = data['login']
    password = data['password']
    userId = 0
    
    model = {}
    response = None
    
    for psrd in psrds.find():
        item = json.loads(json_util.dumps(psrd))
        if item['login'] == login and item['password'] == password:
            userId = item['userId']
            for user in users.find():
                usr = json.loads(json_util.dumps(user))
                if usr['userId'] == userId:
                    model = {
                        "userId" : usr['userId'],
                        "name" : usr['name'],
                        "email" : usr['email'],
                        "calm_mins" : usr['calm_mins'],
                        "last_mood" : usr['last_mood']
                        }
                    response = make_response(jsonify({'success': True, 'data': model}), 200)
                    response.headers['Content-Type'] = 'application/json'
                    response.headers['Access-Control-Allow-Origin'] = '*'
    
    if response == None:
        response = {
            'message' : "Wrong login or password. Please, try again"
        }
        return response
    
    return response

@app.route('/advice', methods=['GET']) 
def getAndSendAdvice():
    advice = requests.get('https://api.adviceslip.com/advice')
    response = make_response(jsonify({'success': True, 'data': advice.json()['slip']['advice']}), 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/saveMood', methods=['POST']) 
def setCurrentMood():
    data = request.get_json()
    user_id = data['user_id']
    mood = data['mood']
    
    currentMood = {
        'user_id': user_id,
        'date': datetime.now(),
        'mood': mood
    }
    
    updateFilter = {
        'user_id': user_id
    }
    update = {
        '$set': {'last_mood': mood}
    }
    
    db.UserDayMood.insert_one(currentMood)
    db.User.update_one(updateFilter, update)
    
    response = make_response(jsonify({'success': True, 'message': "Mood successfully recorded!"}), 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
 
class User(DynamicDocument):
    userId: IntField(required=True)
    name: StringField()
    email: StringField()
    login: StringField()
    dateReg: DateField()
    launchTime: FloatField()
    calm_mins: IntField()
    
class UserPassword(DynamicDocument):
    userId: IntField(required=True)
    password: StringField()
    login: StringField()

class Product(DynamicDocument):
    prod_id: IntField()
    prod_name: StringField()   
    categoryType: IntField() 
    techniques: ListField(StringField())
    
class UserDayMood(DynamicDocument):
    user_id: IntField()
    date: DateField()  
    mood: IntField()  
