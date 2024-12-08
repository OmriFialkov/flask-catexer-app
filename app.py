from flask import Flask, request, jsonify, render_template
import os
import random
import pymysql

app = Flask(__name__)

# Connect to the MySQL database
def get_db_connection():
    connection = pymysql.connect(
        host =os.getenv("MYSQL_HOST"),  # Host matches the service name of the database in docker-compose
        user=os.getenv("MYSQL_USER"),  # MySQL user from docker-compose
        password=os.getenv("MYSQL_PASSWORD"),  # MySQL password from docker-compose
        database=os.getenv("MYSQL_DATABASE")  # Database name from init.sql
    )
    return connection

@app.route("/")
def index():
    # Fetch image URLs from the database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT image_url FROM images")
    result = cursor.fetchall()
    connection.close()

    # Transform the result into a list of URLs
    images = [row[0] for row in result]
    
    # Pick a random image from the list
    url = random.choice(images)
    return render_template("index.html", url=url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
