from flask import *
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# db connection
con = sqlite3.connect('db.db', check_same_thread=False)
cur = con.cursor()


# authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if form submitted
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = cur.execute('SELECT * FROM user WHERE username = ? AND password = ?', (username, password)).fetchone()
        
        if user:
            return redirect('/')
        else:
            return render_template('login.html', error='wrong username or password')
    
    # normal request
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