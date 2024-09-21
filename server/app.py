#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def campers():

    if request.method == 'GET':

        campers = Camper.query.all()

        campers_list = [camper.to_dict() for camper in campers]

        return campers_list, 200

    else:
        
        if request.method == 'POST':
            
            data = request.get_json()

            if not data.get('name') or not isinstance(data['name'], str):
                return {'errors': ['Name is required and must be a valid string.']}, 400
            if not isinstance(data.get('age'), int) or not (8 <= data['age'] <= 18):
                return {'errors': ['Age must be a number between 8 and 18.']}, 400
            
            try:
                new_camper = Camper(
                    name=data['name'],
                    age=data['age']
                )
                
                db.session.add(new_camper)
                db.session.commit()
                
                return new_camper.to_dict(), 201

            except ValueError as e:
                return {'errors': [str(e)]}, 400
   
@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def campers_by_id(id):

    if request.method == 'GET':

        camper = Camper.query.filter(Camper.id == id).first()

        if camper:
            return {
            'id': camper.id,
            'name': camper.name,
            'age': camper.age,
            'signups': [{'activity': signup.activity.name, 'time': signup.time} for signup in camper.signups]
        }, 200
        return {'error': 'Camper not found'}, 404
    
    else:

        if request.method == 'PATCH':
        
            camper = Camper.query.filter(Camper.id == id).first()

            if not camper:
                return {'error': 'Camper not found'}, 404

            data = request.get_json()

        if 'name' in data:
            if not data['name']: 
                return {'errors': ['validation errors']}, 400
            camper.name = data['name']
    
        if 'age' in data:
            try:
                age = int(data['age'])  
                if age <= 0: 
                    return {'errors': ['validation errors']}, 400
                camper.age = age
            except (ValueError, TypeError):
                return {'errors': ['validation errors']}, 400

        db.session.commit()

        return {
            'id': camper.id,
            'name': camper.name,
            'age': camper.age,
            'signups': [{'activity': signup.activity.name, 'time': signup.time} for signup in camper.signups]
        }, 202


@app.route('/activities', methods=['GET'])
def activities():

    activities = Activity.query.all()

    activity_list = [activity.to_dict() for activity in activities]

    return activity_list, 200

@app.route('/activities/<int:id>', methods=['DELETE'])
def activities_by_id(id):

    activity = Activity.query.filter(Activity.id == id).first()

    if not activity:
        return{'error': 'Activity not found'}, 404
        
    db.session.delete(activity)
    db.session.commit()

    return '', 204

@app.route('/signups', methods=['POST'])
def signups():
    
    data = request.get_json()

    if not data:
        return {'errors': ["validation errors"]}, 400
            
    try:
        new_signup = Signup(
            time=data['time'],
            camper_id=data['camper_id'],
            activity_id=data['activity_id']
            )
                
        db.session.add(new_signup)
        db.session.commit()
                
        return new_signup.to_dict(), 201

    except ValueError as e:
        return {'errors': ["validation errors"]}, 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
