import unittest
import json
from main import app as tested_app
from main import db as tested_db
from config import TestConfig
from models import Product

tested_app.config.from_object(TestConfig)


class TestProduct(unittest.TestCase):
    def setUp(self):
        # set up the test DB
        self.db = tested_db
        self.db.create_all()
        self.db.session.add(Product(id=1, product_name="iPad", product_price=1399))
        self.db.session.add(Product(id=2, product_name="iPhone XS", product_price=1899))
        self.db.session.commit()

        self.app = tested_app.test_client()

    def tearDown(self):
        # clean up the DB after the tests
        Product.query.delete()
        self.db.session.commit()

    def test_get_all_product(self):
        # send the request and check the response status code
        response = self.app.get("/products")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        product_list = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(product_list), list)
        self.assertDictEqual(product_list[0], {"id": "1", "product_name": "iPad", "product_price": "1399"})
        self.assertDictEqual(product_list[1], {"id": "2", "product_name": "iPhone XS", "product_price": "1899"})

    def test_get_product_with_valid_id(self):
        # send the request and check the response status code
        response = self.app.get("/product/1")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        product = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(product, {"id": "1", "product_name": "iPad", "product_price": "1399"})

    def test_get_product_with_invalid_id(self):
        # send the request and check the response status code
        response = self.app.get("/product/1000000")
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot find this product id."})

    def test_create_product_without_param(self):
        initial_count = Product.query.count()

        # send the request and check the response status code
        response = self.app.post("/product/create", data={"name": None, "price": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new product. Missing mandatory fields."})

        # check DB unchanged
        added_count = Product.query.count()
        self.assertEqual(added_count, initial_count)

    def test_create_product_with_param(self):
        initial_count = Product.query.count()

        # send the request and check the response status code
        response = self.app.post("/product/create", data={"id": 3, "name": "Macbook pro", "price": 2899})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})

        # check if the DB was added correctly
        product = Product.query.filter_by(id=3).first()
        self.assertEqual(product.product_name, "Macbook pro")
        self.assertEqual(product.product_price, 2899)
        # check if the DB was added correctly
        added_count = Product.query.count()
        self.assertEqual(added_count, initial_count+1)

    def test_create_product_with_only_name(self):
        initial_count = Product.query.count()

        # send the request and check the response status code
        response = self.app.post("/product/create", data={"id": 3, "name": "Macbook pro", "price": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new product. Missing mandatory fields."})

        # check if the DB was unchanged
        added_count = Product.query.count()
        self.assertEqual(added_count, initial_count)

    def test_create_product_with_only_price(self):
        initial_count = Product.query.count()

        # send the request and check the response status code
        response = self.app.post("/product/create", data={"id": 3, "name": None, "price": 2899})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new product. Missing mandatory fields."})

        # check if the DB was unchanged
        added_count = Product.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_product_with_bad_id(self):
        initial_count = Product.query.count()

        # send the request and check the response status code
        response = self.app.put("/product/update/1000", data={"name": "Air pod", "price": 259})
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot update, product not found."})

        # check DB unchanged
        added_count = Product.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_product_without_param(self):
        initial_count = Product.query.count()

        # send the request and check the response status code
        response = self.app.put("/product/update/1", data={"name": None, "price": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot update product. Missing mandatory fields."})

        # check DB unchanged
        added_count = Product.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_product_with_param(self):
        # send the request and check the response status code
        response = self.app.put("/product/update/1", data={"name": "Air pod", "price": 259})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        updated_product = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(updated_product), dict)
        self.assertDictEqual(updated_product, {"code": 200, "data": {"id": "1", "product_name": "Air pod", "product_price": "259"}})

        # check DB changed result
        check_product = Product.query.filter_by(id=1).first()
        self.assertEqual(check_product.product_name, "Air pod")
        self.assertEqual(check_product.product_price, 259)

    def test_update_product_with_only_name(self):
        # send the request and check the response status code
        response = self.app.put("/product/update/1", data={"name": "iPad pro", "price": None})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        updated_product = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(updated_product), dict)
        self.assertDictEqual(updated_product, {"code": 200, "data": {"id": "1", "product_name": "iPad pro", "product_price": 1399}})

        # check DB changed result
        check_product = Product.query.filter_by(id=1).first()
        self.assertEqual(check_product.product_name, "iPad pro")
        self.assertEqual(check_product.product_price, 1399)

    def test_update_product_with_only_price(self):
        # send the request and check the response status code
        response = self.app.put("/product/update/1", data={"name": None, "price": 1599})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        updated_product = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(updated_product), dict)
        self.assertDictEqual(updated_product, {"code": 200, "data": {"id": "1", "product_name": "iPad", "product_price": "1599"}})

        # check DB changed result
        check_product = Product.query.filter_by(id=1).first()
        self.assertEqual(check_product.product_name, "iPad")
        self.assertEqual(check_product.product_price, 1599)

    def test_delete_product_with_bad_id(self):
        initial_count = Product.query.count()

        # send the request and check the response status code
        response = self.app.delete("/product/delete/1000")
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot delete, product not found."})

        # check DB unchanged
        added_count = Product.query.count()
        self.assertEqual(added_count, initial_count)

    def test_delete_product_with_id(self):
        initial_count = Product.query.count()

        # send the request and check the response status code
        response = self.app.delete("/product/delete/1")
        self.assertEqual(response.status_code, 200)

        # check DB changed
        deleted_count = Product.query.count()
        self.assertEqual(deleted_count, initial_count-1)
