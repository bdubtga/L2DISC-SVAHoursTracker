from flask import *
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def portal():
    return render_template('portal.html')

if __name__ == '__main__':
    app.run(debug=True)