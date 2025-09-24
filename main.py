from flask import *
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# authentication
@app.route('/login')
def login():
    return render_template('login.html')

# main app routes
@app.route('/')
def portal():
    return render_template('portal.html')
@app.route('/hours')
def hours():
    return render_template('hours.html')
@app.route('/recordofachievement')
def recordofachievement():
    return render_template('recordofachievement.html')
@app.route('/settings')
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)