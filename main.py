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

@app.route('/hours', methods=['GET', 'POST'])
def hours():
    if 'valid' not in session:
        return redirect('/login')
    
    user_id = session['user']
    message = ""
    error = ""
    
    if request.method == 'POST':
        if 'delete_entry' in request.form:
            entry_id = request.form['entry_id']
            entry = cur.execute('SELECT * FROM entry WHERE id = ? AND user = ?', (entry_id, user_id)).fetchone()
            if entry:
                cur.execute('DELETE FROM entry WHERE id = ? AND user = ?', (entry_id, user_id))
                con.commit()
                message = "entry deleted successfully"
            else:
                error = "Entry not found or access denied"
        elif 'update_entry' in request.form and request.form['update_entry']:
            entry_id = request.form['entry_id']
            activity = request.form.get('activity', '').strip()
            description = request.form.get('description', '').strip()
            date_start = request.form.get('start', '')
            date_end = request.form.get('end', '')
            
            # validation
            if not activity or not description or not date_start or not date_end:
                error = "please fill in all fields"
            else:
                try:
                    start_dt = datetime.fromisoformat(date_start.replace('T', ' '))
                    end_dt = datetime.fromisoformat(date_end.replace('T', ' '))
                    now = datetime.now()
                    
                    if end_dt <= start_dt:
                        error = "end time must be after start time"
                    elif start_dt > now:
                        error = "start time cannot be in the future"
                    elif end_dt > now:
                        error = "end time cannot be in the future"
                    elif (end_dt - start_dt).total_seconds() / 3600 > 24:
                        error = "total hours cannot exceed 24 hours"
                    else:
                        entry = cur.execute('SELECT * FROM entry WHERE id = ? AND user = ?', (entry_id, user_id)).fetchone()
                        if entry:
                            cur.execute('''UPDATE entry SET activity = ?, description = ?, date_start = ?, date_end = ? 
                                         WHERE id = ? AND user = ?''', 
                                      (activity, description, date_start, date_end, entry_id, user_id))
                            con.commit()
                            message = "entry updated successfully"
                        else:
                            error = "entry not found or no access"
                except ValueError:
                    error = "invalid date format"
        else:
            activity = request.form.get('activity', '').strip()
            description = request.form.get('description', '').strip()
            date_start = request.form.get('start', '')
            date_end = request.form.get('end', '')
            
            # vaidation
            if not activity or not description or not date_start or not date_end:
                error = "please fill in all fields"
            else:
                try:
                    start_dt = datetime.fromisoformat(date_start.replace('T', ' '))
                    end_dt = datetime.fromisoformat(date_end.replace('T', ' '))
                    now = datetime.now()
                    
                    if end_dt <= start_dt:
                        error = "end time must be after start time"
                    elif start_dt > now:
                        error = "start time cannot be in the future"
                    elif end_dt > now:
                        error = "end time cannot be in the future"
                    elif (end_dt - start_dt).total_seconds() / 3600 > 24:
                        error = "total hours cannot exceed 24 hours"
                    else:
                        cur.execute('''INSERT INTO entry (activity, description, date_start, date_end, user) 
                                     VALUES (?, ?, ?, ?, ?)''', 
                                  (activity, description, date_start, date_end, user_id))
                        con.commit()
                        message = "entry added successfully"
                except ValueError:
                    error = "invalid date format"

    # get existing entries
    raw_entries = cur.execute('''SELECT id, activity, description, date_start, date_end 
                               FROM entry WHERE user = ? 
                               ORDER BY date_start DESC''', (user_id,)).fetchall()
    
    # calculate hours
    entries = []
    total_hours = 0
    
    for entry in raw_entries:
        try:
            start_dt = datetime.fromisoformat(entry[3].replace('T', ' '))
            end_dt = datetime.fromisoformat(entry[4].replace('T', ' '))
            hours = (end_dt - start_dt).total_seconds() / 3600
            total_hours += hours
            
            enhanced_entry = {
                'id': entry[0],
                'activity': entry[1],
                'description': entry[2],
                'date_start': entry[3],
                'date_end': entry[4],
                'hours': round(hours, 1),
                'date_display': start_dt.strftime('%Y-%m-%d'),
                'time_display': f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
            }
            entries.append(enhanced_entry)
        except:
            enhanced_entry = {
                'id': entry[0],
                'activity': entry[1],
                'description': entry[2],
                'date_start': entry[3],
                'date_end': entry[4],
                'hours': 0,
                'date_display': entry[3][:10] if entry[3] else 'Invalid date',
                'time_display': 'Invalid time'
            }
            entries.append(enhanced_entry)
    
    return render_template('hours.html', 
                         entries=entries, 
                         total_hours=round(total_hours, 2),
                         message=message,
                         error=error)

@app.route('/recordofachievement')
def recordofachievement():
    if 'valid' not in session:
        return redirect('/login')
    
    user_id = session['user']
    
    # get entries
    raw_entries = cur.execute('''SELECT id, activity, description, date_start, date_end 
                               FROM entry WHERE user = ? 
                               ORDER BY date_start DESC''', (user_id,)).fetchall()
    
    # calculate hotal hours
    total_hours = 0
    year_breakdown = {}
    
    for entry in raw_entries:
        try:
            start_dt = datetime.fromisoformat(entry[3].replace('T', ' '))
            end_dt = datetime.fromisoformat(entry[4].replace('T', ' '))
            hours = (end_dt - start_dt).total_seconds() / 3600
            total_hours += hours
            
            # year breakdown
            year = start_dt.year
            if year not in year_breakdown:
                year_breakdown[year] = 0
            year_breakdown[year] += hours
        except:
            # ship errrors
            continue
    
    # sort years descending
    sorted_years = sorted(year_breakdown.items(), key=lambda x: x[0], reverse=True)
    
    return render_template('recordofachievement.html', 
                         total_hours=round(total_hours, 2),
                         year_breakdown=sorted_years)

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