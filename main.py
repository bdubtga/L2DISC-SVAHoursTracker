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

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'valid' not in session:
        return redirect('/login')
    
    user_id = session['user']
    message = ""
    
    if request.method == 'POST':
        if 'update_user' in request.form:
            username = request.form['username']
            cur.execute('UPDATE user SET username = ? WHERE id = ?', (username, user_id))
            con.commit()
            message = "Username updated!"
        
        elif 'update_school' in request.form:
            school_id = request.form['school_id'] or None
            cur.execute('UPDATE user SET school_id = ? WHERE id = ?', (school_id, user_id))
            con.commit()
            message = "School updated!"
        
        elif 'change_password' in request.form:
            if request.form['new_password'] != request.form['confirm_password']:
                return render_template('settings.html', error="Passwords do not match")
            new_password = request.form['new_password']
            cur.execute('UPDATE user SET password = ? WHERE id = ?', (new_password, user_id))
            con.commit()
            message = "Password changed!"
    
    user = cur.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    schools = cur.execute('SELECT * FROM school ORDER BY school').fetchall()
    current_school = None
    if user[3]:
        current_school = cur.execute('SELECT * FROM school WHERE id = ?', (user[3],)).fetchone()
    
    return render_template('settings.html', 
                         user=user, 
                         schools=schools, 
                         current_school=current_school,
                         message=message)

if __name__ == '__main__':
    app.run(port=3000, debug=True)