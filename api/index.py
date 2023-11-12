from flask import Flask, make_response, jsonify, request
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

# con = connect(
#     host="mongodb+srv://Cluster0.fcrlokx.mongodb.net/?retryWrites=true&w=majority",
#     username = "user322",
#     password = "rosewall16",
#     db = "valeriia_baz_db")

# collections=con['valeriia_baz_db'].list_collection_names()
# for col in collections:
#     print(col)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

### API Methods     

# Register new user
@app.route("/register", methods=['POST'])
def register():
    # Generate user_id
    userId = generateUserId()
    while isUserExists(userId) == True:
        userId = generateUserId()
        
    # Creating models to be written to the database    
    newUser = User(name = request.form.get("name"),
                   email = request.form.get("email"),
                   login = request.form.get("login"),
                   dateReg = datetime.now(),
                   userId = userId
                   )
    pasUser = UserPassword(userId = userId,
                           password = request.form.get("password"),
                           login = request.form.get("login")
                           )
    statistics = Statistics(user_id = userId,
                            calm_mins = 0,
                            ratings = []
                            )
    
    newUser.save()
    pasUser.save()
    statistics.save()
    
    return {
        "title" : "Success registration",
        "userId" : userId
    }

# Check if the user exists    
def isUserExists(userId):
    isExists = False
    for item in UserPassword.objects:
        if item.userId == userId:
            isExists = True
            return isExists 
        else:
            isExists = False
    return isExists        
    
def generateUserId():
    return randint(1, 1_000_000)  

@app.route("/hello", methods=['GET'])
def hello():  
    return "Hello"

@app.route("/users", methods=['GET'])
def users():  
    collection = db.User
    
    json_docs = [json.loads(json_util.dumps(doc)) for doc in collection.find()]

    return json.dumps(json_docs)

# Log in and get the user's data
@app.route("/login", methods=['POST'])
def login():
    psrds = db.UserPassword
    users = db.User
    # At the login we get a username and password
    data = request.get_json()
    login = data['login']
    password = data['password']
    userId = 0
    
    model = {}
    response = None
    
    # Find a user in the database
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
                        "calm_mins" : usr['calm_mins']
                        }
                    response = make_response(jsonify({'success': True, 'data': model}), 200)
                    response.headers['Content-Type'] = 'application/json'
                    response.headers['Access-Control-Allow-Origin'] = '*'
    
    # Returning the answer
    if response == None:
        response = {
            'message' : "Wrong login or password. Please, try again"
        }
        return response
    
    return response

# Getting the tip of the day from a third-party API
@app.route('/advice', methods=['GET']) 
def getAndSendAdvice():
    advice = requests.get('https://api.adviceslip.com/advice')
    response = make_response(jsonify({'success': True, 'data': advice.json()['slip']['advice']}), 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# The user rates his current mood on a scale of 1-5 using emoji, where 1 is very bad and 5 is very good
@app.route('/saveMood', methods=['POST']) 
def setCurrentMood():
    data = request.get_json()
    user_id = data['user_id']
    mood = data['mood']
    
    currentMood = UserDayMood()
    currentMood.user_id = user_id
    currentMood.date = datetime.now()
    currentMood.mood = mood
    
    currentMood.save()
    
    response = make_response(jsonify({'success': True, 'message': "Mood successfully recorded!"}), 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
    
# Recover password
@app.route("/reset/password", methods=['POST'])
def resetPassword():
    # You can enter your login or email to recover your password
    email = request.form.get("email")
    login = request.form.get("login")
    
    emailToSend = None
    
    # Find out if there is a login or password in the database
    if email != None:
        for user in User.objects:
            if user.email == email:
                emailToSend = email 
                break
    elif login != None:
        for user in User.objects:
            if user.login == login:
                emailToSend = user.email 
                break
    
    if emailToSend != None:
        return sendEmail(emailToSend)
    else:
        return "The user with the specified username/password does not exist"

# Send a link to recover your password    
def sendEmail(email):
    return "Email send!"
                
### 1 Screen    
# Getting data for the activity screen
@app.route('/activities', methods=['GET'])
def sendActivities():
    # Retrieve product categories and products from the database
    categoryTypes = CategoryTypes.objects
    products = Product.objects   
    
    response = {}
    response["categoryTypes"] = []
    
    # Cycle to find all activities and return them for display
    for type in categoryTypes:
        categoriesOfType = []
        
        for prod in products:
            if prod.categoryType == type.typeId:
                categoriesOfType.append({
                    "name" : prod.prod_name,
                    "categoryId" : prod.prod_id
                })
        
        resp = {
            "typeId" : type.typeId,
            "type" : type.type,
            "categories" : categoriesOfType
        }
        response["categoryTypes"].append(resp)    
 
    return response                     

# Find the activity rating 
def findRatingForActivity(techId, userId):
    ratings = []
    for item in Statistics.objects:
        if item.user_id == int(userId):
            ratings = item.ratings
            break
    
    # Matching techId        
    result = 0
    for rate in ratings:
        if rate['tech_id'] == int(techId):
           result = rate['rating']
           break
    
    return result       

# Launch a technique and get a user rating for it
@app.route('/activities/techniques/start', methods=['GET'])
def startTechnic():
    # To enter, expect a technique id
    techId = request.args.get("tech_id")
    userId = request.args.get("user_id")
    technic = {}

    # Find a technique in the database
    for item in Techniques.objects:
        if int(techId) ==  item.tech_id:
            technic = item.to_json()
            break
        
    return {
        'technic' : technic,
        'rating' : findRatingForActivity(techId, userId)
    }
    
# Evaluating activity techniques
@app.route('/activities/techniques/rate', methods=['POST'])
def rateTechic():
    # For input we expect tech_id, user_id and new rating
    techId = request.form.get("tech_id")
    userId = request.form.get("user_id")
    rate = request.form.get("rating")
    
    statItem = {}
    ratings = []
    
    # Find user ratings
    for item in Statistics.objects:
        if item.user_id == int(userId):
            ratings = item.ratings
            break
    
    # Find an estimate of the technique, if it already exists
    selectedTechRating = 0
    for item in ratings:
        if item['tech_id'] == int(techId):
           selectedTechRating = item['rating']
           statItem = item
           break
    
    # Creating a new rating model
    newRating = {
        'rating' : int(rate),
        'tech_id' : int(techId)
    }
    
    # If there has been no assessment of a technique, we add a new one, otherwise we overwrite the old one
    userId = int(userId)
    if selectedTechRating == 0:
        Statistics.objects(user_id=userId).update_one(push__ratings = newRating)
        return "New rating was added"
    else:
        Statistics.objects(user_id=userId).update_one(pull__ratings = statItem)
        Statistics.objects(user_id=userId).update_one(push__ratings = newRating)
        return "Your old rating was overwriten"
    
### 2 Screen
# Get the username of the user (in fact, we already returned it during login, but in case the programmers need the data again)
@app.route('/user', methods=['GET']) 
def sendUser():
    response = {}
    # We expect a user id for input
    userId = request.args.get("user_id")
    
    # Find the user and bring him back
    for user in User.objects:
        if str(user.userId) == userId:
            response = {
                "userId" : user.userId,      
                "name" : user.name,
                "email" : user.email
                }
    
    if response != {}:
        return response         
    else: 
        return "User not found"

### 3 Screen

# Getting user ratings
@app.route('/user/ratings', methods=['GET'])
def sendRatings():
    # We expect a user id for input
    userId = request.args.get("user_id")
    
    statRatings = {}
    
    # Find the data from the table with statistics
    for item in Statistics.objects:
        if item.user_id == int(userId):
            statRatings = {
            "ratings" : item.ratings
            }

    # Finding activity ratings
    techIds = []
    ratingsValues = []  
    for item in statRatings['ratings']:  
        techIds.append(item['tech_id']) 
        ratingsValues.append(item['rating'])  
    
    # Use the id of the ratings to find their names
    ratings = []
    for item in Techniques.objects:
        if item.tech_id in techIds:
            idx = techIds.index(item.tech_id)
            rating = {
                "name" : item.name,
                "rating" : ratingsValues[idx]
            }
            ratings.append(rating)
    
    response = {
        'ratings' : ratings
    }
    
    return response
    
# When closing the app
@app.route('/end', methods=['GET'])
def onEnd():
    # We expect a user id for input
    userId = request.args.get("user_id")
    calmMins = 0
    launchTime = 0
    
    for item in Statistics.objects:
        if item.user_id == int(userId):
            calmMins = item.calm_mins
            break
    
    for user in User.objects:
        if user.userId == int(userId):
            launchTime = user.launchTime
            break
                    
    endTime = time.time()
    totalInApp = endTime - launchTime
    calmMins = calmMins + totalInApp / 60
    Statistics.objects(user_id=int(userId)).update_one(set__calm_mins = int(calmMins))
    
    return "Success"

# Models

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
    
class CategoryTypes(DynamicDocument):
    type: StringField()
    typeId: IntField()

class Product(DynamicDocument):
    prod_id: IntField()
    prod_name: StringField()   
    categoryType: IntField() 
    techniques: ListField(StringField())
    
class Rating(DynamicDocument):
    tech_id: IntField()
    rating: FloatField()       
    
class Statistics(DynamicDocument):
    user_id: IntField()
    calm_mins: IntField()
    ratings: ListField(Rating)
    
class UserDayMood(DynamicDocument):
    user_id: IntField()
    date: DateField()  
    mood: IntField()  
    
class Techniques(DynamicDocument):
    name: StringField()
    description: StringField()
    effect: StringField()
    example: StringField()  
    tech_id: IntField() 