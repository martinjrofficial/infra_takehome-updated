from flask import Flask
import requests
import json
import sqlite3
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    conn = sqlite3.connect('birds.db')
    return conn

@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/')
def hello():
    return "Add a 2 letter state param to learn about birds and the weather challenges they face.", 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/<state>')
def bird(state):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM birds WHERE abbreviation = ?", (state,))
        bird_data = cursor.fetchall()
        bird_json = json.dumps([dict(row) for row in bird_data])
        cursor.close()
        conn.close()

        weather_url = f'https://api.weather.gov/alerts/active?area={state}'
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        result = [bird_json, weather_data]
        return json.dumps(result), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        logger.exception("An error occurred")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)