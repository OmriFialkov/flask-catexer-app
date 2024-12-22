from flask import Flask, request, jsonify, render_template
import os
import random
import pymysql

app = Flask(__name__)

# Connect to the MySQL database with pymysql
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
    # connect to db
    connection = get_db_connection()
    cursor = connection.cursor()
    
    #_____________________________________________________________________________________________

    # increment counter by one, +1
    cursor.execute("UPDATE visitor_counter SET count = count + 1 where id = 1")
    connection.commit()

    # fetch updated count from db to variable.
    cursor.execute("SELECT count FROM visitor_counter WHERE id = 1")
    visitor_count = cursor.fetchone()[0] # fetches last query one row as tuple, [0] accessing only element.

    # docker compose down -v - will restart the counter, but without -v - volume will keep counter.
    #_____________________________________________________________________________________________

    # Fetch image URLs from the database
    cursor.execute("SELECT image_url FROM images")
    result = cursor.fetchall()
    #print(result)
    connection.close()

    # Transform the result into a list of URLs
    images = [row[0] for row in result]
    
    # Pick a random image from the list
    url = random.choice(images)
    return render_template("index.html", url=url, visitor_count=visitor_count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000))) # if port env var is blank port will be 5000.
