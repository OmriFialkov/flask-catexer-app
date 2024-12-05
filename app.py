from flask import Flask, render_template
import os
import random

app = Flask(__name__)

# list of cat images
images = [
    "https://www.pawlovetreats.com/cdn/shop/articles/pembroke-welsh-corgi-puppy_2000x.jpg?v=1628638716"
]


@app.route("/")
def index():
    url = random.choice(images)
    return render_template("index.html", url=url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
