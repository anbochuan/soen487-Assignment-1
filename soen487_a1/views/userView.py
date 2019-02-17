from flask import jsonify, make_response, request, Blueprint
from models import User, row2dict, db
from main import app
import sqlalchemy

userView = Blueprint("userView", __name__)


@userView.route("/users", methods={"GET"})
def get_all_user():
    user_list = User.query.all()
    return jsonify([row2dict(user) for user in user_list])


@userView.route("/user/<user_id>", methods={"GET"})
def get_user(user_id):
    # id is a primary key, so we'll have max 1 result row
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify(row2dict(user))
    else:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this user id."}), 404)


@userView.route("/user/create", methods={"POST"})
def create_user():
    # get the name first, if no name then fail
    name = request.form.get("name")
    password = request.form.get("password")
    if name is None or password is None:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot create new user. Missing mandatory fields."}), 403)
    new_user = User(user_name=name, password=password)

    db.session.add(new_user)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot add new user. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


@userView.route("/user/update/<user_id>", methods={"PUT"})
def update_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return make_response(jsonify({"code": 404,
                                      "msg": "Cannot update, user not found."}), 404)

    name = request.form.get("name")
    password = request.form.get("password")
    if name is None and password is None:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot update user. Missing mandatory fields."}), 403)
    elif name is None:
        user.password = password
        try:
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            error = "Cannot update user. "
            print(app.config.get("DEBUG"))
            if app.config.get("DEBUG"):
                error += str(e)
            return make_response(jsonify({"code": 404, "msg": error}), 404)
        return jsonify({"code": 200, "data": {"id": user_id, "user_name": user.user_name, "password": password}})
    elif password is None:
        user.user_name = name
        try:
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            error = "Cannot update user. "
            print(app.config.get("DEBUG"))
            if app.config.get("DEBUG"):
                error += str(e)
            return make_response(jsonify({"code": 404, "msg": error}), 404)
        return jsonify({"code": 200, "data": {"id": user_id, "user_name": name, "password": user.password}})
    else:
        user.user_name = name
        user.password = password
        try:
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            error = "Cannot update user. "
            print(app.config.get("DEBUG"))
            if app.config.get("DEBUG"):
                error += str(e)
            return make_response(jsonify({"code": 404, "msg": error}), 404)
        return jsonify({"code": 200, "data": {"id": user_id, "user_name": name, "password": password}})


@userView.route("/user/delete/<user_id>", methods={"DELETE"})
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return make_response(jsonify({"code": 404,
                                      "msg": "Cannot delete, user not found."}), 404)
    db.session.delete(user)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot delete user. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})
