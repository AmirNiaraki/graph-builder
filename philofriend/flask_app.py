'''
To run the flask app in the background:
nohup gunicorn -w 5 -b 0.0.0.0:8000 flask_app:app 

To check for all gunicorn processes:
ps -ef | grep gunicorn

To kill all gunicorn process:
pkill gunicorn

GET
POST
PUT
DELETE
'''

from flask import Flask, jsonify, request
import time
from wisdom_engine import WisdomEngine
import random




app=Flask(__name__)


@app.route('/name')
def get_name():
    print('returned name')
    return 'Philo API'


@app.route('/version')
def get_version():
    print('returned version')
    return '1.0.0'

@app.route("/get_user/<user_id>", methods=['GET'])
def get_user(user_id):
    print(f'returned user {user_id}')
    user_data= {
        'user_id': user_id,
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'age': 30
    }
    # return user_data
    extra = request.args.get('extra')
    if extra:
        user_data['extra'] = extra
    return jsonify(user_data), 200

@app.route("/create_user", methods=['POST'])
def create_user():
    
    data=request.get_json()
    return jsonify(data), 201

@app.route("/create_story", methods=['POST'])
def create_story():
    data=request.get_json()
    reflection_summary=data.get('reflection_summary')
    # engine=WisdomEngine()
    if reflection_summary:
        discoveries=engine.find_relevant_discoveries(number_of_concepts=3, input_summary=reflection_summary)
        random_index = random.randint(0, len(discoveries) - 1)
        story, book_name, page_number = engine.find_relevant_story(discovery=discoveries[random_index], input_summary=reflection_summary)
        response={
            'reflection_summary': reflection_summary,
            'discoveries': discoveries,
            'story': story,
            'book_name': book_name,
            'page_number': page_number
        }
        return jsonify(response), 201
    else:
        return jsonify({'error': ' reflection_summary is required'}), 400


    # return jsonify(data), 201


@app.route("/get_reflection/<reflection_summary>")
def get_reflection(reflection_summary):
    print(f'returned reflection: {reflection_summary}')
    return f'reflection: {reflection_summary}'


if __name__=='__main__':
    engine=WisdomEngine()
    app.run(host='0.0.0.0', port=8000)