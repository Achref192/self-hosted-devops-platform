import os
import time
import psycopg
from flask import Flask, jsonify
from psycopg.rows import dict_row
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "devopsdb"),
        user=os.getenv("DB_USER", "devops"),
        password=os.getenv("DB_PASSWORD", ""),
        connect_timeout=3,
        row_factory=dict_row,
    )

def initialize_database():
    for attempt in range(10):
        try:
            with get_connection() as connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS visits (
                        id SERIAL PRIMARY KEY,
                        visited_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                """)
            return
        except psycopg.OperationalError:
            if attempt == 9:
                raise
            time.sleep(2)

@app.get("/")
def home():
    return jsonify({
        "message": "Self-Hosted DevOps Platform",
        "status": "running"
    })

@app.get("/health")
def health():
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1")
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except psycopg.Error:
        return jsonify({"status": "unhealthy", "database": "unavailable"}), 503

@app.get("/visits")
def visits():
    with get_connection() as connection:
        row = connection.execute("""
            INSERT INTO visits DEFAULT VALUES
            RETURNING id, visited_at
        """).fetchone()
    return jsonify(row), 201

if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000)
