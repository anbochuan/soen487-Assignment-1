from flask import jsonify, make_response, request, Blueprint
from models import Product, row2dict, db
import sqlalchemy
from main import app

productView = Blueprint('productView', __name__)


@productView.route("/products", methods={"GET"})
def get_all_product():
    product_list = Product.query.all()
    return jsonify([row2dict(product) for product in product_list])


@productView.route("/product/<product_id>", methods={"GET"})
def get_product(product_id):
    # id is a primary key, so we'll have max 1 result row
    product = Product.query.filter_by(id=product_id).first()
    if product:
        return jsonify(row2dict(product))
    else:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this product id."}), 404)


@productView.route("/product/create", methods={"POST"})
def create_product():
    name = request.form.get("name")
    price = request.form.get("price")
    if name is None or price is None:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot create new product. Missing mandatory fields."}), 403)
    new_product = Product(product_name=name, product_price=price)

    db.session.add(new_product)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot add new product. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})


@productView.route("/product/update/<product_id>", methods={"PUT"})
def update_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return make_response(jsonify({"code": 404,
                                      "msg": "Cannot update, product not found."}), 404)
    name = request.form.get("name")
    price = request.form.get("price")
    if name is None and price is None:
        return make_response(jsonify({"code": 403,
                                      "msg": "Cannot update product. Missing mandatory fields."}), 403)
    elif name is None:
        product.product_price = price
        try:
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            error = "Cannot update product. "
            print(app.config.get("DEBUG"))
            if app.config.get("DEBUG"):
                error += str(e)
            return make_response(jsonify({"code": 404, "msg": error}), 404)
        return jsonify({"code": 200, "data": {"id": product_id, "product_name": product.product_name, "product_price": price}})
    elif price is None:
        product.product_name = name
        try:
            db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            error = "Cannot update product. "
            print(app.config.get("DEBUG"))
            if app.config.get("DEBUG"):
                error += str(e)
            return make_response(jsonify({"code": 404, "msg": error}), 404)
        return jsonify({"code": 200, "data": {"id": product_id, "product_name": name, "product_price": product.product_price}})
    else:
        product.product_name = name
        product.product_price = price

    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot update product. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "data": {"id": product_id, "product_name": name, "product_price": price}})


@productView.route("/product/delete/<product_id>", methods={"DELETE"})
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product is None:
        return make_response(jsonify({"code": 404,
                                      "msg": "Cannot delete, product not found."}), 404)
    db.session.delete(product)
    try:
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        error = "Cannot delete product. "
        print(app.config.get("DEBUG"))
        if app.config.get("DEBUG"):
            error += str(e)
        return make_response(jsonify({"code": 404, "msg": error}), 404)
    return jsonify({"code": 200, "msg": "success"})

