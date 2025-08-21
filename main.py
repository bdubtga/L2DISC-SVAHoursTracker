from flask import *
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# SQLite connection per request to avoid cross-thread usage errors
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('Database.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(app.root_path, 'templates/js'), filename)
@app.route('/img/<path:filename>')
def serve_img(filename):
    return send_from_directory(os.path.join(app.root_path, 'templates/img'), filename)
@app.route('/404')
def not_found():
    return render_template('404.html')


@app.route('/')
def portal():
    return render_template('portal.html')
@app.route('/settings')
def settings():
    return render_template('settings.html')
@app.route('/hours')
def hours():
    return render_template('hours.html')
@app.route('/edit')
def edit():
    return render_template('edit.html')

@app.route('/NewEntry', methods=['POST'])
def new_entry():
    activity = request.form.get('activity')
    start = request.form.get('start')
    end = request.form.get('end')
    description = request.form.get('description')
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO entry (activity, start, end, description) VALUES (?, ?, ?, ?)",
        (activity, start, end, description),
    )
    db.commit()
    # Redirect back to the page the user came from (PRG pattern), fallback to hours page
    return redirect(request.referrer or url_for('hours'), code=303)



@app.route('/entries')
def list_entries():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT activity, start, end, description FROM entry")
    entries = []
    for row in cur.fetchall():
        start_dt = datetime.strptime(row['start'], '%Y-%m-%dT%H:%M')
        end_dt = datetime.strptime(row['end'], '%Y-%m-%dT%H:%M')
        hours_diff = (end_dt - start_dt).total_seconds() / 3600.0
        entries.append({
            'activity': row['activity'],
            'date': start_dt.strftime('%Y-%m-%d'),
            'hours': str(round(hours_diff, 2)),
            'description': row['description'],
        })
    return jsonify(entries)

if __name__ == '__main__':
    app.run(debug=True)