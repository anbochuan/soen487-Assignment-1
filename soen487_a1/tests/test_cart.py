import unittest
import json
from main import app as tested_app
from main import db as tested_db
from config import TestConfig
from models import Cart

tested_app.config.from_object(TestConfig)


class TestCart(unittest.TestCase):
    def setUp(self):
        # set up the test DB
        self.db = tested_db
        self.db.create_all()
        self.db.session.add(Cart(id=1, user_id=1, product_id=1, quantity=100))
        self.db.session.add(Cart(id=2, user_id=2, product_id=2, quantity=200))
        self.db.session.commit()

        self.app = tested_app.test_client()

    def tearDown(self):
        # clean up the DB after the tests
        Cart.query.delete()
        self.db.session.commit()

    def test_get_all_cart(self):
        # send the request and check the response status code
        response = self.app.get("/carts")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        cart_list = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(cart_list), list)
        self.assertDictEqual(cart_list[0], {"id": "1", "user_id": "1", "product_id": "1", "quantity": "100"})
        self.assertDictEqual(cart_list[1], {"id": "2", "user_id": "2", "product_id": "2", "quantity": "200"})

    def test_get_cart_with_valid_id(self):
        # send the request and check the response status code
        response = self.app.get("/cart/1")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        cart = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(cart, {"id": "1", "user_id": "1", "product_id": "1", "quantity": "100"})

    def test_get_cart_with_invalid_id(self):
        # send the request and check the response status code
        response = self.app.get("/cart/1000000")
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot find this cart id."})

    def test_create_cart_without_param(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.post("/cart/create", data={"user_id": None, "product_id": None, "quantity": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new cart. Missing mandatory fields."})

        # check DB unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_create_cart_with_param(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.post("/cart/create", data={"id": 3, "user_id": 3, "product_id": 3, "quantity": 300})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})

        # check if the DB was added correctly
        cart = Cart.query.filter_by(id=3).first()
        self.assertEqual(cart.user_id, 3)
        self.assertEqual(cart.product_id, 3)
        self.assertEqual(cart.quantity, 300)
        # check if the DB was added correctly
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count+1)

    def test_create_cart_with_only_user_id(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.post("/cart/create", data={"id": 3, "user_id": 3, "product_id": None, "quantity": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new cart. Missing mandatory fields."})

        # check if the DB was unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_create_cart_with_only_product_id(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.post("/cart/create", data={"id": 3, "user_id": None, "product_id": 3, "quantity": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new cart. Missing mandatory fields."})

        # check if the DB was unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_create_cart_with_only_quantity(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.post("/cart/create", data={"id": 3, "user_id": None, "product_id": None, "quantity": 300})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new cart. Missing mandatory fields."})

        # check if the DB was unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_create_cart_without_quantity(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.post("/cart/create", data={"id": 3, "user_id": 3, "product_id": 3, "quantity": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new cart. Missing mandatory fields."})

        # check if the DB was unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_create_cart_without_user_id(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.post("/cart/create", data={"id": 3, "user_id": None, "product_id": 3, "quantity": 300})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new cart. Missing mandatory fields."})

        # check if the DB was unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_create_cart_without_product_id(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.post("/cart/create", data={"id": 3, "user_id": 3, "product_id": None, "quantity": 300})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new cart. Missing mandatory fields."})

        # check if the DB was unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_cart_with_bad_id(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.put("/cart/update/1000", data={"user_id_param": 3, "product_id": 3, "quantity": 800})
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot update, cart not found."})

        # check DB unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_cart_without_param(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.put("/cart/update/1", data={"user_id_param": None, "product_id": None, "quantity": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot update cart. Missing mandatory fields."})

        # check DB unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_cart_with_param(self):
        # send the request and check the response status code
        response = self.app.put("/cart/update/1", data={"user_id_param": 1, "product_id": 3, "quantity": 800})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        updated_cart = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(updated_cart), dict)
        self.assertDictEqual(updated_cart, {"code": 200, "data": {"id": "1", "user_id": 1, "product_id": "3", "quantity": "800"}})

        # check DB changed result
        check_cart = Cart.query.filter_by(id=1).first()
        self.assertEqual(check_cart.user_id, 1)
        self.assertEqual(check_cart.product_id, 3)
        self.assertEqual(check_cart.quantity, 800)

    def test_update_cart_without_user_id(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.put("/cart/update/1", data={"user_id_param": None, "product_id": 3, "quantity": 500})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot update, can not identify cart."})

        # check DB unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_cart_with_bad_user_id(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.put("/cart/update/1", data={"user_id_param": 3, "product_id": 3, "quantity": 500})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot update, this cart does not belong to you."})

        # check DB unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_cart_with_only_product_id(self):
        # send the request and check the response status code
        response = self.app.put("/cart/update/1", data={"user_id_param": 1, "product_id": 3, "quantity": None})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        updated_cart = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(updated_cart), dict)
        self.assertDictEqual(updated_cart, {"code": 200, "data": {"id": "1", "user_id": 1, "product_id": "3", "quantity": 100}})

        # check DB changed result
        check_cart = Cart.query.filter_by(id=1).first()
        self.assertEqual(check_cart.user_id, 1)
        self.assertEqual(check_cart.product_id, 3)
        self.assertEqual(check_cart.quantity, 100)

    def test_update_cart_with_only_quantity(self):
        # send the request and check the response status code
        response = self.app.put("/cart/update/1", data={"user_id_param": 1, "product_id": None, "quantity": 900})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        updated_cart = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(updated_cart), dict)
        self.assertDictEqual(updated_cart, {"code": 200, "data": {"id": "1", "user_id": 1, "product_id": 1, "quantity": "900"}})

        # check DB changed result
        check_cart = Cart.query.filter_by(id=1).first()
        self.assertEqual(check_cart.user_id, 1)
        self.assertEqual(check_cart.product_id, 1)
        self.assertEqual(check_cart.quantity, 900)

    def test_delete_cart_with_bad_id(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.delete("/cart/delete/1000")
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot delete, cart not found."})

        # check DB unchanged
        added_count = Cart.query.count()
        self.assertEqual(added_count, initial_count)

    def test_delete_cart_with_id(self):
        initial_count = Cart.query.count()

        # send the request and check the response status code
        response = self.app.delete("/cart/delete/1")
        self.assertEqual(response.status_code, 200)

        # check DB changed
        deleted_count = Cart.query.count()
        self.assertEqual(deleted_count, initial_count-1)
