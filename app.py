from flask import Flask, request, jsonify, render_template
import os
import random
import pymysql

app = Flask(__name__)

# list of cat images
images = [
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRcuqUINWHLTIq9D-GWb9gyGG3AWQmO2HiA3w&s",
    "https://www.pawlovetreats.com/cdn/shop/articles/pembroke-welsh-corgi-puppy_1000x.jpg?v=1628638716",
    "https://hips.hearstapps.com/goodhousekeeping/assets/17/30/pembroke-welsh-corgi.jpg",
    "https://img.freepik.com/free-photo/portrait-cute-boxer-dog_181624-47633.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQlO4erNhFuKmV1TNly5fu8RbSFftERnpUCUg&s",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS0qDKYT9QCq6VnNu4Rlo-rCzD5CDpwt4JCBvIJ5dhI1NpNjyE0tQl740Kf5lUWwe8T6UA&usqp=CAU"
]
@app.route("/")
def index():
    url = random.choice(images)
    return render_template("index.html", url=url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
