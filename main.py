from flask import *
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sdfcvy79t80wrfyrcvwn80h7wercv'

# db connection
con = sqlite3.connect('db.db', check_same_thread=False)
cur = con.cursor()


# authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('user', None)
    session.pop('valid', None)
    
    # if form submitted
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = cur.execute('SELECT * FROM user WHERE username = ? AND password = ?', (username, password)).fetchone()
        
        if user: 
            session['user'] = user[0]
            session['valid'] = True
            return redirect('/')
        else:
            return render_template('login.html', error='wrong username or password')
    
    # normal request
    return render_template('login.html')


# main app routes
@app.route('/')
def portal():
    if 'valid' not in session:
        return redirect('/login')
    return render_template('portal.html')

@app.route('/hours')
def hours():
    if 'valid' not in session:
        return redirect('/login')
    return render_template('hours.html')

@app.route('/recordofachievement')
def recordofachievement():
    if 'valid' not in session:
        return redirect('/login')
    return render_template('recordofachievement.html')

@app.route('/settings')
def settings():
    if 'valid' not in session:
        return redirect('/login')
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)