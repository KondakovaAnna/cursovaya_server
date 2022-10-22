

from logging import exception
from flask import Flask
import flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import cast, String

from servercode.predict import Model_predictor, MyResNet18, Idle, init_weights
from servercode.image_loader import read_image

from datetime import datetime as dt

from models import *

import base64

app = Flask(__name__)

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost:3306/findaplant'

db = SQLAlchemy(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

'''
Внешний вид входного json:
    userid: int
    date: string 
    langitude: float
    latitude: float
    image_data: string base64

Описание работы функции
    проверяем есть ли пользователь с таким id в базе
    если он есть 
    проверяем есть ли локешн в таблице локейшн по langitude и langitude
    предсказываем растение по картинке
    создаём запись в хистори 

    возвращаем пользователю описание растения
'''
@app.route("/predict", methods=["POST"])
def predict():
    if flask.request.method == "POST":
        #Достаём данные из json
        json = flask.request.get_json()
        if "userid" in json:
            usrid_id = json['userid']
        else:
            return 'key userid didn t specifiyed', 400

        if "date" in json:
            date = json['date']
        else:
            return 'key date didn t specifiyed', 400

        if "longitude" in json:
            mylongitude = json['longitude']
        else:
            return 'key longitude didn t specifiyed', 400

        if "latitude" in json:
            mylatitude = json['latitude']
        else:
            return 'key latitude didn t specifiyed', 400

        user =  db.session.query(Users).filter_by(id=usrid_id).first() 
        location = db.session.query(Location).filter(cast(Location.latitude, String()).like('%' + str(mylatitude) + '%'), cast(Location.longitude, String()).like('%' + str(mylongitude) + '%')).first()
        if user is not None:
            user_id = user.id
            print(location)
            if location is not None:
                location_id = location.id
            else:
                location = Location(latitude=mylatitude, longitude=mylongitude)
                       
                location_id = db.session.query(func.max(Location.id)).scalar()
                db.session.add(location)
                db.session.commit()


                
            new_history = History(peson = user_id, location_id=location_id + 1, time=dt.strptime(date, '%d/%m/%Y'), plants_id = 1)

            db.session.add(new_history)
            db.session.commit()

        return flask.jsonify({"userid": usrid_id,"date": date,"longitude": mylongitude,"latitude": mylatitude})

    '''
        if flask.request.files.get("image"):
            image = read_image(flask.request.files["image"].read())
            image = model.preproprocess_image(image)
            prediction = model.prdict_with_model(image)
            print(prediction)
    return flask.jsonify(prediction)'''
            
@app.route("/create_plants_database", methods=["POST"])
def create_plants_database():
    json = flask.request.get_json()
    for name, new_info in json.items():
        plant = db.session.query(Plants).filter(Plants.name == name).first()
        if plant is not None:
            plant.info = new_info
        else:
            new_plant = Plants(name=name, info=new_info)
            db.session.add(new_plant)
        
    db.session.flush()
    db.session.commit()

    resp = flask.jsonify(success=True)
    return resp

@app.route("/registration", methods=["POST"])
def registration():
    json = flask.request.get_json()
    for username, pwd in json.items():
        user = db.session.query(Users).filter(Users.login == username).first()
        if user is not None:
            return {'status': 'Login already taken'}
        else:
            encrypt_password =  base64.b64encode(pwd.encode("utf-8")) 
            new_user = Users(login=username, password=encrypt_password)
            db.session.add(new_user)

    db.session.flush()
    db.session.commit()

    resp = flask.jsonify(success=True)
    return resp

@app.route("/sign_in", methods=["POST"])
def sign_in():
    json = flask.request.get_json()
    for username, pwd in json.items():
        user = db.session.query(Users).filter(Users.login == username).first()
        if user is not None:
            if base64.b64decode(user.password) != pwd:
                return {'status': 'Sucsess'}
            else:
                return {'status': 'Invalid password'} 
            
        else:
            return {'status': 'Invalid login'} 




if __name__ == '__main__':
    model = Model_predictor()
    ##
    app.run()

