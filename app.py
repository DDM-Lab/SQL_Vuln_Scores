from flask import Flask, request, render_template, g, redirect, url_for, session, send_file
import sqlite3
import os
import sys
import random  
from flask_bootstrap import Bootstrap5
from datetime import datetime
import argparse
from io import StringIO, BytesIO
import logging
import json

seed = os.environ.get("SEED")

# Add at the start of your file, after the other imports
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open("/challenge/metadata.json", "r") as f:
    metadata_flag = json.load(f)
FLAG = metadata_flag['flag']

DEFAULT_CONDITION = 0

app = Flask(__name__)
app.secret_key = str(seed) # Needed if you use session
bootstrap = Bootstrap5(app)  # Initialize Bootstrap

# Parse command line arguments
parser = argparse.ArgumentParser(description='SQL Injection Challenge Application')
parser.add_argument('--treatment', action='store_true', help='Enable treatment condition')
args = parser.parse_args()

if '--treatment' in sys.argv:
    condition = 1
elif os.environ.get('TREATMENT', '').lower() in ('true', '1', 'yes'):
    condition = 1
else:
    condition = DEFAULT_CONDITION
    
# Database directory
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)


def format_qualtrics_data(qualtrics_data):
    """Format just the data portion of the qualtrics display"""
    data_str = "--- Study Data ---\n"
    for key, value in qualtrics_data.items():
        data_str += f"{key}: {value}\n"
    return data_str

def generate_qualtrics_data(problem):
    return {
        'condition': condition,
        "problem": problem
    }

# Database initialization
def init_dbs():
    # Main database for Challenge 1
    conn = sqlite3.connect(os.path.join(DB_DIR, 'main.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS flags
                 (id INTEGER PRIMARY KEY, flag TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'very_secret_IT_pass1234')")
    c.execute(f"INSERT OR IGNORE INTO flags VALUES (1, '{FLAG}')")
    conn.commit()
    conn.close()

    # Inventory database for Challenge 2
    conn = sqlite3.connect(os.path.join(DB_DIR, 'inventory.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY, 
                  item_name TEXT, 
                  quantity INTEGER,
                  category TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS hidden_flags
                 (id INTEGER PRIMARY KEY, flag TEXT)''')
    c.execute("INSERT OR IGNORE INTO inventory VALUES (1, 'USB Cable', 50, 'Electronics')")
    c.execute(f"INSERT OR IGNORE INTO hidden_flags VALUES (1, '{FLAG}')")
    conn.commit()
    conn.close()

    # Challenge 4 database initialization
    conn = sqlite3.connect(os.path.join(DB_DIR, 'login.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY, 
                     username TEXT, 
                     password TEXT)''')
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'the_best_mailserver_pass')")
    c.execute('''CREATE TABLE IF NOT EXISTS flags (
                     id INTEGER PRIMARY KEY, 
                     flag TEXT)''')
    c.execute(f"INSERT OR IGNORE INTO flags VALUES (1, '{FLAG}')")
    conn.commit()
    conn.close()

    # Library database for Challenge 3
    conn = sqlite3.connect(os.path.join(DB_DIR, 'library.db'))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books 
                 (id INTEGER PRIMARY KEY, title TEXT, author TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS library_secrets
                 (id INTEGER PRIMARY KEY, secret_code TEXT)''')
    c.execute("INSERT OR IGNORE INTO books VALUES (1, 'The Great Gatsby', 'F. Scott Fitzgerald')")
    c.execute(f"INSERT OR IGNORE INTO library_secrets VALUES (1, '{FLAG}')")
    conn.commit()
    conn.close()

    qualtrics_data = {
            'condition': condition
        }

init_dbs()

# Database helpers
def get_db(name):
    db = getattr(g, f'_{name}', None)
    if db is None:
        db = sqlite3.connect(os.path.join(DB_DIR, f'{name}.db'))
        setattr(g, f'_{name}', db)
    return db

@app.teardown_appcontext
def close_connection(exception):
    for db_name in ['main', 'inventory', 'library', 'login']:
        db = getattr(g, f'_{db_name}', None)
        if db is not None:
            db.close()

@app.route('/')
def index():  
    # Hard-coded "challenges" (vulnerabilities) with CVSS & severity
    # severity can be a short label like "High", "Medium", "Low"
    challenges = [
        {
            "id": 1,
            "endpoint": "/challenge1",
            "name": "IT Department Endpoint",
            "description": "Could we use the UNION operator?",
            "cvss": round(random.uniform(6,7.99), 1),
            "severity": "High"
        },
        {
            "id": 2,
            "endpoint": "/challenge2",
            "name": "Inventory DB",
            "description": "I wonder what happens if multiple columns are matched with the UNION operator...",
            "cvss": round(random.uniform(8,10), 1),
            "severity": "Very High"
        },
        {
            "id": 3,
            "endpoint": "/challenge3",
            "name": "Library Endpoint",
            "description": "WHERE could we possibly use this?",
            "cvss": round(random.uniform(2,3.99), 1),
            "severity": "Low"
        },
        {
            "id": 4,
            "endpoint": "/challenge4",
            "name": "Mailserver Endpoint",
            "description": "If you forgot your password, could they tell you what it is?",
            "cvss":  round(random.uniform(4,5.99), 1),
            "severity": "Medium"
        }
    ]
    if condition != 1:
        random.shuffle(challenges)
    else:
        challenges = sorted(challenges, key=lambda x: x['cvss'], reverse=True)

    session['challenges'] = challenges

    # Optional: store condition in session if you want to keep it for the user
    session['condition'] = condition

    # This text acts as a placeholder for "world building" or narrative.
    story_intro = (
        "Welcome to MegaCorp's Security Operations Challenge (CTF)!\n"
        "In this scenario, you've been brought in to demonstrate the "
        "exploitation of potential vulnerabilities. Pick a vulnerability "
        "and attempt to exploit it."
    )

    return render_template('index.html',
                           condition=condition,
                           challenges=challenges,
                           story_intro=story_intro)

@app.route('/select/<int:challenge_id>', methods=['POST'])
def select_challenge(challenge_id):
    """
    Logs the participant's selection to the DB with 
    participant_id (for demonstration, use a random or session-based ID),
    and condition.
    """
    # In a real scenario, you'd have an actual participant ID
    participant_id = request.remote_addr  # e.g. just IP for demonstration

    # Find the chosen vulnerability name (in a real scenario, store them in DB)
    vulnerabilities = {
        1: "Basic UNION-based Injection",  
        2: "Multi-Column UNION Injection",
        3: "UNION Injection with WHERE clause",
        4: "Login Form SQL Injection"
    }
    chosen_vuln = vulnerabilities.get(challenge_id, "Unknown")

    # Insert selection into main.db -> selections table
    conn = sqlite3.connect(os.path.join(DB_DIR, 'main.db'))
    c = conn.cursor()
    c.execute('''
        INSERT INTO selections (participant_id, condition, vulnerability_name, chosen_at)
        VALUES (?, ?, ?, ?)
    ''', (participant_id, condition, chosen_vuln, datetime.now()))
    conn.commit()
    conn.close()

    # Redirect user to the chosen challenge or somewhere else
    return redirect(url_for(f'challenge{challenge_id}'))

@app.route('/download_qualtrics')
def download_qualtrics():
    # Get the problem identifier from the query string; default to "unknown problem" if not provided.
    problem = request.args.get("problem", "unknown problem")
    qualtrics_data = generate_qualtrics_data(problem)
    
    # Format the data as a string.
    output_text = "Upload this file to Qualtrics to get compensation for this challenge.\n"
    output_text += "--- Study Data ---\n"
    for key, value in qualtrics_data.items():
        output_text += f"{key}: {value}\n"
    
    # Use BytesIO to create an in-memory binary file-like object.
    file_obj = BytesIO()
    file_obj.write(output_text.encode('utf-8'))
    file_obj.seek(0)  # Reset pointer to the beginning
    
    # Send the file as an attachment using the new keyword 'download_name'
    return send_file(
        file_obj,
        as_attachment=True,
        download_name="sql_challenge.txt",
        mimetype="text/plain"
    )


# Challenge 1: Basic UNION-based Injection
# IT Department Endpoint
@app.route('/challenge1', methods=['GET', 'POST'])
def challenge1():
    result = None
    qualtrics_data = None
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            query = f"SELECT username FROM users WHERE username = '{username}'"
            logger.info(f"Query: {query}")
            db = get_db('main')
            cur = db.execute(query)
            result = cur.fetchall()
            logger.info(f"Result: {result}")
        except sqlite3.Error as e:
            logger.info(f"Error: {str(e)}")
            result = [f"Error: {str(e)}"]
        if any('picoCTF' in str(row) for row in result):
            qualtrics_data = format_qualtrics_data(generate_qualtrics_data("problem 1"))
    return render_template('challenge1.html', result=result, qualtrics_data=qualtrics_data)

# Challenge 2: Multi-Column UNION Injection
# Inventory DB
@app.route('/challenge2', methods=['GET', 'POST'])
def challenge2():
    result = None
    qualtrics_data = None
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        query = f"SELECT item_name, quantity, category FROM inventory WHERE id = '{product_id}'"
        logger.info(f"Query: {query}")
        db = get_db('inventory')
        try:
            cur = db.execute(query)
            result = cur.fetchall()
            logger.info(f"Result: {result}")
            # Check if any row in the result contains 'picoCTF'
            if any('picoCTF' in str(row) for row in result):
                qualtrics_data = format_qualtrics_data(generate_qualtrics_data("problem 2"))
        except sqlite3.Error as e:
            logger.info(f"Error: {str(e)}")
            result = [f"Error: {str(e)}"]
    return render_template('challenge2.html', result=result, qualtrics_data=qualtrics_data)

# Challenge 3: UNION Injection with WHERE clause
# Logs Endpoint
@app.route('/challenge3', methods=['GET', 'POST'])
def challenge3():
    result = None
    qualtrics_data = None
    if request.method == 'POST':
        author = request.form.get('author', '')
        query = f"SELECT title, author FROM books WHERE author = '{author}'"
        db = get_db('library')
        try:
            cur = db.execute(query)
            result = cur.fetchall()
            logger.info(f"Result: {result}")
        except sqlite3.Error as e:
            result = [f"Error: {str(e)}"]
        if any('picoCTF' in str(row) for row in result):
            qualtrics_data = format_qualtrics_data(generate_qualtrics_data("problem 3"))
    return render_template('challenge3.html', result=result, qualtrics_data=qualtrics_data)

# Challenge 4: Login Form
# Mailserver Endpoint
@app.route('/challenge4', methods=['GET', 'POST'])
def challenge4():
    message = ''
    message_class = ''
    qualtrics_data = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Use prepared SQL statements for secure login
        query = "SELECT username FROM users WHERE username = ? AND password = ?"
        db = get_db('login')
        cur = db.execute(query, (username, password))
        result = cur.fetchone()

        if result:
            # Fetch the flag upon successful login
            flag_query = "SELECT flag FROM flags WHERE id = 1"
            cur = db.execute(flag_query)
            flag_result = cur.fetchone()
            if 'picoCTF' in flag_result:
                qualtrics_data = format_qualtrics_data(generate_qualtrics_data("problem 4"))
            return render_template('challenge4_success.html', flag=flag_result[0], qualtrics_data=qualtrics_data)
        else:
            message = "Invalid credentials"
            message_class = "danger"

    return render_template('challenge4.html', message=message, message_class=message_class, qualtrics_data=qualtrics_data)

@app.route('/challenge4/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    message = ''
    message_class = ''
    
    if request.method == 'POST':
        username = request.form.get('username')
        
        # Vulnerable to SQL injection
        query = f"SELECT username FROM users WHERE username = '{username}'"
        db = get_db('login')
        try:
            cur = db.execute(query)
            result = cur.fetchone()
            
            if result:
                message = f"Password reset link sent to user: {result[0]}"
                message_class = "success"
                
            else:
                message = "User not found"
                message_class = "danger"
        except sqlite3.Error as e:
            message = f"Error: {str(e)}"
            message_class = "danger"

    return render_template('forgot_password.html', message=message, message_class=message_class, qualtrics_data=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)