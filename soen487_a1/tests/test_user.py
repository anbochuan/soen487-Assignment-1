import unittest
import json
from main import app as tested_app
from main import db as tested_db
from config import TestConfig
from models import User

tested_app.config.from_object(TestConfig)


class TestUser(unittest.TestCase):
    def setUp(self):
        # set up the test DB
        self.db = tested_db
        self.db.create_all()
        self.db.session.add(User(id=1, user_name="Alice", password=123))
        self.db.session.add(User(id=2, user_name="Bob", password=456))
        self.db.session.commit()

        self.app = tested_app.test_client()

    def tearDown(self):
        # clean up the DB after the tests
        User.query.delete()
        self.db.session.commit()

    def test_get_all_user(self):
        # send the request and check the response status code
        response = self.app.get("/users")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        user_list = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(user_list), list)
        self.assertDictEqual(user_list[0], {"id": "1", "user_name": "Alice", "password": "123"})
        self.assertDictEqual(user_list[1], {"id": "2", "user_name": "Bob", "password": "456"})

    def test_get_user_with_valid_id(self):
        # send the request and check the response status code
        response = self.app.get("/user/1")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        user = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(user, {"id": "1", "user_name": "Alice", "password": "123"})

    def test_get_user_with_invalid_id(self):
        # send the request and check the response status code
        response = self.app.get("/user/1000000")
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot find this user id."})

    def test_create_user_without_param(self):
        initial_count = User.query.count()

        # send the request and check the response status code
        response = self.app.post("/user/create", data={"name": None, "password": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new user. Missing mandatory fields."})

        # check DB unchanged
        added_count = User.query.count()
        self.assertEqual(added_count, initial_count)

    def test_create_user_with_param(self):
        initial_count = User.query.count()

        # send the request and check the response status code
        response = self.app.post("/user/create", data={"id": 3, "name": "Amy", "password": "789"})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 200, "msg": "success"})

        # check if the DB was added correctly
        user = User.query.filter_by(id=3).first()
        self.assertEqual(user.user_name, "Amy")
        self.assertEqual(user.password, "789")
        # check if the DB was added correctly
        added_count = User.query.count()
        self.assertEqual(added_count, initial_count+1)

    def test_create_user_with_only_name(self):
        initial_count = User.query.count()

        # send the request and check the response status code
        response = self.app.post("/user/create", data={"id": 3, "name": "Amy", "password": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new user. Missing mandatory fields."})

        # check if the DB was unchanged
        added_count = User.query.count()
        self.assertEqual(added_count, initial_count)

    def test_create_user_with_only_password(self):
        initial_count = User.query.count()

        # send the request and check the response status code
        response = self.app.post("/user/create", data={"id": 3, "name": None, "password": "789"})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot create new user. Missing mandatory fields."})

        # check if the DB was unchanged
        added_count = User.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_user_with_bad_id(self):
        initial_count = User.query.count()

        # send the request and check the response status code
        response = self.app.put("/user/update/1000", data={"name": "kevin", "password": "123"})
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot update, user not found."})

        # check DB unchanged
        added_count = User.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_user_without_param(self):
        initial_count = User.query.count()

        # send the request and check the response status code
        response = self.app.put("/user/update/1", data={"name": None, "password": None})
        self.assertEqual(response.status_code, 403)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 403, "msg": "Cannot update user. Missing mandatory fields."})

        # check DB unchanged
        added_count = User.query.count()
        self.assertEqual(added_count, initial_count)

    def test_update_user_with_param(self):
        # send the request and check the response status code
        response = self.app.put("/user/update/1", data={"name": "Kevin", "password": "111"})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        updated_user = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(updated_user), dict)
        self.assertDictEqual(updated_user, {"code": 200, "data": {"id": "1", "user_name": "Kevin", "password": "111"}})

        # check DB changed result
        check_user = User.query.filter_by(id=1).first()
        self.assertEqual(check_user.user_name, "Kevin")
        self.assertEqual(check_user.password, "111")

    def test_update_user_with_only_name(self):
        # send the request and check the response status code
        response = self.app.put("/user/update/1", data={"name": "Kevin", "password": None})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        updated_user = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(updated_user), dict)
        self.assertDictEqual(updated_user, {"code": 200, "data": {"id": "1", "user_name": "Kevin", "password": "123"}})

        # check DB changed result
        check_user = User.query.filter_by(id=1).first()
        self.assertEqual(check_user.user_name, "Kevin")
        self.assertEqual(check_user.password, "123")

    def test_update_user_with_only_pwd(self):
        # send the request and check the response status code
        response = self.app.put("/user/update/1", data={"name": None, "password": "234"})
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        updated_user = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(updated_user), dict)
        self.assertDictEqual(updated_user, {"code": 200, "data": {"id": "1", "user_name": "Alice", "password": "234"}})

        # check DB changed result
        check_user = User.query.filter_by(id=1).first()
        self.assertEqual(check_user.user_name, "Alice")
        self.assertEqual(check_user.password, "234")

    def test_delete_user_with_bad_id(self):
        initial_count = User.query.count()

        # send the request and check the response status code
        response = self.app.delete("/user/delete/1000")
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot delete, user not found."})

        # check DB unchanged
        added_count = User.query.count()
        self.assertEqual(added_count, initial_count)

    def test_delete_user_with_id(self):
        initial_count = User.query.count()

        # send the request and check the response status code
        response = self.app.delete("/user/delete/1")
        self.assertEqual(response.status_code, 200)

        # check DB changed
        deleted_count = User.query.count()
        self.assertEqual(deleted_count, initial_count-1)
