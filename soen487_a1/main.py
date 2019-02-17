from flask import Flask, jsonify, make_response
from config import DevConfig

# need an app before we import models because models need it
app = Flask(__name__)

from models import db

db.create_all()

from views.userView import userView
app.register_blueprint(userView)

from views.productView import productView
app.register_blueprint(productView)

from views.cartView import cartView
app.register_blueprint(cartView)




@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({"code": 404, "msg": "404: Not Found"}), 404)

@app.route('/')
def soen487_a1():
    return jsonify({"title": "SOEN487 Assignment 1",
                    "student": {"id": "Your id#", "name": "Your name"}})


if __name__ == '__main__':
    app.run()
