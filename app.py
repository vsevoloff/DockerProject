# app.py
from flask import Flask, request, redirect, url_for, render_template_string
import psycopg2
from psycopg2 import OperationalError
import time
import logging

app = Flask(__name__)

# Database connection details
DB_NAME = "mydb"
DB_USER = "user"
DB_PASS = "password"
DB_HOST = "db"
DB_PORT = "5432"

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_connection():
    retry_count = 5
    while retry_count > 0:
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                host=DB_HOST,
                port=DB_PORT
            )
            return conn
        except OperationalError as e:
            logging.warning(f"Database connection failed: {e}")
            retry_count -= 1
            time.sleep(2)
    logging.error("Failed to connect to the database after multiple attempts")
    return None

def create_table():
    conn = create_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS entries (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL
                    );
                """)
                conn.commit()
                logging.info("Table 'entries' created successfully or already exists.")
        except Exception as e:
            logging.error(f"Error creating table: {e}")
        finally:
            conn.close()
    else:
        logging.error("Connection to database failed, cannot create table.")

create_table()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = create_connection()
    if not conn:
        return "Error: Unable to connect to the database", 500

    if request.method == "POST":
        content = request.form["content"]
        with conn.cursor() as cur:
            cur.execute("INSERT INTO entries (content) VALUES (%s)", (content,))
            conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM entries")
        entries = cur.fetchall()
    
    conn.close()

    html = """
    <!doctype html>
    <title>Flask PostgreSQL App</title>
    <h1>Enter data</h1>
    <form method=post>
      <input type=text name=content>
      <input type=submit value=Submit>
    </form>
    <h2>Entries</h2>
    <ul>
      {% for entry in entries %}
        <li>{{ entry[1] }}</li>
      {% endfor %}
    </ul>
    """
    return render_template_string(html, entries=entries)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)