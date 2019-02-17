from flask import jsonify, make_response, request, Blueprint
from models import Cart, row2dict, app
import sqlalchemy
from main import db

cartView = Blueprint('cartView', __name__)

@cartView.route("/carts", methods={"GET"})
def get_all_cart():
    cart_list = Cart.query.all()
    return jsonify([row2dict(cart) for cart in cart_list])


@cartView.route("/cart/<cart_id>", methods={"GET"})
def get_cart(cart_id):
    # id is a primary key, so we'll have max 1 result row
    cart = Cart.query.filter_by(id=cart_id).first()
    if cart:
        return jsonify(row2dict(cart))
    else:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this cart id."}), 404)


@cartView.route("/cart/create", methods={"POST"})
def create_cart():
    user_id = request.form.get("user_id")
    product_id = request.form.get("product_id")
    quantity = request.form.get("quantity")
    if user_id is None or product_id is None or quantity is None:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot create new cart. Missing mandatory fields."}), 403)
    new_cart = Cart(user_id=user_id, product_id=product_id, quantity=quantity)

    db.session.add(new_cart)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot add new cart. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


@cartView.route("/cart/update/<cart_id>", methods={"PUT"})
def update_cart(cart_id):
    cart = Cart.query.filter_by(id=cart_id).first()
    if cart is None:
        return make_response(jsonify({"code": 404,
                                      "msg": "Cannot update, cart not found."}), 404)
    user_id_param = request.form.get("user_id_param")
    product_id = request.form.get("product_id")
    quantity = request.form.get("quantity")
    if quantity is None and product_id is None:
        return make_response(jsonify({"code": 403,
                                    "msg": "Cannot update cart. Missing mandatory fields."}), 403)
    elif user_id_param is None:
        return make_response(jsonify({"code": 403,
                               "msg": "Cannot update, can not identify cart."}), 403)
    elif int(user_id_param) != cart.user_id:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot update, this cart does not belong to you."}), 403)
    elif product_id is None:
        cart.quantity = quantity
        try:
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            error = "Cannot update cart. "
            print(app.config.get("DEBUG"))
            if app.config.get("DEBUG"):
                error += str(e)
            return make_response(jsonify({"code": 404, "msg": error}), 404)
        return jsonify({"code": 200, "data": {"id": cart_id, "user_id": cart.user_id, "product_id": cart.product_id, "quantity": quantity}})
    elif quantity is None:
        cart.product_id = product_id
        try:
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            error = "Cannot update cart. "
            print(app.config.get("DEBUG"))
            if app.config.get("DEBUG"):
                error += str(e)
            return make_response(jsonify({"code": 404, "msg": error}), 404)
        return jsonify({"code": 200, "data": {"id": cart_id, "user_id": cart.user_id, "product_id": product_id, "quantity": cart.quantity}})
    else:
        cart.product_id = product_id
        cart.quantity = quantity

    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot update cart. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "data": {"id": cart_id, "user_id": cart.user_id, "product_id": product_id, "quantity": quantity}})


@cartView.route("/cart/delete/<cart_id>", methods={"DELETE"})
def delete_cart(cart_id):
    cart = Cart.query.filter_by(id=cart_id).first()
    if cart is None:
        return make_response(jsonify({"code": 404,
                                      "msg": "Cannot delete, cart not found."}), 404)
    db.session.delete(cart)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot delete cart. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})
