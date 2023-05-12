

from logging import exception
from flask import Flask
import flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
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
db.textsize = 10000
@app.route("/predict", methods=["POST"])
def predict():
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            image = read_image(flask.request.files["image"].read())
            image = model.preproprocess_image(image)
            prediction = model.prdict_with_model(image)
            print(prediction)
    return flask.jsonify(prediction) #дбавить сгенерированый айдишник в ответ

@app.route("/data", methods=["POST"])
def data():
    print("start data")
    if flask.request.method == "POST":
#Достаём данные из json
        print("start")
        json = flask.request.get_json()
        print("json:", json)
        if "plantid" in json:
            plantid = json['plantid']
            print("plan id:", plantid)
        else:
            print("fale plan id:", plantid)
            return 'key plantid didn t specifiyed', 400

        if "userid" in json:
            usrid_id = json['userid']
            print("user id:", usrid_id)
        else:
            return 'key userid didn t specifiyed', 400

        if "date" in json:
            date = json['date']
            print("date:", date)
        else:
            return 'key date didn t specifiyed', 400

        if "longitude" in json:
            mylongitude = json['longitude']
            print("longitude:", mylongitude)
        else:
            return 'key longitude didn t specifiyed', 400

        if "latitude" in json:
            mylatitude = json['latitude']
            print("latitude:", mylatitude)
        else:
            return 'key latitude didn t specifiyed', 400

        print("after")      
        user =  db.session.query(Users).filter_by(id=usrid_id).first() 
        plant =  db.session.query(Plants.name).filter_by(id=plantid).first() 
        plant_info =  db.session.query(Plants).filter_by(id=plantid).first().info
        picture =  db.session.query(Plants.picture).filter_by(id=plantid).first()
        print("plant:",plant)
        print("info:",plant_info)
        print("picture:",picture)
        location = db.session.query(Location).filter(cast(Location.latitude, String()).like('%' + str(mylatitude) + '%'), cast(Location.longitude, String()).like('%' + str(mylongitude) + '%')).first()
        if user is not None:
            user_id = user.id
            if location is not None:
                location_id = location.id
            else:
                location = Location(latitude=mylatitude, longitude=mylongitude)
                location_id = db.session.query(func.max(Location.id)).scalar()
                db.session.add(location)
                db.session.commit()

            new_history = History(peson = user_id, location_id=location_id + 1, time=dt.strptime(date, '%d/%m/%Y'), plants_id = plantid)

            db.session.add(new_history)
            db.session.commit()

        return flask.jsonify({"plantname": str(plant),"plantinfo": str(plant_info),"picture": str(picture)})

@app.route("/histories", methods=["POST"])
def histories():
    if flask.request.method == "POST":
#Достаём данные из json
        json = flask.request.get_json()
        if "userid" in json:
            usrid_id = json['userid']
            print("user id:", usrid_id)
        else:
            return 'key userid didn t specifiyed', 400

        user =  db.session.query(Users).filter_by(id=usrid_id).first() 

        if user is not None:
            user_id = user.id
        print("user: ", user_id)
        
        user_histories = db.session.query(History).filter_by(peson=user_id)
        
        response = []
        for hi in user_histories:
            resp = {"date": str(hi.time), "plant": {}}
            plant_table = db.session.query(Plants).filter_by(id=hi.plants_id).first()
            resp["plant"]["plantname"] = str(plant_table.name)
            resp["plant"]["plantinfo"] = str(plant_table.info)
            resp["plant"]["picture"] = str(plant_table.picture).replace('\\','\\\\')
            location_table = db.session.query(Location).filter_by(id=hi.location_id).first()
            resp["longitude"] = (location_table.longitude)
            resp["latitude"] = (location_table.latitude)
            response.append(resp)
        # plants_names = [str(db.session.query(Plants.name).filter_by(id=r).first()) for r in plants_ides]
        # plants_infos= [str(db.session.query(Plants.info).filter_by(id=r).first()) for r in plants_ides]
        # plants_pictures = [str(db.session.query(Plants.picture).filter_by(id=r).first()) for r in plants_ides]
        # plants_latitudes = [str(db.session.query(Location.latitude).filter_by(id=r).first()) for r in location_ides]
        # plants_longitudes = [str(db.session.query(Location.longitude).filter_by(id=r).first()) for r in location_ides]
        # return flask.jsonify({"plantsnames": plants_names,"plantsinfos": plants_infos,"pictures": plants_pictures, "latitude": plants_latitudes, "longitudes": plants_longitudes, "plantstime": plants_time})
        return flask.jsonify(response)
            
@app.route("/create_plants_database", methods=["POST"])
def create_plants_database():
    json = flask.request.get_json()
    for name, new_info in json.items():
        plant = db.session.query(Plants).filter(Plants.name == name).first()
        if plant is not None:
            plant.info = new_info[0]
            #plant.picture = new_info[1]
        else:
            new_plant = Plants(name=name, info=new_info[0], picture = new_info[1])
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
    app.run(host='0.0.0.0', port=80)

