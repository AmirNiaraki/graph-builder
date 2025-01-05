'''
nohup gunicorn -w 5 -b 0.0.0.0:8000 flask_app:app &
'''

from flask import Flask
import time


app=Flask(__name__)


@app.route('/name')
def get_name():
    print('returned name')
    return 'philo api'


@app.route('/version')
def get_version():
    print('returned version')
    return '1.0.0'

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000)