import os
import sqlite3
from flask import Flask, render_template, url_for
from database import get_db_connection

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), "..", "output"),
    static_url_path="/static",
)


def query_db(query, args=(), one=False):
    db = get_db_connection()
    if isinstance(db, sqlite3.Connection):
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        data = [dict(row) for row in rows]
    else:
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, args)
        data = cursor.fetchall()
        cursor.close()
        db.close()
    return data[0] if one and data else (data[0] if one else data)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/violations')
def violations():
    data = query_db("SELECT * FROM violations ORDER BY id DESC")
    return render_template('violations.html', violations=data)


@app.route('/dashboard')
def dashboard():
    total = query_db("SELECT COUNT(*) AS total FROM violations", one=True)
    unpaid = query_db("SELECT COUNT(*) AS unpaid FROM violations WHERE status='UNPAID'", one=True)
    return render_template('dashboard.html', total=total, unpaid=unpaid)


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)
